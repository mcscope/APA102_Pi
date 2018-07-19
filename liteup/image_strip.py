import os
from APA102 import APA102
from lib.ppm import write_image

filename = "scheme_images/strip.ppm"
filename = os.path.join(os.path.dirname(__file__), filename)


class ImageStrip(APA102):
    """
    This is a strip you can plug into schemes instead of a real APA102 Strip.
    It mimics the public API but instead of lighting up LEDS, it writes the LED
    pattern to a big PPM file
    """

    led_buffer = []

    def show(self):

        self.led_buffer.append(self.leds)
        self.leds = list(self.leds)
        if len(self.led_buffer) % 100 == 50:
            write_image(self.led_buffer, filename=filename)
