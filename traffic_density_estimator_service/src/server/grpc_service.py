from traffic_density_estimator_pb2_grpc import TrafficDensityEstimatorServiceServicer
from traffic_density_estimator_pb2 import PredictRequest, PredictResponse

from model.service import TrafficDensityEstimatorService


class GrpcTrafficDensityEstimatorServiceImpl(TrafficDensityEstimatorServiceServicer):

    def __init__(self, service: TrafficDensityEstimatorService):
        self.__service = service

    def predict(self, request: PredictRequest, context):
        dmap, num_objs = self.__process_single_predict(request)

        return PredictResponse(image_data=dmap,
                               num_objs=num_objs)

    def __process_single_predict(self, request):
        image_bytes = request.image_data
        dmap, num_objs = self.__service.predict(image_bytes)

        return dmap, num_objs

