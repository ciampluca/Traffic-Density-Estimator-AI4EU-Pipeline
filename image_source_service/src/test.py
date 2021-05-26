import argparse
import time
from PIL import Image
import io

import grpc

import source_pb2 as source
import source_pb2_grpc as source_grpc


def parse_args():
    parser = argparse.ArgumentParser(
        description='Test for Image Source Service')
    parser.add_argument(
        '--target',
        default='localhost:8061',
        help='Location where the server to test is listening')
    parser.add_argument(
        '--delay',
        type=int,
        default=1,
        help='Delay between images in seconds')
    parser.add_argument(
        '--num_gets',
        type=int,
        default=50,
        help='Number of gets to be done to the server')

    return parser.parse_args()


def get_images(channel, delay, num_gets):
    stub = source_grpc.ImageSourceServiceStub(channel=channel)

    for i in range(num_gets):
        req = source.Empty()
        image_data = stub.Get(request=req)
        image_bytes = image_data.image_data

        time.sleep(delay)

        image = Image.open(io.BytesIO(image_bytes))

        image.show()


def main():
    args = parse_args()
    target = args.target
    delay = args.delay
    num_gets = args.num_gets
    with grpc.insecure_channel(target) as channel:
        get_images(channel, delay, num_gets)


if __name__ == '__main__':
    main()

