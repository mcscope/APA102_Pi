import math
from random import random
from liteup.schemes.scheme import Scheme

from liteup.APA102.color_utils import hue_to_rgb


def HSV_from_place(hue, place, total):
    # plot saturation over a complete sin wave
    saturation = math.sin((place / total) * (2 * math.pi))
    if saturation < 0:
        saturation *= -1
        # find complement
        hue = 1 - hue
    # use saturation as value + brightness %
    # to provide pleasing effect
    return (*hue_to_rgb(hue, saturation, saturation), saturation * 100)


class Complement(Scheme):

    def init(self):
        hue = random()
        for idx in range(self.strip.num_leds):
            self.strip.set_pixel(
                idx,
                *HSV_from_place(hue, idx, self.strip.num_leds),
                gamma=True)

    def paint(self):
        self.strip.rotate()
        return True
