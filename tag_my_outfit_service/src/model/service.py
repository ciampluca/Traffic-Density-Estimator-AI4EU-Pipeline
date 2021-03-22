from model.preprocess import PreprocessHandler
from model.prediction import PredictionHandler
from model.results import ResultsHandler


class TagMyOutfitService:

    def __init__(self,
                 preprocess_handler: PreprocessHandler,
                 prediction_handler: PredictionHandler,
                 results_handler: ResultsHandler):
        self.__preprocess_handler = preprocess_handler
        self.__prediction_handler = prediction_handler
        self.__results_handler = results_handler

    def predict(self, image_bytes, all_categories, all_attributes):
        preprocessed_image = self.__preprocess_handler.preprocess_image(image_bytes)
        prediction = self.__prediction_handler.predict(preprocessed_image)
        return self.__results_handler.build_results(prediction, all_categories, all_attributes)
