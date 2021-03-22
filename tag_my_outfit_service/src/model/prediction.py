import tensorflow as tf
import keras

from keras import layers
from keras.models import Model
from keras.layers import Dense, Activation, Dropout, Conv2D, GlobalAveragePooling2D, Input, Lambda
import keras.backend as K
from keras.engine.topology import Layer


class CustomRegularization(Layer):
    def __init__(self, lam, **kwargs):
        self.lam = lam
        super(CustomRegularization, self).__init__(**kwargs)

    def call(self, x, mask=None):
        # x[0] is the learned feature map from regul_att_block, with size depending on the block
        # x[1] is the GT attention map (224,224)

        def euclidean_distance(vects):
            x, y = vects
            return K.sqrt(K.sum(K.sum(K.square(x - y),
                                      axis=1, keepdims=True), axis=2,
                                keepdims=False))

        dim1 = x[0].get_shape().as_list()
        att_mat_dim = dim1[1]
        pred_heat_map = x[0]

        # Assume features is of size [N, H, W, C] (batch_size, height, width, channels).
        # Transpose it to [N, C, H, W], then reshape to [N * C, H * W] to compute softmax
        # jointly over the image dimensions.
        pred_heat_map = tf.reshape(tf.transpose(pred_heat_map, [0, 3, 1, 2]), [-1, 56 * 56])
        pred_heat_map = tf.nn.softmax(pred_heat_map)  # apply 2D "spatial" softmax to predicted heatmap
        # Reshape and transpose back to original format.
        pred_heat_map = tf.transpose(tf.reshape(pred_heat_map, [-1, 1, 56, 56]), [0, 2, 3, 1])

        pred_heat_map_resh = tf.reshape(pred_heat_map, [-1, att_mat_dim,
                                                        att_mat_dim])  # to reshape the feature map to the same shape as the GT maps
        gt_heatmap_orig = x[1]

        if att_mat_dim == 56:
            heatmap_56 = tf.image.resize_images(gt_heatmap_orig, (56, 56), align_corners=True)
            gt_heatmap = heatmap_56

        gt_heatmap = tf.reshape(gt_heatmap, tf.shape(gt_heatmap)[:-1])
        pred_heat_map_resh_shape_tensor = tf.shape(pred_heat_map_resh)
       att_regul = euclidean_distance([gt_heatmap,
                                        pred_heat_map_resh])  # to measure the "pixelwise" euclidean distance between the predicted and Gt map

        loss2 = self.lam * K.sum(att_regul)
        self.add_loss(loss2, x)

        return pred_heat_map

    def compute_output_shape(self, input_shape):
        return [input_shape[0], input_shape[1]]


class PredictionHandler:

    # Graph to be used by all threads
    __graph = tf.get_default_graph()

    def __init__(self, model_weights_path, n_categories, n_attributes):
        # One unique session for each thread
        self.__session = tf.Session(graph=PredictionHandler.__graph)

        # model parameters
        att_regul_weight = 10
        conv_kernel_size = 3
        scale_param = 20

        img_input = Input(shape=(224, 224, 3), name='input1')
        att_prior_input = Input(shape=(224, 224, 1), name='input2')

        # Block 1
        x = layers.Conv2D(64, (conv_kernel_size, conv_kernel_size),
                          activation='relu',
                          padding='same',
                          name='block1_conv1')(img_input)
        x = layers.Conv2D(64, (conv_kernel_size, conv_kernel_size),
                          activation='relu',
                          padding='same',
                          name='block1_conv2')(x)
        x = layers.MaxPooling2D((2, 2), strides=(2, 2), name='block1_pool')(x)

        # Block 2
        x = layers.Conv2D(128, (conv_kernel_size, conv_kernel_size),
                          activation='relu',
                          padding='same',
                          name='block2_conv1')(x)
        x = layers.Conv2D(128, (conv_kernel_size, conv_kernel_size),
                          activation='relu',
                          padding='same',
                          name='block2_conv2')(x)
        out_block2 = layers.MaxPooling2D((2, 2), strides=(2, 2), name='block2_pool')(x)

        # Block 3
        x = layers.Conv2D(256, (conv_kernel_size, conv_kernel_size),
                          activation='relu',
                          padding='same',
                          name='block3_conv1')(out_block2)
        x = layers.Conv2D(256, (conv_kernel_size, conv_kernel_size),
                          activation='relu',
                          padding='same',
                          name='block3_conv2')(x)
        x = layers.Conv2D(256, (conv_kernel_size, conv_kernel_size),
                          activation='relu',
                          padding='same',
                          name='block3_conv3')(x)
        out_block3 = layers.MaxPooling2D((2, 2), strides=(2, 2), name='block3_pool')(x)

        # Block 4
        x = layers.Conv2D(512, (conv_kernel_size, conv_kernel_size),
                          activation='relu',
                          padding='same',
                          name='block4_conv1')(out_block3)  # changed here
        x = layers.Conv2D(512, (conv_kernel_size, conv_kernel_size),
                          activation='relu',
                          padding='same',
                          name='block4_conv2')(x)
        x = layers.Conv2D(512, (conv_kernel_size, conv_kernel_size),
                          activation='relu',
                          padding='same',
                          name='block4_conv3')(x)
        out_block4 = layers.MaxPooling2D((2, 2), strides=(2, 2), name='block4_pool')(x)

        out_block3_56 = Lambda(lambda image: tf.image.resize_images(image, (56, 56), align_corners=True),
                               name='resize_out_block_3')(out_block3)
        out_block4_56 = Lambda(lambda image: tf.image.resize_images(image, (56, 56), align_corners=True),
                               name='resize_out_block_4')(out_block4)

        x_combined = layers.Concatenate(axis=3)([out_block2, out_block3_56, out_block4_56])
        x_combined = layers.Conv2D(512, (1, 1), activation='relu', padding='same', name='conv_1x1x512')(x_combined)

        num_channels = 512
        # compute mean using tf.nn.avg_pool
        x_combined_t = Lambda(lambda tensor: tf.transpose(tensor, [0, 1, 3, 2]), name='transpose_x')(x_combined)
        avg_pool_spatial_att = Lambda(
            lambda layer: tf.nn.avg_pool(layer, ksize=[1, 1, num_channels, 1], strides=[1, 1, num_channels, 1],
                                         padding='SAME'), name='channel_avg_pool')(x_combined_t)
        max_pool_spatial_att = Lambda(
            lambda layer: tf.nn.max_pool(layer, ksize=[1, 1, num_channels, 1], strides=[1, 1, num_channels, 1],
                                         padding='SAME'), name='channel_max_pool')(x_combined_t)

        # transpose back to original form
        avg_pool_spatial_att = Lambda(lambda tensor: tf.transpose(tensor, [0, 1, 3, 2]), name='transpose_avg_pool')(
            avg_pool_spatial_att)
        max_pool_spatial_att = Lambda(lambda tensor: tf.transpose(tensor, [0, 1, 3, 2]), name='transpose_max_pool')(
            max_pool_spatial_att)

        concat_att_out = layers.Concatenate(axis=3)([avg_pool_spatial_att, max_pool_spatial_att])

        cr_combined = layers.Conv2D(1, (7, 7), activation='sigmoid', padding='same', name='conv_7x7x1')(concat_att_out)

        cr_combined_realim = layers.Multiply()([x_combined, cr_combined])

        cr_combined_realim = layers.AveragePooling2D((2, 2), strides=(4, 4), name='cr_combined_realim_pool')(
            cr_combined_realim)

        cr_combined_out = CustomRegularization(att_regul_weight)([cr_combined, att_prior_input])

        cr_combined_realim_scaled = Lambda(lambda input_tensor: input_tensor * scale_param, name='scaling_att')(
            cr_combined_realim)

        x4_added = keras.layers.Add()([out_block4, cr_combined_realim_scaled])

        # Block 5
        x = layers.Conv2D(512, (3, 3),
                          activation='relu',
                          padding='same',
                          name='block5_conv1')(x4_added)
        x = layers.Conv2D(512, (3, 3),
                          activation='relu',
                          padding='same',
                          name='block5_conv2')(x)
        x = layers.Conv2D(512, (3, 3),
                          activation='relu',
                          padding='same',
                          name='block5_conv3')(x)
        x = layers.MaxPooling2D((2, 2), strides=(2, 2), name='block5_pool')(x)

        kernel_init = keras.initializers.RandomNormal(mean=0.0, stddev=0.01, seed=None)
        x_out1 = Conv2D(1024, kernel_size=(3, 3), strides=1, padding='same', activation='relu',
                        kernel_initializer=kernel_init)(x)
        x_out1 = GlobalAveragePooling2D(name='glbal_average_pooling_2D_cat')(x_out1)
        x_out1 = Dropout(0.5)(x_out1)

        out_1 = Dense(n_categories, name='out_1_dense')(x_out1)
        out_1 = Activation('softmax', name='Category_deep_2')(out_1)

        kernel_init = keras.initializers.RandomNormal(mean=0.0, stddev=0.01, seed=None)
        x_out2 = Conv2D(1024, kernel_size=(3, 3), strides=1, padding='same', activation='relu',
                        kernel_initializer=kernel_init)(x)
        x_out2 = GlobalAveragePooling2D(name='glbal_average_pooling_2D_att')(x_out2)
        x_out2 = Dropout(0.5)(x_out2)

        out_3 = Dense(n_attributes, name='out_3_dense')(x_out2)
        out_3 = Activation('sigmoid', name='Attribute_deep')(out_3)

        # Use common graph for all threads
        with PredictionHandler.__graph.as_default():
            # Use each thread's unique session
            with self.__session.as_default():
                self.__learning_framework = Model(inputs=[img_input, att_prior_input], outputs=[out_1, out_3, cr_combined_out])
                self.__learning_framework.load_weights(model_weights_path)

    def predict(self, received_input):
        # Use common graph for all threads
        with PredictionHandler.__graph.as_default():
            # Use each thread's unique session
            with self.__session.as_default():
                return self.__learning_framework.predict_on_batch(received_input)

    def __del__(self):
        self.__session.close()
