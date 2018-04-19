import math
import time
from random import random
from liteup.APA102.color_utils import linear_hue_to_rgb
from liteup.schemes.base_schemes import GeneratorScheme
import attr

USE_FOCUS = True


class Case:
    PRESORTED = 1
    REVERSE = 2


@attr.s
class Visual(object):
    highlights = attr.ib(default=attr.Factory(list))
    focus = attr.ib(default=None)


def fresh_random_array(size, case=None):
    array = []
    for _ in range(size):
        array.append(random())
    if case:
        if case == Case.PRESORTED:
            array.sort()
        if case == Case.REVERSE:
            array.sort(reverse=True)
    return array


def mergesort(array, start=None, stop=None):
    if start is None and stop is None:
        start, stop = 0, len(array)
    if stop - start < 2:
        # Already sorted
        return True
    midpoint = start + math.ceil((stop - start) / 2)
    yield from mergesort(array, start, midpoint)
    yield from mergesort(array, midpoint, stop)

    # merge!
    lhead, lstop = start, midpoint
    rhead = midpoint
    yield Visual([], (start, stop))

    # there's actual efficent in-place merge algorithm
    # so we're gonna visually simulate it by inserting elements before
    # the left list
    while lhead < lstop and rhead < stop:
        if array[lhead] < array[rhead]:
            # easy, it's already in the right spot
            lhead += 1
            yield Visual([lhead - 1], (start, stop))
        else:
            tmp = array.pop(rhead)
            array.insert(lhead, tmp)
            lhead += 1
            lstop += 1
            rhead += 1
            yield Visual([lhead + 1, rhead - 1], (start, stop))

    yield Visual([], (start, stop))


def swap(array, x, y):
    yield Visual([x, y])
    tmp = array[x]
    array[x] = array[y]
    array[y] = tmp
    yield Visual([x, y])


def bubblesort(array):
    # Bubblesort it... it's the only way to be sure

    for _ in range(math.ceil((len(array) / 2))):
        for x in range(len(array) - 1):
            if array[x] > array[x + 1]:
                yield from swap(array, x, x + 1)

        for x in range(len(array) - 2, -1, -1):
            if array[x] > array[x + 1]:
                yield from swap(array, x, x + 1)


def heapsort(array):
    yield from heapify(array)

    for sorted_head in range(len(array) - 1, 0, -1):
        # Max value will always be at position 0 of heap.
        # Swap it to our new head
        yield from swap(array, 0, sorted_head)
        # That ruined our heap, so reheap
        yield from siftdown(array, 0, sorted_head - 1)


def heapify(array):
    """
    O(n) build a heap in-place

    starts as having a heap of len 1, and then keeps adding 'broken' heads t
    and fixing them, until we've added them all.

    """
    for idx in range(len(array), -1, -1):
        yield from siftdown(array, idx, len(array) - 1)


def siftdown(array, start, end):
    """
    Take a 'broken' heap (a heap with a possible misplaced root)
    and fix it by swapping with it's children

    [0,1,0,x,x,0,0]
    """
    yield Visual([start])
    root = start
    leftchild = (start) * 2 + 1

    while leftchild <= end:
        rightchild = root * 2 + 2
        smallest = root

        if array[smallest] < array[leftchild]:
            smallest = leftchild
        if rightchild <= end and array[smallest] < array[rightchild]:
            smallest = rightchild

        if smallest == root:
            # We didn't find a smaller child.
            # This heap is (now) healthy!
            return
        else:
            # We found a smaller child.
            # Swap in there, then sift down from that subtree
            yield from swap(array, root, smallest)
            root = smallest
            leftchild = root * 2 + 1


def quicksort(array, start=None, stop=None):
    if start is None and stop is None:
        start, stop = 0, len(array)
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
            yield Visual([hole], focus=(start, stop))
        else:
            # gotta put it on the other side
            tmp = array[larger_index]
            array[larger_index] = array[smaller_index]

            array[smaller_index] = tmp
            smaller_index += 1
            yield Visual([smaller_index, larger_index], focus=(start, stop))

    array[hole] = pivot
    yield Visual([hole], focus=(start, stop))

    yield from quicksort(array, start, hole)
    yield from quicksort(array, hole + 1, stop)
    yield Visual(focus=(start, stop))


class Sort(GeneratorScheme):
    PAUSE_BETWEEN_PAINTS = 0.1   # Override to control animation speed!
    ui_select = True

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
            for case in (None, Case.PRESORTED, Case.REVERSE):
                self.PAUSE_BETWEEN_PAINTS = 0.0
                yield from self.draw_sort(quicksort, case)
                yield from self.draw_sort(mergesort, case)
                yield from self.draw_sort(heapsort, case)
                yield from self.draw_sort(bubblesort, case)
                self.PAUSE_BETWEEN_PAINTS = 0.1
                yield from self.draw_sort(mergesort, case)
                yield from self.draw_sort(heapsort, case)
                yield from self.draw_sort(quicksort, case)
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
            value = 1.0
            if USE_FOCUS and vis.focus and (idx < vis.focus[0] or idx > vis.focus[1]):
                value = 0.5

            r, g, b = linear_hue_to_rgb(color, value=value)
            brightness = 33 if idx in vis.highlights else 1
            self.strip.set_pixel(idx, r, g, b, brightness, gamma=True)

        return True
