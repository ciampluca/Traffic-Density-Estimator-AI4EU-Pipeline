from traffic_density_estimator_pb2_grpc import DensityTrafficEstimatorServiceServicer
from traffic_density_estimator_pb2 import PredictRequest, PredictResponse

from annotations.profiling import profile


class GrpcTrafficDensityEstimatorServiceImpl(DensityTrafficEstimatorServiceServicer):

    def __init__(self, service: TrafficEstimatorService):
        self.__service = service

    @profile
    def predict(self, request: PredictRequest, context):
        dmap, num_objs = self.__process_single_predict(request)
        return PredictResponse(categories=categories_results,
                               attributes=attributes_results)