import io
import logging
from PIL import ImageFont, Image, ImageDraw
import concurrent.futures as futures
import time

import grpc
import grpc_reflection.v1alpha.reflection as grpc_reflect

import visualization_pb2 as vis
import visualization_pb2_grpc as vis_grpc

_PORT = 8061
_SERVICE_NAME = 'VisualizationService'
_ONE_DAY_IN_SECONDS = 60 * 60 * 24


class VisualizationServiceImpl(vis_grpc.VisualizationServiceServicer):

    def __init__(self, current_image):
        self.__font = ImageFont.load_default()
        self.__current_img = current_image

    def Visualize(self, request: vis.VisualizationRequest, context):
        image_bytes = request.image.data
        img = Image.open(io.BytesIO(image_bytes)).resize((300, 300)).convert('RGB')

        # Add space for text
        new_img = Image.new(img.mode, (500, 300), (255, 255, 255))
        new_img.paste(img, (0, 0))

        # Add text to image
        text = "Num of Vehicles: {}".format(request.num_objs)
        editable_img = ImageDraw.Draw(new_img)
        editable_img.text((315, 15), text, (0, 0, 0), font=self.__font)

        # Saving img bytes in the shared buffer
        img_bytes = io.BytesIO()
        new_img.save(img_bytes, format='jpeg')
        img_bytes = img_bytes.getvalue()
        self.__current_img.bytes = img_bytes

        logging.info("Received img to visualize having num of vehicles: {}".format(request.num_objs))

        return vis.Empty()


def run_vis_server(shared_image):
    logging.basicConfig(level=logging.DEBUG)
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    vis_grpc.add_VisualizationServiceServicer_to_server(VisualizationServiceImpl(shared_image), server)
    service_names = (
        vis.DESCRIPTOR.services_by_name[_SERVICE_NAME].full_name,
        grpc_reflect.SERVICE_NAME
    )
    grpc_reflect.enable_server_reflection(service_names, server)
    server.add_insecure_port(f'[::]:{_PORT}')
    logging.info('Starting server at [::]:%d', _PORT)
    server.start()
    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        server.stop(0)

