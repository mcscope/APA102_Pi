from liteup.schemes.base_schemes import Scheme
from random import randint, choice


class FlowBall(Scheme):
    PAUSE_BETWEEN_PAINTS = 0.00
    autofade = True

    basecolor = (0xFF, 0xFF, 0xFF, 50)
    _transitions = {}

    def init(self):
        self.setall(self.basecolor)
        colors = [
            (0xFF, 0, 0, 50),
            (0, 0xFF, 0, 50),
            (0, 0, 0xFF, 50),
            (0, 0xFF, 0xFF, 50),
            (0xFF, 0, 0xFF, 50),
            (0xFF, 0xFF, 0, 50),
        ]
        self._transitions["ball"] = self.make_ball(colors[0])

    def paint(self):
        return True

    @property
    def transitions(self):
        return list(self._transitions.values())

    @transitions.setter
    def transitions(self, val):
        pass

    def make_ball(self, color):
        center = randint(0, self.options.num_leds)
        dx = -0.2 * choice((2, 1, -1, -2))
        while True:
            center = self.bound(center + dx)
            self.fadeplace(center, color)

            displacement = self.bound(center + randint(-5, 5))
            self.fadeplace(displacement, (0, 0xFF, 0, 50),
                           )

            print(center, len(self.transitions))
            yield True

    def fadeplace(self, place, color):
        place = int(place)
        self._transitions[place] = (self.fade(place,
                                              color,
                                              self.basecolor,
                                              steps=30))

    def bound(self, item):
        if item < 0:
            return self.bound(item + self.options.num_leds)
        if item > self.options.num_leds:
            return self.bound(item - self.options.num_leds)
        return item
