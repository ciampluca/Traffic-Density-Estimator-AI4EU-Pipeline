import numpy as np
from model.encoder import Encoder


class ResultsHandler:

    __MULTI_LABEL_THRESHOLD = 0.5

    def __init__(self,
                 categories_encoder: Encoder,
                 num_categories: int,
                 attributes_encoder: Encoder,
                 num_attributes: int):
        self.__categories_encoder = categories_encoder
        self.__attributes_encoder = attributes_encoder
        # Get categories labels
        np_diagonal = np.zeros(shape=(num_categories, num_categories))
        np.fill_diagonal(np_diagonal, 1)
        self.__categories_labels = [x[0] for x in self.__categories_encoder.decode(np_diagonal)]
        # Get attributes labels
        np_diagonal = np.zeros(shape=(num_attributes, num_attributes))
        np.fill_diagonal(np_diagonal, 1)
        self.__attributes_labels = [x[0] for x in self.__attributes_encoder.decode(np_diagonal)]

    def build_results(self, prediction, all_categories=False, all_attributes=False):
        """
        Args:
            prediction: prediction from the model
            all_categories: true if all categories results should be included and false if only the selected one
            all_attributes: true if all attributes results should be included and false if only the selected ones
        Returns:
            categories_results: iterable with the categories results
            attributes_results: iterable with the attributes results
        """
        predicted_categories, predicted_attributes, _ = prediction
        # Categories results
        # Reshape array for single dimension
        predicted_categories = np.reshape(predicted_categories, (predicted_categories.shape[1],))
        assert (len(self.__categories_labels) == len(predicted_categories))
        if all_categories:
            categories_results = zip(self.__categories_labels, predicted_categories)
        else:
            max_pred_idx = np.argmax(predicted_categories)
            # If only the predicted category return tuple with single element
            categories_results = ((self.__categories_labels[max_pred_idx],
                                   predicted_categories[max_pred_idx]),)
        # Attributes results
        # Reshape array for single dimension
        predicted_attributes = np.reshape(predicted_attributes, (predicted_attributes.shape[1],))
        attributes_results = zip(self.__attributes_labels, predicted_attributes)
        if not all_attributes:
            attributes_results = filter(lambda x: x[1] > ResultsHandler.__MULTI_LABEL_THRESHOLD, attributes_results)
        return categories_results, attributes_results
