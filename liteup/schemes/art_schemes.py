import math
from random import random
from liteup.schemes.base_schemes import GeneratorScheme

from liteup.APA102.color_utils import hue_to_rgb

def HSV_from_place(hue, place, total):
    # plot saturation over a complete sin wave
    saturation = math.sin(place/total) * (2*math.pi)
    if saturation < 0:
        saturation *= -1
        # find complement
        hue = 1- hue
    # use saturation as value to provide pleasing effect
    return(hue, saturation, saturation)

class Complement(GeneratorScheme):

    def generator(self):
        hue = random()

        for x in range(self.strip.num_leds):
            self.strip.paint(*HSV_from_place(hue, x, self.strip.num_leds))
