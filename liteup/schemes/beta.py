import math
from liteup.schemes.base_schemes import GeneratorScheme
from liteup.APA102.color_utils import linear_hue_to_rgb
import numpy as np
from scipy import stats

SIGNAL_SIZE = 20


class Beta(GeneratorScheme):
    """
    A statistics visualization that shows the gradual 'training' of a beta
    distribution. It's trained on coin flips that are sampled from a
    distribution with an unknown probability.
    """
    PAUSE_BETWEEN_PAINTS = 0.1   # Override to control animation speed!
    ui_select = True

    def generator(self):
        self.size = self.options.num_leds - SIGNAL_SIZE
        N_Trials = 100
        p = .3
        a = 1
        b = 1
        x = np.linspace(0, 1, self.size)
        for i in range(N_Trials):
            trial = stats.bernoulli.rvs(p)
            if trial == 1:
                a += 1
            else:
                b += 1

            self.array = stats.beta(a, b).pdf(x)
            yield self.draw(trial)

    def draw(self, success):
        """
        Draw an array of our samples
        """
        maxval = float(max(self.array))

        for idx, count in enumerate(self.array):
            val = count / (maxval + 0.1)
            print(val)
            r, g, b = linear_hue_to_rgb(val)
            self.strip.set_pixel(idx, r, g, b, 1, gamma=True)

        for idx in range(self.size, self.size + SIGNAL_SIZE):
            # We'll add a helpful signal to let you the result of our sample
            if success:
                r, g, b = 255, 255, 255
            else:
                r, g, b = 0, 0, 0
            self.strip.set_pixel(idx, r, g, b, 1, gamma=True)

        return True
