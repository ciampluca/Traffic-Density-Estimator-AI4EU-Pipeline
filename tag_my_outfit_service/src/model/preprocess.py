import io
import numpy as np
from PIL import Image
from keras.preprocessing import image
from keras.applications import vgg16
from typing import Iterable


class PreprocessHandler:

    def __init__(self, target_size=(224, 224)):
        self.target_size = target_size
        heatmap = np.random.randn(224, 224)
        heatmap = np.expand_dims(heatmap, axis=0)
        self.heatmap = np.expand_dims(heatmap, axis=3)

    def __preprocess_image(self, image_bytes):
        img = Image.open(io.BytesIO(image_bytes))
        img = img.convert('RGB')
        img = img.resize(self.target_size, Image.NEAREST)
        img = image.img_to_array(img)
        img = np.expand_dims(img, axis=0)
        img = vgg16.preprocess_input(img)
        return [img, self.heatmap]

    def preprocess_image(self, image_bytes):
        """
        Transforms the given image bytes in the
        format to be processed.
        Does the same as tf.keras.preprocessing.image.load_img
        before transforming the image to array
        Args:
            image_bytes: string with bytes of the image to transform
        Returns: a tuple with the preprocessed numpy array and heatmap
        """
        return self.__preprocess_image(image_bytes)

    def preprocess_image_batch(self, image_bytes_batch: Iterable[bytes]):
        """
        Transforms each given image bytes in the
        format to be processed.
        Does the same as tf.keras.preprocessing.image.load_img
        before transforming the image to array
        Args:
            image_bytes_batch: nd.array with strings of bytes of the images to transform
        Returns: iterable with list of preprocessed numpy arrays and heat maps
        """
        return map(self.__preprocess_image, image_bytes_batch)
