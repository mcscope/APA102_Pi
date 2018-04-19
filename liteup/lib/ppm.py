from itertools import zip_longest
from math import ceil

# Recipe from Itertools docs


def grouper(n, iterable, fillvalue=None):
    "grouper(3, 'ABCDEFG', 'x') --> ABC DEF Gxx"
    args = [iter(iterable)] * n
    return zip_longest(fillvalue=fillvalue, *args)


def write_image(led_buffer, filename):
    """
    PPM file format is a short header of magic numbers and width+height
    then the bytes of each R/G/B pixel.
    """
    print("writing %s lines to %s" % (len(led_buffer), filename))

    with open(filename, 'wb') as file:
        # ppm image is 1 pixel per led, with time going 'down'
        # all lines
        height = len(led_buffer)
        # each line (4 ints per pixel, so /4)
        width = len(led_buffer[0]) / 4
        ppm_header = b"P6 %d %d %d\n" % (width, height, 255)
        file.write(ppm_header)

        for led_line in led_buffer:
            # Fun fact! These are stored as an APA102 serial format,
            # It's BrightnessByte, R G B. the first is trash!
            # I'm dropping brightness here to simplify things
            # and fit our byte format into ppm nicely

            for _, blue, green, red in grouper(4, led_line, 0):
                file.write(b"%c%c%c" % (red, green, blue))


def read_image(filename, options):
    """
    read a ppm file and return the entire thing as
    [
        [B,r,g,b, B, r,g,b,],
    ]
    where B is 255, a brightness bit. this is so that
    this can be pushed directly into a APA102 strip.
    Soon we'll have a proper color class that can handle these conversions.
    """
    print("reading image from %s" % filename)

    LED_START = 0b11100000  # Three "1" bits, followed by 5 brightness bits
    MAX_BRIGHTNESS = 31  # Safeguard: Set to a value appropriate for your setup

    brightness = int(ceil(options.brightness / 100.0 * MAX_BRIGHTNESS))

    bright_bit = (brightness & 0b00011111) | LED_START

    with open(filename, "rb") as file:
        buf = file.read()
        # TODO handle comments!
        magicnum, rest = buf.split(maxsplit=1)
        assert magicnum == b'P6'
        if rest.startswith(b'#'):
            _, rest = rest.split(b"\n", maxsplit=1)

        width, height, maxval, image = rest.split(maxsplit=3)
        width = int(width)
        height = int(height)
        assert maxval == b'255'

        for line in grouper(3 * width, image):
            line_buf = []
            for r, g, b in grouper(3, line):
                line_buf.extend([bright_bit, b, g, r])
            if not all(isinstance(val, int) and val < 256 for val in line_buf):
                # bad line! skip
                print(f"Broken line detected in {filename}")
                continue

            yield line_buf
