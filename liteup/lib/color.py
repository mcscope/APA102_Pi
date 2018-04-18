from random import randint
import colorsys
from liteup.APA102.color_utils import gamma_correct_color, gamma_correct, hue_to_rgb


class Color:
    __slots__ = ["r", "g", "b", "brightness"]

    def __init__(self, r, g, b, brightness, gamma=False):
        if gamma:
            r = gamma_correct(r)
            g = gamma_correct(g)
            b = gamma_correct(b)

        self.r = r
        self.g = g
        self.b = b
        self.brightness = brightness

    @classmethod
    def make_random(cls, maxval, brightness, gamma=False):
        raw_color = (randint(0, maxval),
                     randint(0, maxval),
                     randint(0, maxval),
                     brightness)

        return cls(*gamma_correct_color(raw_color))

    @classmethod
    def from_hue(cls, hue):
        return cls(*hue_to_rgb(hue), brightness=1, gamma=True)

    def paint(self, strip, number, brightness=None):

        strip.set_pixel(number, self.r, self.g, self.b,
                        brightness or self.brightness)

    def __lt__(self, other):
        hue, _, _ = colorsys.rgb_to_hsv(self.r, self.g, self.b)
        otherhue, _, _ = colorsys.rgb_to_hsv(other.r, other.g, other.b)
        return hue > otherhue

    def __eq__(self, other):
        return self.r.__dict__ == self.other.__dict__

    def __str__(self):
        return f"Color({self.r}, {self.g}, {self.b})({self.brightness})"

    def __repr__(self):
        return self.__str__()
