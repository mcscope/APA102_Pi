import random
from liteup.schemes.scheme import Scheme
from liteup.APA102.color_utils import linear_hue_to_rgb

ENERGY_FROM_FOOD = 2
MOVE_ENERGY = 0.05
ENERGY_REQUIRED_TO_BREED = 200
MAX_CRITTERS = 50


class Critter:
    init_energy = 5

    def __init__(self, place, team):
        self.place = place
        self.team = team
        self.skill = 1
        self.energy = self.init_energy

    def move(self):
        if self.energy < 0:
            return None

        move_options = [-1, 1] + [0] * 10
        move_choice = random.choice(move_options)
        if move_choice != 0:
            self.energy = self.energy - MOVE_ENERGY
        return move_choice

    def fight(self, other_critter, strip):
        if other_critter.team != self.team:
            strip.set_pixel_rgb(self.place, 0xFFFFFF, 100)
            # what if this creature only dmanages others
            # self.energy -= other_critter.skill
            other_critter.energy -= self.skill * 4
            self.skill += 0.1

        if other_critter.energy < 0 and self.energy > 0:
            # I win
            self.skill += 1
            self.energy += ENERGY_FROM_FOOD

    def eat(self, breed_callback, can_breed):
        self.energy += ENERGY_FROM_FOOD
        self.energy = min(self.energy, ENERGY_REQUIRED_TO_BREED)
        if can_breed and self.energy == ENERGY_REQUIRED_TO_BREED:
            self.energy = 5
            breed_callback(self.place, self.team)

    def draw(self, strip):
        # Red Team
        hue = 0.95
        if self.team:
            hue = 0.1  # Blue team
        color = linear_hue_to_rgb(hue,
                                  saturation=min(self.skill / 5, 1),
                                  value=0.5 * (min(100, self.energy) / 100) + 0.5
                                  )

        strip.set_pixel(self.place, *color)
        # for x in len(skill):
        # strip.set_pixel_rgb(self.place + x - int(x / 2), *color)


class RTS(Scheme):
    """
    A Scheme built like a real-time strategy game!
    RTS = Real time Scheme
    """

    init_food = 200
    step_food = 1
    PAUSE_BETWEEN_PAINTS = 0.01

    def init(self):
        self.food = set()
        self.generate_food(self.init_food)
        self.generate_critters()

    def paint(self):
        self.paint_background()

        self.generate_food(self.step_food)
        self.paint_food()
        self.move_critters()
        return True

    def generate_critters(self):
        self.critters = []
        self.critters.append(Critter(0, False))
        opposite = int(self.strip.num_leds / 2)
        self.critters.append(Critter(opposite, True))

    def generate_food(self, numfood):
        all_places = set(range(self.strip.num_leds))

        empty_spaces = all_places - self.food

        numfood = min(numfood, len(empty_spaces))
        new_food_spaces = random.sample(empty_spaces, numfood)
        for new_food_space in new_food_spaces:
            self.food.add(new_food_space)

    def paint_background(self):
        for led in range(self.strip.num_leds):
            self.strip.set_pixel(led, 1, 1, 1, 1)

    def paint_food(self):
        for food_place in self.food:
            self.strip.set_pixel(food_place, 0, 100, 0, 1)

    def move_critters(self):
        critter_places = {critter.place: critter for critter in self.critters}
        for critter in self.critters:
            place = critter.place

            movement = critter.move()
            if movement is None:

                self.critters.remove(critter)
                del critter_places[place]
                continue

            new_place = (place + movement + self.strip.num_leds) % self.strip.num_leds
            if new_place > self.strip.num_leds:
                new_place = new_place - self.strip.num_leds

            if new_place in critter_places and critter_places[new_place] is not critter:
                # don't move there, just fight it
                critter.fight(critter_places[new_place], self.strip)
                continue

            critter.place = new_place

            if new_place in self.food:
                self.food.discard(new_place)
                critter.eat(breed_callback=self.add_child,
                            can_breed=len(self.critters) < MAX_CRITTERS)

            critter.draw(self.strip)

    def add_child(self, place, team):
        """
        called by critter!
        """

        def _add_child(new_place):
            self.critters.append(Critter(new_place, team))

        critter_places = {critter.place: critter for critter in self.critters}
        if place - 1 not in critter_places:
            _add_child(place - 1)

        if place + 1 not in critter_places:
            _add_child(place + 1)
