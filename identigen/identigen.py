#!/usr/bin/env python3
import hashlib as hl
import numpy as np
import cv2 as cv
import random
import argparse
from pathlib import Path


class IdenticonGenerator:

    def __init__(self):
        self.__horizontal_symmetry = 1
        self.__vertical_symmetry = 2
        self.__quarter_symmetry = 3

    def generate(self, string, symmetry=1, img_width=16, color_count=3,
                 hsv_percent_min=(0.0, 0.2, 0.2), hsv_percent_max=(1.0, 0.8, 0.8)):
        assert (img_width % 16 == 0), \
            "Parameter img_width must be a factor of 16. Given parameter was {}.".format(img_width)
        assert (symmetry in [self.__horizontal_symmetry, self.__vertical_symmetry, self.__quarter_symmetry]), \
            "Parameter symmetry must be equal to IdenticonGenerator.horizontal_symmetry, " \
            "IdenticonGenerator.vertical_symmetry, or IdenticonGenerator.quarter_symmetry."

        bytestring = string.encode()  # defaults to utf-8
        hashed = hl.sha512(bytestring)
        hex_digest = hashed.hexdigest()
        decimal_digest = int(hex_digest, 16)
        # use the hash of the string parameter to generate pseudorandom numbers
        random.seed(decimal_digest)

        # color values are in HSV format,
        # and limited to the range specified by the hsv_percent_min and hsv_percent_max parameters
        h_range = (int(hsv_percent_min[0] * 179), int(hsv_percent_max[0] * 179))
        s_range = (int(hsv_percent_min[1] * 255), int(hsv_percent_max[1] * 255))
        v_range = (int(hsv_percent_min[2] * 255), int(hsv_percent_max[2] * 255))

        colors = []
        for color_index in range(0, color_count):
            h = random.randint(h_range[0], h_range[1])
            s = random.randint(s_range[0], s_range[1])
            v = random.randint(v_range[0], v_range[1])
            hsv = [h, s, v]
            colors.append(hsv)

        if symmetry == self.__horizontal_symmetry:
            hsvimg = IdenticonGenerator.__create_horizontal_symmetric_img(img_width, colors)
        elif symmetry == self.__vertical_symmetry:
            hsvimg = IdenticonGenerator.__create_vertical_symmetric_img(img_width, colors)
        else:  # symmetry == self.__quarter_symmetry:
            hsvimg = IdenticonGenerator.__create_quarter_symmetric_img(img_width, colors)

        rgbimg = cv.cvtColor(hsvimg, cv.COLOR_HSV2RGB_FULL)
        return rgbimg

    @staticmethod
    def __scale_img_to_multiple(img, scaled_width):
        if img.shape[0] != scaled_width:
            scaled_img = np.zeros((scaled_width, scaled_width, img.shape[2]), np.uint8)
            multiple_factor = int(scaled_width / img.shape[0])

            for src_row in range(0, img.shape[0]):
                for src_col in range(0, img.shape[1]):
                    src_color = img[src_row, src_col]
                    for scaled_row in range(src_row * multiple_factor, src_row * multiple_factor + multiple_factor):
                        for scaled_col in range(src_col * multiple_factor, src_col * multiple_factor + multiple_factor):
                            scaled_img[scaled_row, scaled_col] = src_color
        else:
            scaled_img = img

        return scaled_img

    @staticmethod
    def __create_horizontal_symmetric_img(width, colors):
        channels = 3
        base_width = 16
        base_shape = (base_width, base_width, channels)
        base_img = np.zeros(base_shape, np.uint8)

        for row in range(0, base_width):
            for col in range(0, int(base_width / 2)):
                chosen_color = colors[random.randint(0, len(colors) - 1)]
                base_img[row, col] = chosen_color
                base_img[row, base_width - col - 1] = chosen_color

        scaled_img = IdenticonGenerator.__scale_img_to_multiple(base_img, width)

        return scaled_img

    @staticmethod
    def __create_vertical_symmetric_img(width, colors):
        channels = 3
        base_width = 16
        base_shape = (base_width, base_width, channels)
        base_img = np.zeros(base_shape, np.uint8)

        for row in range(0, int(base_width / 2)):
            for col in range(0, base_width):
                chosen_color = colors[random.randint(0, len(colors) - 1)]
                base_img[row, col] = chosen_color
                base_img[base_width - row - 1, col] = chosen_color

        scaled_img = IdenticonGenerator.__scale_img_to_multiple(base_img, width)

        return scaled_img

    @staticmethod
    def __create_quarter_symmetric_img(width, colors):
        channels = 3
        base_width = 16
        base_shape = (base_width, base_width, channels)
        base_img = np.zeros(base_shape, np.uint8)

        for row in range(0, int(base_width / 2)):
            for col in range(0, int(base_width / 2)):
                chosen_color = colors[random.randint(0, len(colors) - 1)]
                base_img[row, col] = chosen_color
                base_img[row, base_width - col - 1] = chosen_color
                base_img[base_width - row - 1, col] = chosen_color
                base_img[base_width - row - 1, base_width - col - 1] = chosen_color

        scaled_img = IdenticonGenerator.__scale_img_to_multiple(base_img, width)

        return scaled_img

    @property
    def vertical_symmetry(self):
        return self.__vertical_symmetry

    @vertical_symmetry.setter
    def vertical_symmetry(self, value):
        pass

    @property
    def horizontal_symmetry(self):
        return self.__horizontal_symmetry

    @horizontal_symmetry.setter
    def horizontal_symmetry(self, value):
        pass

    @property
    def quarter_symmetry(self):
        return self.__quarter_symmetry

    @quarter_symmetry.setter
    def quarter_symmetry(self, value):
        pass


if __name__ == "__main__":
    idgen = IdenticonGenerator()
    parser = argparse.ArgumentParser(description="Generate an identicon from a given string.")
    parser.add_argument("string", type=str, help="a string from which to generate an identicon")
    parser.add_argument("directorypath", type=str, help="the path to the directory in which to write generated "
                                                        "identicons")
    parser.add_argument("-sym", "--symmetry", type=int, help="the integer representing the type of symmetry desired "
                                                             "(horizontal=1, vertical=2, quarter=3)", default=1)
    parser.add_argument("-w", "--width", type=int, help="the desired pixel width of the identicon (at least 16)",
                        default=16)
    parser.add_argument("-c", "--colors", type=int, help="the number of colors from which to create the identicon",
                        default=3)
    parser.add_argument("-min", "--hsvmin", type=float, nargs=3, help="the minimum percentages of hue, saturation, and value "
                                                             "from which to generate colors", default=(0.0, 0.2, 0.2))
    parser.add_argument("-max", "--hsvmax", type=float, nargs=3, help="the maximum percentages of hue, saturation, and value "
                                                             "from which to generate colors", default=(1.0, 0.8, 0.8))
    args = parser.parse_args()
    
    rgbimg = idgen.generate(args.string, args.symmetry, args.width, args.colors, args.hsvmin, args.hsvmax)

    dirpath = Path(args.directorypath)
    if not dirpath.is_dir():
        dirpath.mkdir()
    filepath = dirpath / "{}.png".format(args.string)
    cv.imwrite(str(filepath), rgbimg)
