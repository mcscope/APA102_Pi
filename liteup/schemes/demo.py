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
All schemes must be imported in all_schemes.py so the client and the server are
aware of them.
'''
from liteup.schemes.scheme import Scheme
from liteup.APA102.color_utils import hue_to_rgb


class Demo(Scheme):
    options_supported = ["brightness", "speed"]

    ui_select = True

    def init(self):
        self.counter = 0
        self.current_led = 0
        self.PAUSE_BETWEEN_PAINTS = 1 / (10 * self.options.speed)

    def paint(self):
        self.counter += 1
        self.current_led += 1
        self.strip.rotate()

        r, g, b = hue_to_rgb(self.current_led / self.options.num_leds)
        self.strip.set_pixel(self.current_led, r, g, b, self.options.brightness)
        if self.current_led >= self.options.num_leds:
            self.current_led = 0

        return True

    def on_options_change(self, new_options):
        """
        because we set our pause value on init, when options change
        we must reset it. This should let us speed up without resetting.
        """
        super().on_options_change(self, new_options)
        self.PAUSE_BETWEEN_PAINTS = 1 / (10 * self.options.speed)
