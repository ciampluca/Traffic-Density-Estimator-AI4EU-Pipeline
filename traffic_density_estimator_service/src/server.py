import concurrent.futures as futures
import os
import logging
import time

import grpc
from grpc_reflection.v1alpha import reflection

from server.context import Context

from model.preprocess import PreprocessHandler
from model.prediction import PredictionHandler
from model.results import ResultsHandler
from model.service import TrafficDensityEstimatorService

from traffic_density_estimator_pb2 import DESCRIPTOR
from traffic_density_estimator_pb2_grpc import add_TrafficDensityEstimatorServiceServicer_to_server

from server.grpc_service import GrpcTrafficDensityEstimatorServiceImpl


_ONE_DAY_IN_SECONDS = 60 * 60 * 24
_SERVICE_NAME = 'TrafficDensityEstimatorService'
_IMG_OUTPUT_DIM = (640, 640)

# By default listen on all interfaces on port 8061
_DEFAULT_HOST = '[::]'
_DEFAULT_PORT = 8061


def start_server():
    # Get configs
    server_context = Context()
    model_dir = server_context.model_dir
    model_weights_path = os.path.join(model_dir, server_context.weights)
    img_output_dim = (server_context.img_output_dim[0], server_context.img_output_dim[1]) if hasattr(server_context, 'img_output_dim') else _IMG_OUTPUT_DIM

    # Init handlers
    preprocess_handler: PreprocessHandler = PreprocessHandler(img_output_dim)
    prediction_handler: PredictionHandler = PredictionHandler(model_weights_path)
    results_handler: ResultsHandler = ResultsHandler(img_output_dim)

    service = TrafficDensityEstimatorService(preprocess_handler, prediction_handler, results_handler)
    service_impl = GrpcTrafficDensityEstimatorServiceImpl(service)

    # Init server
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=100))
    add_TrafficDensityEstimatorServiceServicer_to_server(service_impl, server)
    # Enable server reflection
    SERVICE_NAMES = (
        DESCRIPTOR.services_by_name[_SERVICE_NAME].full_name,
        reflection.SERVICE_NAME,
    )
    reflection.enable_server_reflection(SERVICE_NAMES, server)

    # Find host and port and start server
    host = server_context.host if hasattr(server_context, 'host') else _DEFAULT_HOST
    port = server_context.port if hasattr(server_context, 'port') else _DEFAULT_PORT
    server.add_insecure_port(f'{host}:{port}')
    server.start()
    logging.info(f'Server running at {host}:{port}')

    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        logging.info('Server stopped by keyboard interruption')
        server.stop(0)


if __name__ == '__main__':
    start_server()
