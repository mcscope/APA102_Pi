#!/etc/python3
import asyncio
import json
from aiohttp import ClientSession
import aiohttp.client_exceptions
from APA102 import APA102
from image_strip import ImageStrip

from liteup.options import parse_options
from liteup.schemes.all_schemes import SCHEME_CHOICES

# FOR CLI OPTIONS LOOK IN OPTIONS.PY


def main():
    """
    Given our first scheme object, start painting.
    I make it async, and check for updates from the server in the background.
    The scheme yields every loop to let the supervisor have a chance to run
    Cooperative multitasking! Good when you write a single client!
    """
    options = parse_options()
    loop = asyncio.get_event_loop()  # event loop

    async def launch():
        # this is the supervisor loop

        old_config = {}
        old_scheme = None
        fresh_config = {"scheme_name": options.scheme}
        Stripcls = ImageStrip if options.save_image else APA102
        strip = Stripcls(num_leds=options.num_leds,
                         order="RGB",
                         max_speed_hz=5000000)  # Initialize the strip
        while True:
            if fresh_config and fresh_config != old_config:
                print(f"fresh config: {fresh_config}")

                # todo is it possible to truely parse these options with
                # configargparse?
                for name, value in fresh_config.items():
                    # todo attempt to not fake this
                    if name == "scheme_name":
                        continue
                    if name == 'brightness':
                        options.brightness = int(value)
                        print(options.brightness)

                fresh_scheme = fresh_config.get("scheme_name")
                if fresh_scheme != old_config.get("scheme_name"):
                    # TODO maybe we should ALWAYS do this on a config change
                    # is it ever safe to update options on the fly?
                    SchemeCls = SCHEME_CHOICES[fresh_scheme.lower()]

                    if old_scheme:
                        old_scheme.stop()

                    scheme = SchemeCls(strip, options=options)
                    old_scheme = scheme
                    asyncio.ensure_future(scheme.start())

                old_config = fresh_config

            if not options.isolate:
                fresh_config = await get_fresh_config(options)
            await asyncio.sleep(1)

    loop.run_until_complete(launch())  # loop until done


async def get_fresh_config(options):
    """Launch requests for all web pages."""
    options.servers
    tasks = []
    async with ClientSession() as session:
        for server in options.servers:

            task = asyncio.ensure_future(fetch(server, session))
            tasks.append(task)  # create list of tasks
        responses = await asyncio.gather(*tasks)  # gather task responses
    print(responses)
    if responses:
        # TODO this should be based on timestamp, not just the first one
        return responses.pop()

async def fetch(server, session):
    """Fetch a url, using specified ClientSession."""
    url = "http://%s/config" % server
    try:
        async with session.get(url) as response:
            resp = await response.read()
    except aiohttp.client_exceptions.ClientConnectorError:
        print("Can't find server at %s " % server)
        return None
    if not response.status == 200:
        return None

    return json.loads(resp)


if __name__ == '__main__':
    main()
