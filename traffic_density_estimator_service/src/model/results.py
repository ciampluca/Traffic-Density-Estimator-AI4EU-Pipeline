from PIL import Image
import io

import torch
import torchvision.transforms.functional as F


class ResultsHandler:

    def __init__(self, img_output_dim=(640, 640)):
        super(ResultsHandler, self).__init__()
        self.img_output_dim = img_output_dim

    def build_results(self, original_img_dim, prediction):
        den_map = prediction.squeeze()

        # Computing estimated number of vehicles present in the scene
        num_objs = torch.sum(den_map)
        num_objs = int(num_objs.cpu().item())

        # Normalizing density map
        den_map = den_map.cpu().numpy()
        minval = den_map.min()
        maxval = den_map.max()
        if minval != maxval:
            den_map -= minval
            den_map *= (255.0 / (maxval - minval))
        den_map = den_map.astype('uint8')

        # Converting to RGB, eventually removing added pad, resizing to output dim
        den_map = Image.fromarray(den_map).convert('RGB')
        den_map = self.__remove_pad(den_map, original_img_dim)
        den_map = den_map.resize((self.img_output_dim[0], self.img_output_dim[0]))

        # Converting to bytes
        den_map_bytes = io.BytesIO()
        den_map.save(den_map_bytes, format='jpeg')
        den_map_bytes = den_map_bytes.getvalue()

        return den_map_bytes, num_objs

    def __remove_pad(self, img, output_dim):
        img_width, img_height = img.size

        if img_width == output_dim[0] and img_height == output_dim[1]:
            return img

        pad_w = img_width - output_dim[0]
        w_pad_left = pad_w // 2

        pad_h = img_height - output_dim[1]
        h_pad_top = pad_h // 2

        img = F.crop(img, h_pad_top, w_pad_left, output_dim[1], output_dim[0])

        return img
