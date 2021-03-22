from tag_my_outfit_pb2 import PredictRequest, PredictResponse, StreamPredictResponse, Prediction, Correspondence
from tag_my_outfit_pb2_grpc import TagMyOutfitServiceServicer
from annotations.profiling import profile
from model.service import TagMyOutfitService


class GrpcTagMyOutfitServiceImpl(TagMyOutfitServiceServicer):

    def __init__(self, service: TagMyOutfitService):
        self.__service = service

    @profile
    def predict(self, request: PredictRequest, context):
        categories_results, attributes_results = self.__process_single_predict(request)
        return PredictResponse(categories=categories_results,
                               attributes=attributes_results)

    @profile
    def stream_predict(self, request_iterator, context):
        predictions = map(self.__process_single_request, request_iterator)
        return StreamPredictResponse(predictions=predictions)

    def __process_single_request(self, request):
        categories_results, attributes_results = self.__process_single_predict(request)
        return Prediction(categories=categories_results, attributes=attributes_results)

    def __process_single_predict(self, request):
        image_bytes = request.image_data
        all_categories = request.all_categories
        all_attributes = request.all_attributes
        categories_results, attributes_results = self.__service.predict(image_bytes, all_categories, all_attributes)
        categories_results = map(lambda x: Correspondence(label=x[0], value=x[1]), categories_results)
        attributes_results = map(lambda x: Correspondence(label=x[0], value=x[1]), attributes_results)
        return categories_results, attributes_results
