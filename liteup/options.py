import os
import configargparse
from liteup.schemes.all_schemes import all_schemes, SCHEME_CHOICES
import sys

for name, cls in SCHEME_CHOICES.items():
    print(name, cls)


def find_config():
    # do some work to always find a config file next to us in config.py
    curfile_path = os.path.abspath(__file__)
    cur_dir = os.path.abspath(os.path.join(curfile_path, os.pardir))
    return os.path.abspath(os.path.join(cur_dir, 'config.py'))


config_path = find_config()

parser = configargparse.ArgParser(default_config_files=[config_path])
parser.add('-c', '--my-config', required=False, is_config_file=True, help='config file path')
parser.add('scheme', type=str.lower, nargs="?", help='Choose a Scheme to show!', choices=SCHEME_CHOICES, default="flux")
parser.add('--servers', type=str, action='append', help='What servers should I recieve config from? defaults to ["127.0.0.1:5000"]', default=["127.0.0.1:5000"])
parser.add('-b', '--brightness', type=int, help='Brightness. Percentage 1-100. Not all schemes use this', default=100)
parser.add('--speed', type=int, help='speed 1-100.', default=100)
parser.add('--corners', type=int, action='append', help='Where are meaningful start points in the installation?', default=[])
parser.add('--center', type=int, help='Wheres the logical center of the leds?', default=0)
parser.add('--force_hour', type=int, help='force an hour (for flux)')
parser.add('--save_image', action='store_true', default=False, help='Output an image file (image.ppm) instead of writing to leds')
parser.add('--num_leds', type=int, default=390, help='how many leds to light up')
parser.add('--from_ppm', type=str, help='ImageScan scheme can scan over a ppm image')
parser.add('--isolate', action='store_true', help="Don't poll servers to change config, just stick with initial config")
parser.add('--sort_alg',
           type=str,
           nargs="?",
           help='Which sort alg to use if sort chosen!',
           choices=['merge', 'heap', 'bubble', 'quick', ""],
           default="")


def parse_options(extra_config={}):
    command_line_format = []
    for name, value in extra_config.items():
        if name == "scheme":
            command_line_format.append(f'{value}')
        else:
            command_line_format.append(f'--{name}={value}')
    options = parser.parse_args(sys.argv[1:] + command_line_format)

    if options.from_ppm:
        # Right now image playback is stand-alone
        options.isolate = True
        options.scheme = "imagescan"

    return options
