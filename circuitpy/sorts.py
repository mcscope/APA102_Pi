import math
import time
from random import random


# def linear_hue_to_rgb(hue):
#     """
#     Hacked together replacement for my HSV->RGB color library
#     Using the adafruit wheel function
#     """

#     pos = hue * 255
#     # Input a value 0 to 255 to get a color value.
#     # The colours are a transition r - g - b - back to r.
#     if (pos < 0):
#         return [0, 0, 0]
#     if (pos > 255):
#         return [0, 0, 0]
#     if (pos < 85):
#         return [int(pos * 3), int(255 - (pos * 3)), 0]
#     elif (pos < 170):
#         pos -= 85
#         return [int(255 - pos * 3), 0, int(pos * 3)]
#     else:
#         pos -= 170
#         return [0, int(pos * 3), int(255 - pos * 3)]


# class Case:
#     PRESORTED = 1
#     REVERSE = 2


# class Visual(object):

#     def __init__(highlights=None, focus=None):
#         self.highlights = highlights or []
#         self.focus = focus


# def fresh_random_array(size, case=None):
#     array = []
#     for _ in range(size):
#         array.append(random())
#     if case:
#         if case == Case.PRESORTED:
#             array.sort()
#         if case == Case.REVERSE:
#             array.sort(reverse=True)
#     return array


# def mergesort(array, start=None, stop=None):
#     if start is None and stop is None:
#         start, stop = 0, len(array)
#     if stop - start < 2:
#         # Already sorted
#         return True
#     midpoint = start + math.ceil((stop - start) / 2)
#     yield from mergesort(array, start, midpoint)
#     yield from mergesort(array, midpoint, stop)

#     # merge!
#     lhead, lstop = start, midpoint
#     rhead = midpoint
#     yield Visual([], (start, stop))

#     # there's actual efficent in-place merge algorithm
#     # so we're gonna visually simulate it by inserting elements before
#     # the left list
#     while lhead < lstop and rhead < stop:
#         if array[lhead] < array[rhead]:
#             # easy, it's already in the right spot
#             lhead += 1
#             yield Visual([lhead - 1], (start, stop))
#         else:
#             tmp = array.pop(rhead)
#             array.insert(lhead, tmp)
#             lhead += 1
#             lstop += 1
#             rhead += 1
#             yield Visual([lhead + 1, rhead - 1], (start, stop))

#     yield Visual([], (start, stop))


# def swap(array, x, y):
#     yield Visual([x, y])
#     tmp = array[x]
#     array[x] = array[y]
#     array[y] = tmp
#     yield Visual([x, y])


# def bubblesort(array):
#     # Bubblesort it... it's the only way to be sure

#     for _ in range(math.ceil((len(array) / 2))):
#         for x in range(len(array) - 1):
#             if array[x] > array[x + 1]:
#                 yield from swap(array, x, x + 1)

#         for x in range(len(array) - 2, -1, -1):
#             if array[x] > array[x + 1]:
#                 yield from swap(array, x, x + 1)


class Sort(object):

    def __init__(self, ring):
        self.strip = ring

    def draw_sort(self, sort, case=None):
        array = fresh_random_array(self.options.num_leds, case)
        for visualization in sort(array):
            yield self.draw(array, visualization)

        for _ in range(5):
            yield self.draw(array, Visual())
            time.sleep(1)
            yield self.draw(sorted(array), Visual())
            time.sleep(1)

    def generator(self):
        while True:
            yield from self.draw_sort(mergesort, case)
            yield from self.draw_sort(bubblesort, case)

    def draw(self, array, vis):
        """
        Draw the current array.
        We're using a linearized version of hue to make it very easy to
        distinguish low values from high values (naive hue 'wraps' around)

        focus is a tuple of min/max that is the area the algorithm is focused on r
        ight now, like it's recursive scope.
        Highlights are things being currently swapped

        """
        for idx, color in enumerate(array):
            # value = 1.0
            # if USE_FOCUS and vis.focus and (idx < vis.focus[0] or idx > vis.focus[1]):
            #     value = 0.5

            r, g, b = linear_hue_to_rgb(color)
            # brightness = 33 if idx in vis.highlights else 1
            self.strip[idx] = [r, g, b]

        return True
