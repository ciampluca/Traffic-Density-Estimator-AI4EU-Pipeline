import logging
import os
import argparse
import concurrent.futures as futures
import pathlib

import grpc
import grpc_reflection.v1alpha.reflection as grpc_reflect

import source_pb2 as source
import source_pb2_grpc as source_grpc
import image_source_service_impl


_IMAGES_ENV_VAR = 'IMAGE_DIR'
_PORT_ENV_VAR = 'PORT'
_SERVICE_NAME = 'ImageSourceService'


def parse_argv():
    main_parser = argparse.ArgumentParser()
    main_parser.add_argument(
        'image_dir',
        nargs='?',
        default='imgs',
        help='source directory of the images to send (defaults to images)'
    )
    main_parser.add_argument(
        '--port',
        type=int,
        default=8061,
        help='Port where the server should listen (defaults to 8061)'
    )

    return main_parser.parse_args()


def run_pull_mode(image_dir, port):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    source_grpc.add_ImageSourceServiceServicer_to_server(
        image_source_service_impl.ImageSourceServiceImpl(pathlib.Path(image_dir)),
        server)
    SERVICE_NAME = (
        source.DESCRIPTOR.services_by_name[_SERVICE_NAME].full_name,
        grpc_reflect.SERVICE_NAME
    )
    grpc_reflect.enable_server_reflection(SERVICE_NAME, server)
    server.add_insecure_port(f'[::]:{port}')
    logging.info('Starting server at [::]:%d', port)
    server.start()
    server.wait_for_termination()


def main():
    args = parse_argv()
    image_dir = args.image_dir
    image_dir = os.getenv(_IMAGES_ENV_VAR, image_dir)
    port = args.port
    port = os.getenv(_PORT_ENV_VAR, port)
    logging.info('Recovering images from %s', image_dir)
    run_pull_mode(image_dir, port)


if __name__ == '__main__':
    logging.basicConfig(
        format='[ %(levelname)s ] %(asctime)s (%(module)s) %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        level=logging.INFO)

    main()
