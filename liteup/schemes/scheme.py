"""The module contains the base Scheme class"""
import asyncio
import time
import sys
from liteup.APA102.color_utils import byte_bound


class Scheme:
    """
    This is the base for all Scheme objects.
    They are similar to the color cycle template provided by APA102, but Schemes
    are intended to display perpetually (without the notion of *cycles*), and there
    is a larger client that controls starting and stopping Schemes.
    TODO: Schemes are also able to recieve configurable arguments from the API

    Schemes are intended to keep track of their own state, such as where they are
    in their animation. It should be incremented during each *update* call

    A specific scheme must subclass this template, and implement at least the
    'paint' method.
    """

    PAUSE_BETWEEN_PAINTS = 0.001  # Override to control animation speed!
    autofade = False
    ui_select = True
    # Override this if you'd like any ui-configurable options for you.
    # options must be defined in options.py
    options_supported = []

    def __init__(self, strip, options):
        self.strip = strip
        self.options = options
        self.transitions = []

    def init(self):
        """This method is called to initialize a Scheme.

        #TODO configurable arguments!

        The default does nothing. A particular subclass could setup
        variables, or even light the strip in an initial color.
        """
        pass

    def paint(self):
        """
        This method paints one subcycle. It must be implemented.
        """

        raise NotImplementedError("Please implement the paint() method")

    def super_paint(self):
        autofade_update = False
        if self.autofade and self.transitions:
            autofade_update = True
            self.tick_generators(self.transitions)

        did_paint_update = self.paint()
        return autofade_update or did_paint_update

    def cleanup(self):
        """Cleanup method."""
        self.stop()
        # don't clear if we have been switched off by our parent
        if self.running:
            self.strip.clear_strip()
            self.strip.cleanup()

    async def start(self):
        """This method does the actual work."""
        try:
            print("Starting: %s" % self.__class__.__name__)
            self.strip.clear_strip()
            self.init()  # Call the subclasses init method
            self.strip.show()
            self.running = True
            while self.running:
                need_repaint = self.super_paint()
                if need_repaint:
                    self.strip.show()  # repaint if required
                await asyncio.sleep(self.PAUSE_BETWEEN_PAINTS)
        finally:
            # Finished, cleanup everything
            self.cleanup()

    def stop(self):
        """This method is called to stop the scheme. It loops while self.running
        """
        self.running = False

    def on_new_options(self, new_options):
        self.options = new_options

    # A bunch of utility functions!
    def setall(self, color):
        for led in range(self.strip.num_leds):
            self.strip.set_pixel(led, *color)

    def tick_generators(self, gen_list):
        for gen in gen_list:
            try:
                next(gen)
            except StopIteration:
                gen_list.remove(gen)

    def wait(self, steps):
        for step in range(steps):
            yield True

    def fade(self, led_num, start_color, target_color, steps=10):
        """
        Returns a generator that will paint this pixel to the target over some
        steps. good with tick_generators()

        This uses linear interpretation.
        maybe another kind of interpretation would also be cool?

        """

        for cur_step in range(steps):
            stepcolor = [
                self.lin_interp(cur_step, steps, start_val, target_val)
                for start_val, target_val in zip(start_color, target_color)
            ]
            stepcolor = [byte_bound(x) for x in stepcolor]
            self.strip.set_pixel(led_num, *stepcolor)
            yield True

    @staticmethod
    def lin_interp(cur_step, num_steps, start_val, target_val):

        return int(start_val + ((target_val - start_val) * (cur_step / num_steps)))
