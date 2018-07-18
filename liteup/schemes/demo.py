'''
This is a demo scheme that shows how to program these.
Start editing here!
'''
import math
from datetime import datetime, timedelta
import itertools
import time
from liteup.schemes.scheme import Scheme
from liteup.APA102.color_utils import gamma_correct_color, hue_to_rgb


class Demo(Scheme):
    ui_select = True

    PAUSE_BETWEEN_PAINTS = 0.10

    def init(self):
        return False

    def paint(self):
        for x in range(0, self.options.num_leds):
            r, g, b = hue_to_rgb(x / self.options.num_leds)
            self.strip.set_pixel(x, r, g, b, self.options.brightness)
