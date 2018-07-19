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
    loop = asyncio.get_event_loop()  # event loop

    async def launch():
        # this is the supervisor loop

        old_scheme = None
        old_config = None
        config = parse_options()

        Stripcls = ImageStrip if config.save_image else APA102
        strip = Stripcls(num_leds=config.num_leds,
                         order="RGB",
                         max_speed_hz=4000000)
        # Supposed to be 8k but
        # we get flicker at the end if I set that
        while True:
            if config and config != old_config:
                # we have a new config. We may need to change schemes
                # or just update the current one

                if not old_config or config.scheme != old_config.scheme:
                    # we need to change schemes
                    SchemeCls = SCHEME_CHOICES[config.scheme.lower()]

                    if old_scheme:
                        old_scheme.stop()

                    scheme = SchemeCls(strip, options=config)
                    old_scheme = scheme
                    asyncio.ensure_future(scheme.start())
                else:
                    scheme.on_new_options(config)

                old_config = config

            if not config.isolate:
                new_config = await get_config(config)
                if new_config:
                    config = new_config
            await asyncio.sleep(1)
    loop.run_until_complete(launch())  # loop until done


async def get_config(config):
    """Launch requests for all web pages."""
    tasks = []
    async with ClientSession() as session:
        for server in config.servers:

            task = asyncio.ensure_future(fetch(server, session))
            tasks.append(task)  # create list of tasks
        responses = await asyncio.gather(*tasks)  # gather task responses
    print(responses)
    if responses:
        # TODO this should be based on timestamp of change,
        # not just the first one receieved
        # so if two servers, the most recently edited one wins.
        first_response = responses.pop()
        if not first_response:
            return None
        config = parse_options(first_response)
        return config


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
