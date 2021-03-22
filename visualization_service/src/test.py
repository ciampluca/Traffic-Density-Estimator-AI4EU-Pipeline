import argparse
import grpc
import time
import pathlib
from random import randrange

import visualization_pb2 as vis
import visualization_pb2_grpc as vis_grpc


def parse_args():
    parser = argparse.ArgumentParser(
        description='Test for Visualization Service')
    parser.add_argument(
        '--target',
        default='localhost:8061',
        help='Location where the server to test is listening')
    parser.add_argument(
        'images_dir',
        nargs='?',
        default='images',
        help='directory of the images to send and visualize (defaults to images)'
    )
    parser.add_argument(
        '--delay',
        type=int,
        default=1,
        help='Delay between images in seconds')

    return parser.parse_args()


def images_paths_generator(images_dir):
    return filter(
        lambda x: x.is_file() and x.suffix in {'.jpg', '.png', '.jpeg'},
        images_dir.iterdir())


def send_image(stub, img_path):
    with open(img_path, 'rb') as fp:
        image_bytes = fp.read()

    fake_num_objs = randrange(100)

    img_to_send = vis.Image(
        data=image_bytes
    )

    req = vis.VisualizationRequest(
        image=img_to_send,
        num_objs=fake_num_objs
    )

    stub.Visualize(request=req)


def send_images(channel, images_dir, delay):
    stub = vis_grpc.VisualizationServiceStub(channel=channel)

    path = pathlib.Path(images_dir)
    for img_path in images_paths_generator(path):
        send_image(stub, img_path)
        time.sleep(delay)


def main():
    args = parse_args()
    target = args.target
    images_dir = args.images_dir
    delay = args.delay
    with grpc.insecure_channel(target) as channel:
        send_images(channel, images_dir, delay)


if __name__ == '__main__':
    main()
