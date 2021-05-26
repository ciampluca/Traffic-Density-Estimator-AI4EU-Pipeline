import logging
import pathlib
import time
import requests
from requests.auth import HTTPBasicAuth

import source_pb2 as source
import source_pb2_grpc as source_grpc


_DELAY = 2


class ImageSourceServiceImpl(source_grpc.ImageSourceServiceServicer):

    def __init__(self, img_source):
        self.__image_dir = None
        self.__url = None
        if img_source.startswith("http"):
            self.__url = img_source
        else:
            self.__image_dir = img_source
            self.__directory_iter = self.__get_directory_images_iter()

    def Get(self, request, context):
        response = None

        if self.__image_dir is not None:
            image_path = None
            while True:
                # directory_iter = self.__get_directory_images_iter()
                while not image_path:
                    try:
                        image_path = next(self.__directory_iter, None)
                        logging.info("Getting image: {}".format(image_path))
                    except StopIteration:
                        logging.error(
                            "Directory '%s' has no images",
                            self.__image_dir)
                        break
                if image_path:
                    break
            time.sleep(_DELAY)

            response = self.__get_response_from_path(image_path)

        elif self.__url is not None:
            response = self.__get_response_from_url(self.__url, with_auth=True)

        return response

    def __get_directory_images_iter(self):
        directory_iter = filter(
            lambda x: x.is_file() and x.suffix in {'.jpg', '.png', '.jpeg'},
            self.__image_dir.iterdir())

        return directory_iter

    @staticmethod
    def __get_response_from_path(image_path):
        with open(image_path, 'rb') as fp:
            image_bytes = fp.read()
        response = source.PredictRequest(image_data=image_bytes)

        return response

    @staticmethod
    def __get_response_from_url(url, with_auth=None):
        if with_auth:
            req = requests.get(url, verify=False, auth=HTTPBasicAuth('admin', 'admin'))
        else:
            req = requests.get(url)

        image_bytes = req.content
        response = source.PredictRequest(image_data=image_bytes)

        return response
