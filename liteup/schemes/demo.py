'''
This is a demo scheme that shows how to program these.
Start editing here!
Each scheme should inherit from the Scheme class, or one of it's children.
For ones that inherit from Scheme, you should define init and paint.
Init will be called once when the scheme is started, and then paint will be called
over and over again very quickly, to draw the pattern.

There are several utility functions in Scheme, and elsewhere in the repository.
I have support for a couple different ways of representing color and converting
between colors, gamma correction, and maintaining state between paints with generators.

There's also some schemes that use an api to control what they display.
They're a little bit tricky because the API call can be very long but the paint
calls must be rapid. To see one, look at the Muni scheme.

Looking at the other schemes is a great way to get inspiration and see what's
available. easy_schemes.py is a great source but there are lots to look at.
'''
from liteup.schemes.scheme import Scheme
from liteup.APA102.color_utils import hue_to_rgb


class Demo(Scheme):
    ui_select = True

    PAUSE_BETWEEN_PAINTS = 0.010

    def init(self):
        self.current_led = 0

    def paint(self):
        r, g, b = hue_to_rgb(self.current_led / self.options.num_leds)
        self.strip.set_pixel(self.current_led, r, g, b, self.options.brightness)
        self.current_led += 1
        if self.current_led >= self.options.num_leds:
            self.current_led = 0
            strip.rotate()

        return True
