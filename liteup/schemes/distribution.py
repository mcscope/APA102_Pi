import time
from random import gauss, choice, randint, paretovariate, betavariate
import itertools
import math
from liteup.schemes.base_schemes import GeneratorScheme
from liteup.APA102.color_utils import linear_hue_to_rgb

NUM_SAMPLES = 1
WAIT_TIME = 500


class Distribution(GeneratorScheme):
    # PAUSE_BETWEEN_PAINTS = 0.0001   # Override to control animation speed!
    ui_select = True

    def sample_distribution(self, sample_fn):
        """
        Choose a spot to increment using our sample function, and increment it.
        The draw function will highlight that index to draw attention
        """
        samples = [int(sample_fn()) for _ in range(NUM_SAMPLES)]
        for sample in samples:
            if sample >= 0 and sample < len(self.array):
                self.array[sample] += 1

        yield self.draw(samples)

    def generator(self):
        size = self.options.num_leds

        def gaussian():
            return gauss(size / 2,
                         size / 8)

        def bimodal():
            if choice([1, 0]):
                return gauss(size / 2,
                             size / 8)
            else:
                return gauss(size * 0.73,
                             size / 16)

        def trimodal():
            mode = choice([0, 1, 2])
            if mode == 2:
                return gauss(size * 0.25,
                             size / 16)
            elif mode == 1:
                return gauss(size * 0.5,
                             size / 16)
            else:
                return gauss(size * 0.75,
                             size / 16)

        def uniform():
            return randint(0, size)

        def pareto():
            return paretovariate(0.1) - 1

        all_distributions = itertools.cycle([
            gaussian,
            bimodal,
            trimodal,
            uniform,
            pareto,
        ])
        while True:
            self.array = [0 for _ in range(size)]
            dist = next(all_distributions)
            for x in range(WAIT_TIME):
                yield from self.sample_distribution(dist)

    def draw(self, highlights):
        """
        To draw a gaussian, we need to go down the entire array, which is just
        numbers, and transform them into a color representation.
        I'm gonna start with like, heatmap colors that are normalized
        and I'll probbly iterate
        """
        maxval = float(max(self.array) + 0.1)
        ret = []
        for idx, count in enumerate(self.array):
            val = math.log(count + 0.1) / math.log(maxval + 0.1)
            if count == 0:
                val = 0.0
            r, g, b = linear_hue_to_rgb(val)
            brightness = 2 if idx in highlights else 1
            self.strip.set_pixel(idx, r, g, b, brightness, gamma=True)

        return True
