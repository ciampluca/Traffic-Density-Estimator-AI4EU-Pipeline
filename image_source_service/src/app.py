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
        'source',
        nargs='?',
        # default='imgs',
        default='http://printart.isr.ist.utl.pt:9011/?action=snapshot',
        help='source directory or url of the images to send (defaults to imgs)'
    )
    main_parser.add_argument(
        '--port',
        type=int,
        default=8061,
        help='Port where the server should listen (defaults to 8061)'
    )

    return main_parser.parse_args()


def run_pull_mode(img_source, port):
    if not img_source.startswith("http"):
        img_source = pathlib.Path(img_source)
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    source_grpc.add_ImageSourceServiceServicer_to_server(
        image_source_service_impl.ImageSourceServiceImpl(img_source),
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
    img_source = args.source
    # image_dir = os.getenv(_IMAGES_ENV_VAR, image_dir)
    port = args.port
    port = os.getenv(_PORT_ENV_VAR, port)
    logging.info('Recovering images from %s', img_source)
    run_pull_mode(img_source, port)


if __name__ == '__main__':
    logging.basicConfig(
        format='[ %(levelname)s ] %(asctime)s (%(module)s) %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        level=logging.INFO)

    main()
