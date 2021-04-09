import argparse
import grpc
import time
import pathlib

import traffic_density_estimator_pb2_grpc as den_grpc
import traffic_density_estimator_pb2 as den


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
        default='imgs',
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

    req = den.PredictRequest(
        image_data=image_bytes
    )

    stub.predict(request=req)


def send_images(channel, images_dir, delay):
    stub = den_grpc.TrafficDensityEstimatorServiceStub(channel=channel)

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
