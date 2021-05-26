import io
from PIL import Image, ImageDraw
import json
import numpy as np
import logging

import torchvision.transforms.functional as F


class PreprocessHandler:

    JSON_ROI_PATH = "./metadata/roi.json"

    def __init__(self, resize_factor=32, apply_roi=None):
        self.resize_factor = resize_factor
        self.roi_bmask = None
        if apply_roi:
            self.roi_bmask = self._load_roi_bmask()

    def preprocess_image(self, image_bytes):
        img = Image.open(io.BytesIO(image_bytes))
        img = img.convert('RGB')
        if self.roi_bmask is not None:
            img = self._apply_roi_bmask(img)
        orig_dim = img.size
        img = self.__pad_to_resize_factor(img, resize_factor=self.resize_factor)
        img = F.to_tensor(img).unsqueeze(dim=0)

        return img, orig_dim

    def __pad_to_resize_factor(self, img, resize_factor=32):
        img_width, img_height = img.size

        if img_width % resize_factor == 0 and img_height % resize_factor == 0:
            return img

        img_padded_width, img_padded_height = img_width, img_height
        if img_width % resize_factor != 0:
            img_padded_width = img_width + (resize_factor - (img_width % resize_factor))
        if img_height % resize_factor != 0:
            img_padded_height = img_height + (resize_factor - (img_height % resize_factor))

        pad_w = img_padded_width - img_width
        w_pad_left = pad_w // 2
        w_pad_right = pad_w - w_pad_left

        pad_h = img_padded_height - img_height
        h_pad_top = pad_h // 2
        h_pad_bottom = pad_h - h_pad_top

        img = F.pad(img, (w_pad_left, h_pad_top, w_pad_right, h_pad_bottom))

        return img

    def _load_roi_bmask(self):
        with open(self.JSON_ROI_PATH) as f:
            json_roi = json.load(f)

        h, w = json_roi['imageHeight'], json_roi['imageWidth']
        polygons_roi = []
        for roi_shape in json_roi['shapes']:
            polygon_roi = []
            for point_coords in roi_shape['points']:
                polygon_roi.append(int(point_coords[0]))
                polygon_roi.append(int(point_coords[1]))
            polygons_roi.append(polygon_roi)
        binary_mask = Image.new("L", (w, h), 1)
        b_mask_draw = ImageDraw.Draw(binary_mask)
        for pol in polygons_roi:
            b_mask_draw.polygon(pol, outline=1, fill=0)
        np_binary_mask = np.array(binary_mask).astype(np.uint8)

        return np_binary_mask

    def _apply_roi_bmask(self, img):
        img = np.array(img)
        h, w = img.shape[:2]
        bmask_h, bmask_w = self.roi_bmask.shape[:2]

        if h == bmask_h and w == bmask_w:
            return Image.fromarray(self.roi_bmask[:, :, None] * img)
        else:
            logging.error("Binary ROI Mask and input image have different sizes")


