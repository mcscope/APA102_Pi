import colorsys
import time
from random import random
from liteup.lib.color import Color
import math
from liteup.schemes.base_schemes import GeneratorScheme
# merge sort!


class Case:
    PRESORTED = 1
    REVERSE = 2


def fresh_random_array(size, case=None):
    array = []
    for _ in range(size):
        raw_color = colorsys.hsv_to_rgb(random(), 1.0, 1.0)
        new_color = Color(*(255 * v for v in raw_color),
                          brightness=1, gamma=True)
        array.append(new_color)
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


def swap(array, x, y):
    yield [x, y]
    tmp = array[x]
    array[x] = array[y]
    array[y] = tmp
    yield [x, y]


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
    yield [start]
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
    PAUSE_BETWEEN_PAINTS = 0.1   # Override to control animation speed!
    ui_select = True

    def draw_sort(self, sort, case=None):
        array = fresh_random_array(self.options.num_leds, case)
        for highlight in sort(array):
            yield self.draw(array, highlight)

        for _ in range(5):
            yield self.draw(array, [])
            time.sleep(1)
            yield self.draw(sorted(array), [])
            time.sleep(1)

    def generator(self):
        while True:
            for case in (None, Case.PRESORTED, Case.REVERSE):
                self.PAUSE_BETWEEN_PAINTS = 0.1
                yield from self.draw_sort(mergesort, case)
                yield from self.draw_sort(quicksort, case)
                yield from self.draw_sort(heapsort, case)
                yield from self.draw_sort(bubblesort, case)
                self.PAUSE_BETWEEN_PAINTS = 0.1
                yield from self.draw_sort(mergesort, case)
                yield from self.draw_sort(heapsort, case)
                yield from self.draw_sort(quicksort, case)
                yield from self.draw_sort(bubblesort, case)

    def draw(self, array, highlights):
        for idx, color in enumerate(array):
            if idx in highlights:
                color.paint(self.strip, idx, brightness=100)
            else:
                color.paint(self.strip, idx)

        return True
