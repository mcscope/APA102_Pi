import colorsys
import time
from random import random
from liteup.lib.color import Color
import math
from liteup.schemes.base_schemes import GeneratorScheme
# merge sort!


def clean_array(size):
    array = []
    for _ in range(size):
        raw_color = colorsys.hsv_to_rgb(random(), 1.0, 1.0)
        new_color = Color(*(255 * v for v in raw_color),
                          brightness=1, gamma=True)
        array.append(new_color)
    return array


def mergesort(array, start, stop):
    if stop - start < 2:
        # Already sorted bra
        return True
    midpoint = start + math.ceil((stop - start) / 2)
    yield from mergesort(array, start, midpoint)
    yield from mergesort(array, midpoint, stop)

    # merge!
    lhead, lstop = start, midpoint
    rhead = midpoint

    print(f"sorting {array[start:stop]} ")
    # there's actual efficent in-place merge algorithm
    # so we're gonna visually simulate it by inserting elements before
    # the left list
    while lhead < lstop and rhead < stop:
        if array[lhead] < array[rhead]:
            # easy, it's already in the right spot
            lhead += 1
            yield [lhead - 1]
        else:
            tmp = array.pop(rhead)
            array.insert(lhead, tmp)
            lhead += 1
            lstop += 1
            rhead += 1
            yield [lhead + 1, rhead - 1]
    print(f"sorted   {array[start:stop]}")


def bubblesort(array, start, stop):
    # Bubblesort it... it's the only way to be sure
    def swap(x, y):
        tmp = array[x]
        array[x] = array[y]
        array[y] = tmp

    for _ in range(math.ceil((len(array) / 2))):
        for x in range(len(array) - 1):
            if array[x] > array[x + 1]:
                swap(x, x + 1)
                yield [x, x + 1]

        for x in range(len(array) - 2, -1, -1):
            if array[x] > array[x + 1]:
                swap(x, x + 1)
                yield [x, x + 1]


def quicksort(array, start, stop):
    if stop - start < 2:
        return True

    larger_index = stop - 2
    smaller_index = start
    # the "whole" starts where the pivot does
    pivot = array[stop - 1]
    hole = stop - 1

    while larger_index + 1 > smaller_index:
        if pivot < array[larger_index]:
            # good case, this is the right side
            # just shift the whole and continue!
            array[hole] = array[larger_index]
            larger_index -= 1
            hole -= 1
            yield [hole]
        else:
            # gotta put it on the other side
            tmp = array[larger_index]
            array[larger_index] = array[smaller_index]

            array[smaller_index] = tmp
            smaller_index += 1
            yield [smaller_index, larger_index]

    array[hole] = pivot
    yield [hole]

    yield from quicksort(array, start, hole)
    yield from quicksort(array, hole + 1, stop)


class Sort(GeneratorScheme):
    PAUSE_BETWEEN_PAINTS = 0.00001   # Override to control animation speed!
    ui_select = True

    def draw_sort(self, sort):
        array = clean_array(self.options.num_leds)
        for highlight in sort(array, 0, self.options.num_leds):
            yield self.draw(array, highlight)

        for _ in range(5):
            yield self.draw(array, [])
            time.sleep(1)
            yield self.draw(sorted(array), [])
            time.sleep(1)

    def generator(self):
        while True:
            yield from self.draw_sort(mergesort)
            yield from self.draw_sort(quicksort)
            yield from self.draw_sort(bubblesort)

    def draw(self, array, highlights):
        for idx, color in enumerate(array):
            if idx in highlights:
                color.paint(self.strip, idx, brightness=100)
            else:
                color.paint(self.strip, idx)

        return True
