import random


def gen_perlin(num_octaves=5):
    octaves = []
    max_possible_value = 0.0

    for octave_num in range(num_octaves):

        cur_step_size = 2 ** octave_num

        # make the generator for this octave
        octaves.append(gen_octave(step=cur_step_size))

    while True:
        cur_value = 0.0
        max_possible_value = 0.0

        # go through all the octaves and get their values, scale them and add them to our curent value.
        # (biggest octave should be scaled at 0.5, smallest at 1/2*octave)

        for octave_index, octave in enumerate(octaves):
            scale_for_value = 1.0 / (2 ** (num_octaves - octave_index))
            max_possible_value += 1.0 * scale_for_value
            cur_value += scale_for_value * next(octave)

        # normalize after everything is done
        normalized_value = cur_value / max_possible_value
        yield normalized_value


def gen_octave(step):
    prev_value = random.random()
    fill_beginning = 0
    while True:
        cur_random_val = random.random()
        how_many_to_fill = step
        for how_many_filled in range(how_many_to_fill):
            linear_interpolation_to_new_point = prev_value + (cur_random_val - prev_value) * (how_many_filled / how_many_to_fill)
            yield linear_interpolation_to_new_point

        prev_value = cur_random_val
        fill_beginning = fill_beginning + step
