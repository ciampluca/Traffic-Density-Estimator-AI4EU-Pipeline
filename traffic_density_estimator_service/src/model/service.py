import logging

from model.preprocess import PreprocessHandler
from model.prediction import PredictionHandler
from model.results import ResultsHandler


class TrafficDensityEstimatorService:

    def __init__(self,
                 preprocess_handler: PreprocessHandler,
                 prediction_handler: PredictionHandler,
                 results_handler: ResultsHandler):
        self.__preprocess_handler = preprocess_handler
        self.__prediction_handler = prediction_handler
        self.__results_handler = results_handler
        self.__imgs_counter = 0

    def predict(self, image_bytes):
        logging.info(f"Received img number: {self.__imgs_counter}")
        preprocessed_image, original_dim = self.__preprocess_handler.preprocess_image(image_bytes)
        prediction = self.__prediction_handler.predict(preprocessed_image)
        results = self.__results_handler.build_results(prediction)
        logging.info(f"End processing of img number: {self.__imgs_counter}")
        self.__imgs_counter += 1

        return results
