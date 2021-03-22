import concurrent.futures as futures
import grpc
import logging
import pickle as pkl
import time

from grpc_reflection.v1alpha import reflection
from tag_my_outfit_pb2 import DESCRIPTOR
from tag_my_outfit_pb2_grpc import add_TagMyOutfitServiceServicer_to_server

from model.service import TagMyOutfitService
from model.preprocess import PreprocessHandler
from model.prediction import PredictionHandler
from model.results import ResultsHandler
from model.encoder import Encoder
from server.context import Context
from server.grpc_service import GrpcTagMyOutfitServiceImpl

_ONE_DAY_IN_SECONDS = 60 * 60 * 24
_SERVICE_NAME = 'TagMyOutfitService'

# By default listen on all interfaces on port 8061
_DEFAULT_HOST = '[::]'
_DEFAULT_PORT = 8061


def load_encoder(file):
    with open(file, 'rb') as fp:
        params = pkl.load(fp)
    encoder = Encoder(*params)
    n_classes = len(encoder.encoder.classes_)
    return encoder, n_classes


def start_server():
    # Get configs
    server_context = Context()
    model_dir = server_context.model_dir
    model_weights_path = model_dir + '/' + server_context.weights
    categories_path = model_dir + '/' + server_context.ohe_categories
    attributes_path = model_dir + '/' + server_context.ohe_attributes

    # Load encoders
    categories_encoder, n_categories = load_encoder(categories_path)
    attributes_encoder, n_attributes = load_encoder(attributes_path)

    # Init handlers
    preprocess_handler: PreprocessHandler = PreprocessHandler()
    prediction_handler: PredictionHandler = PredictionHandler(model_weights_path, n_categories, n_attributes)
    results_handler: ResultsHandler = ResultsHandler(categories_encoder, n_categories, attributes_encoder, n_attributes)

    service = TagMyOutfitService(preprocess_handler, prediction_handler, results_handler)
    service_impl = GrpcTagMyOutfitServiceImpl(service)

    # Init server
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=100))
    add_TagMyOutfitServiceServicer_to_server(service_impl, server)
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
