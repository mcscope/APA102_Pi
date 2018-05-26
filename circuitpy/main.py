"""
Liteup 'port' of 2 schemes (perlin and sorts) to Adafruit Gemma
Written in a hackathon at pycon 2018 as a badge decoration
"""
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode
from digitalio import DigitalInOut, Direction, Pull
from analogio import AnalogIn, AnalogOut
import neopixel
from touchio import TouchIn
import adafruit_dotstar as dotstar
import microcontroller
import board
import time
import random
import math
from perlin import gen_perlin
# One pixel connected internally!
dot = dotstar.DotStar(board.APA102_SCK, board.APA102_MOSI, 1, brightness=0.3)

# Built in red LED
led = DigitalInOut(board.D13)
led.direction = Direction.OUTPUT


# Capacitive touch on A2
touch2 = TouchIn(board.A2)

# Used if we do HID output, see below
kbd = Keyboard()
REG_BRIGHTNESS = 0.05
FLASH_BRIGHTNESS = 0.2

######################### HELPERS ##############################


def hue_to_rgb(hue):
    """
    Convert float hue value to a rgb color value. Probably doesn't match
    actual hsv conversion, but good for rainbows.
    """
    return wheel(hue * 255)


# Helper to give us a nice color swirl

def wheel(pos):
    # Input a value 0 to 255 to get a color value.
    # The colours are a transition r - g - b - back to r.
    if (pos < 0):
        return [0, 0, 0]
    if (pos > 255):
        return [0, 0, 0]
    if (pos < 85):
        return [int(pos * 3), int(255 - (pos * 3)), 0]
    elif (pos < 170):
        pos -= 85
        return [int(255 - pos * 3), 0, int(pos * 3)]
    else:
        pos -= 170
        return [0, int(pos * 3), int(255 - pos * 3)]


def is_touched():
    # set analog output to 0-3.3V (0-65535 in increments)

    # use A2 as capacitive touch to turn on internal LED
    if touch2.value:
        print("A2 touched!")
        # optional! uncomment below & save to have it sent a keypress
        # kbd.press(Keycode.A)
        # kbd.release_all()
        return True

    led.value = touch2.value


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
    yield True

    # there's actual efficent in-place merge algorithm
    # so we're gonna visually simulate it by inserting elements before
    # the left list
    while lhead < lstop and rhead < stop:
        if array[lhead] < array[rhead]:
            # easy, it's already in the right spot
            lhead += 1
            yield True
        else:
            tmp = array.pop(rhead)
            array.insert(lhead, tmp)
            lhead += 1
            lstop += 1
            rhead += 1
            yield True

    yield True


def swap(array, x, y):
    tmp = array[x]
    array[x] = array[y]
    array[y] = tmp
    yield


def bubblesort(array):
    # Bubblesort it... it's the only way to be sure

    for _ in range(math.ceil((len(array) / 2))):
        for x in range(len(array) - 1):
            if array[x] > array[x + 1]:
                yield from swap(array, x, x + 1)

        for x in range(len(array) - 2, -1, -1):
            if array[x] > array[x + 1]:
                yield from swap(array, x, x + 1)


######################### MAIN LOOP ##############################

def flash(strip):
    strip.brightness = FLASH_BRIGHTNESS
    yield 0.1
    strip.brightness = REG_BRIGHTNESS
    yield 0.3


def draw(strip, array, time=0.1):
    for i in range(len(strip)):
        strip[i] = hue_to_rgb(array[i])
    yield time


def sort_scheme(strip):
    while True:
        for alg in [bubblesort, mergesort]:
            array = [random.random() for _ in strip]
            for _ in alg(array):
                yield from draw(strip, array)
            for _ in range(2):
                yield from flash(strip)


def fade(array, idx, start, end):
    diff_step = (end - start) / 8.0
    for x in range(8):
        array[idx] = start + x * diff_step
        yield


def perlin_scheme(strip):
    array = [0] * len(strip)
    pervals = gen_perlin()
    fadelist = []
    while True:
        for idx in range(len(strip)):
            fadelist.append((idx, array[idx], next(pervals), 0))
            newlist = []
            for idx, start, end, step in fadelist:
                diff_step = (end - start) / 8.0
                array[idx] = start + step * diff_step
                if step < 8:
                    newlist.append((idx, start, end, step + 1))
            fadelist = newlist
            yield from draw(strip, array)


def main():
    num_leds = 16
    strip = neopixel.NeoPixel(board.D1, num_leds, auto_write=False)
    strip.brightness = REG_BRIGHTNESS

    gen_idx = 0
    gens = [sort_scheme(strip), perlin_scheme(strip)]
    # gens = [perlin_scheme(strip)]
    while True:
        sleeptime = next(gens[gen_idx % len(gens)])
        strip.show()
        time.sleep(sleeptime)
        if is_touched():
            gen_idx += 1
            next(gens[gen_idx % len(gens)])
            strip.show()
            # time to move your finger away
            time.sleep(0.7)

main()
