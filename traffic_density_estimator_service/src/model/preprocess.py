import io
from PIL import Image

import torchvision.transforms.functional as F


class PreprocessHandler:

    def __init__(self, img_output_dim=(640, 640), resize_factor=32):
        self.img_output_dim = img_output_dim
        self.resize_factor = resize_factor

    def preprocess_image(self, image_bytes):
        img = Image.open(io.BytesIO(image_bytes))
        img = img.convert('RGB')
        orig_dim = img.size
        img = img.resize(self.img_output_dim, Image.NEAREST)
        img = self.__pad_to_resize_factor(img, resize_factor=self.resize_factor)
        img = F.to_tensor(img).unsqueeze(dim=0)

        return img, orig_dim

    def __pad_to_resize_factor(self, img, resize_factor=32):
        img_width, img_height = img.size

        if img_width % resize_factor == 0 and img_height % resize_factor == 0:
            return img

        img_padded_width = img_width + (resize_factor - (img_width % resize_factor))
        img_padded_height = img_height + (resize_factor - (img_height % resize_factor))

        pad_w = img_padded_width - img_width
        w_pad_left = pad_w // 2
        w_pad_right = pad_w - w_pad_left

        pad_h = img_padded_height - img_height
        h_pad_top = pad_h // 2
        h_pad_bottom = pad_h - h_pad_top

        img = F.pad(img, (w_pad_left, h_pad_top, w_pad_right, h_pad_bottom))

        return img
