from random import randint
from liteup.lib.perlin import gen_perlin_ints
from liteup.APA102.color_utils import gamma_correct, gamma_correct_color
from liteup.schemes.scheme import Scheme
from liteup.schemes.base_schemes import GeneratorScheme


class RandomColorChaos(Scheme):
    PAUSE_BETWEEN_PAINTS = 1.5

    def paint(self):
        for led in range(self.strip.num_leds):
            self.strip.set_pixel(led, randint(0, 255), randint(0, 255), randint(0, 255), 100)
        return True


class RandomColorFade(Scheme):
    PAUSE_BETWEEN_PAINTS = 0.05
    autofade = True

    def paint(self):
        if not self.transitions:
            for led in range(self.strip.num_leds):
                cur_color = self.strip.get_pixel(led)
                new_color = gamma_correct_color((randint(0, 255), randint(0, 255), randint(0, 255), randint(0, 100)))
                self.transitions.append(self.fade(led, cur_color, new_color, steps=30))


class Perlin(GeneratorScheme):
    options_supported = ["brightness"]

    PAUSE_BETWEEN_PAINTS = 0.04
    ui_select = True

    # how long the perlin wave is, and how fast they adjust
    num_steps = 50
    # how chaotic the perlin is. higher is more stable
    perlin_octaves = 6

    def generator(self):

        waves = [
            self.perlin_wave(corner)
            for corner in self.options.corners
        ]
        while True:
            self.tick_generators(waves)
            yield True

    def perlin_wave(self, start_point):
        sub_gens = []

        r_perlin = gen_perlin_ints(0, 255, num_octaves=self.perlin_octaves)
        g_perlin = gen_perlin_ints(0, 255, num_octaves=self.perlin_octaves)
        b_perlin = gen_perlin_ints(0, 255, num_octaves=self.perlin_octaves)
        while True:
            for led in range(start_point, self.strip.num_leds):
                cur_color = self.strip.get_pixel(led)
                new_color = [next(r_perlin),
                             next(g_perlin),
                             next(b_perlin),
                             self.options.brightness]
                new_color = gamma_correct_color(new_color)

                sub_gens.append(
                    self.fade(led, cur_color, new_color, steps=self.num_steps))

                # we have a tail of colors we want to update
                self.tick_generators(sub_gens)

                yield True
            start_point = 0
