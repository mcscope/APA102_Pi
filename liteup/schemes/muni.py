import requests
import xml.etree.ElementTree as ET
from collections import namedtuple
from itertools import tee
import time
from liteup.schemes.scheme import Scheme

Coord = namedtuple('Coord', ['lat', 'lon'])


class Route:
    def __init__(self, color, tag, directions):
        self.color = color
        self.tag = tag
        self.directions = directions


class Stop:
    def __init__(self, tag, title, coord):
        self.tag = tag
        self.title = title
        self.coord = coord


class Direction:
    def __init__(self, tag, name, stops):
        self.name = name
        self.tag = tag
        self.stops = stops


Vehicle = namedtuple('Vehicle', ["id", "route_tag", "dir_tag", "coord"])


def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    # from itertools recipe
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)


def calc_distance(from_loc, to_loc):
    from_coord = from_loc.coord
    to_coord = to_loc.coord
    distance_squared = pow(from_coord.lat - to_coord.lat, 2) + pow(from_coord.lon - to_coord.lon, 2)
    return pow(distance_squared, 0.5)


class Muni(Scheme):
    PAUSE_BETWEEN_PAINTS = 10.0
    ROUTE_TAGS = ["14", "14X", "14R", "12", "KT", "J", "N", "F"]

    def init(self):
        self.routes = {tag: NextBusApi.get_route(tag) for tag in self.ROUTE_TAGS}
        self.vehicles, self.last_poll = NextBusApi.get_vehicles()

    def paint(self):
        self.setall([0, 0, 0, 0])
        new_poll_times = []
        for tag in self.ROUTE_TAGS:
            updated_vehicles, new_poll_time = NextBusApi.get_vehicles(tag, since=self.last_poll)
            new_poll_times.append(new_poll_time)
            self.vehicles.update(updated_vehicles)
            self.paint_route(self.routes[tag])
        self.last_poll = min(new_poll_times) - 1  # query for the oldest
        # move start point to the side of the window
        self.strip.rotate(-166)
        return True

    def paint_route(self, route):

        bookmark_led = 0
        for direction in route.directions.values():
            dir_vehicles = [v for v in self.vehicles.values()
                            if route.tag == v.route_tag and direction.tag == v.dir_tag]
            distances = [0] + [calc_distance(*pair) for pair in pairwise(direction.stops)]
            total_distance = sum(distances)
            unit = total_distance / (self.strip.num_leds / 2)

            stop_lights = {}
            for distance, stop in zip(distances, direction.stops):
                dist_in_leds = int(distance / unit)
                bookmark_led += dist_in_leds
                bookmark_led = min(self.strip.num_leds - 1, bookmark_led)

                # Don't want to overwrite a vehicle location with a stop.
                # Stops often serve multiple vehicles
                if self.strip.get_pixel(bookmark_led)[3] < 10:
                    self.strip.set_pixel_rgb(bookmark_led, route.color, 1, gamma=True)
                stop_lights[stop.tag] = bookmark_led

            for v in dir_vehicles:
                stop_distances = {calc_distance(v, stop): stop for stop in direction.stops}
                closest_stop = stop_distances[min(stop_distances.keys())]
                # stop_nieghbors =
                vehicle_light = stop_lights[closest_stop.tag]
                self.strip.set_pixel_rgb(vehicle_light, route.color, 100, gamma=True)


class NextBusApi:

    @classmethod
    def get_route(cls, route_tag="N"):
        url = "http://webservices.nextbus.com/service/publicXMLFeed?command=routeConfig&a=sf-muni&r=%s" % route_tag
        resp = requests.get(url)
        # TODO error handling
        root = ET.fromstring(resp.content)
        x_route = root[0]
        all_stops = {}
        directions = {}

        for x_stop in x_route.findall('stop'):
            new_stop = Stop(
                tag=x_stop.get("tag"),
                title=x_stop.get("title"),
                coord=Coord(float(x_stop.get("lat")),
                            float(x_stop.get("lon"))),
            )
            all_stops[new_stop.tag] = new_stop
        for x_direction in x_route.findall('direction'):
            dir_stops = []
            for x_stop in x_direction:
                stop_tag = x_stop.get("tag")
                dir_stops.append(all_stops[stop_tag])

            new_dir = Direction(
                name=x_direction.get('name'),
                tag=x_direction.get('tag'),
                stops=dir_stops
            )
            directions[new_dir.tag] = new_dir

        route_color = int("0x%s" % x_route.get('color'), 16)
        route = Route(color=route_color,
                      tag=x_route.get("tag"),
                      directions=directions)
        return route

    @classmethod
    def get_vehicles(cls, route_tag=None, since=None):
        # TODO -timing?
        url = "http://webservices.nextbus.com/service/publicXMLFeed?command=vehicleLocations&a=sf-muni"
        if since:
            url += "&t=%s" % since
        if route_tag:
            url += "&r=%s" % route_tag

        resp = requests.get(url)
        # TODO error handling
        root = ET.fromstring(resp.content)
        vehicles = {}
        for x_vehicle in root.findall('vehicle'):
            coord = Coord(float(x_vehicle.get("lat")),
                          float(x_vehicle.get("lon")))
            new_vehicle = Vehicle(
                id=x_vehicle.get("id"),
                route_tag=x_vehicle.get("routeTag"),
                dir_tag=x_vehicle.get("dirTag"),
                coord=coord,
            )
            vehicles[new_vehicle.id] = new_vehicle

        lastTime = int(root.find('lastTime').get('time'))
        return vehicles, lastTime

#  http://webservices.nextbus.com/service/publicXMLFeed?command=vehicleLoc
# # ations&a=sf-muni&r=N&t=1144953500233
#     <body>
#       <vehicle id="1453" routeTag="N" dirTag="out" lat="37.7664199" lon="-
# 122.44896" secsSinceReport="29" predictable="true" heading="276"/>
#     </body>
# http://webservices.nextbus.com/service/publicXMLFeed?command=routeList&a=sf-muni
#
#     <body>
#       <route tag="1" title="1 - California" shortTitle="1-Calif/>
#       <route tag="3" title="3 - Jackson" shortTitle="3-Jacksn"/>
#       <route tag="4" title="4 - Sutter" shortTitle="4-Sutter"/>
#       <route tag="5" title="5 - Fulton" shortTitle="5-Fulton"/>
#       <route tag="6" title="6 - Parnassus" shortTitle="6-Parnas"/>
#       <route tag="7" title="7 - Haight" shortTitle="7-Haight"/>
#       <route tag="14" title="14 - Mission" shortTitle="14-Missn"/>
#       <route tag="21" title="21 - Hayes" shortTitle="21-Hayes"/>
# </body>


# http://webservices.nextbus.com/service/publicXMLFeed?command=vehicleLoc
# ations&a=sf-muni&r=N&t=1144953500233
#     <body>
#       <vehicle id="1453" routeTag="N" dirTag="out" lat="37.7664199" lon="-
# 122.44896" secsSinceReport="29" predictable="true" heading="276"/>
#     </body>

# http://webservices.nextbus.com/service/publicXMLFeed?command=routeConfig&a=sf-muni&r=N
#
# <route tag="N" title="N - Judah" color="003399" oppositeColor="ffffff" latMin="37.7601699" latMax="37.7932299" lonMin="-122.5092" lonMax="-122.38798">
 # <stop tag="KINGd4S0" title="King St and 4th St" shortTitle="King & 4th" lat="37.776036" lon="-122.394355" stopId="1"/>
# <stop tag="KINGd2S0" title="King St and 2nd St" shortTitle="King & 2nd" lat="37.7796152" lon="-122.3898067" stopId="2"/>
# <stop tag="EMBRBRAN" title="Embarcadero and Brannan St" shortTitle="Embarcadero & Brannan" lat="37.7844455" lon="-122.3880081" stopId="3"/>
# <stop tag="EMBRFOLS" title="Embarcadero and Folsom St" shortTitle="Embarcadero & Folsom" lat="37.7905742" lon="-122.3896326" stopId="4"/>
# ...
#          <direction tag="out" title="Outbound to La Playa" name=”Outbound”
# useForUI="true">
#           <stop tag="KINGd4S0"/>
#           <stop tag="KINGd2S0"/>
#           <stop tag="EMBRBRAN"/>
#           <stop tag="EMBRFOLS"/>
#           <stop tag="CVCENTF"/>
# </direction>
#          <direction tag="in" title="Inbound to Caltrain" name=”Inbound”
# useForUI="true">
#           <stop tag="CVCENTF"/>
#           <stop tag="EMBRFOLS"/>
#           <stop tag="EMBRBRAN"/>
#           <stop tag="KINGd2S0"/>
#           <stop tag="KINGd4S0"/>
# </direction>
#          <direction tag="in_short" title="Short Run" name=”Inbound”
# useForUI="false">
#           <stop tag="CVCENTF"/>
#           <stop tag="EMBRFOLS"/>
#           <stop tag="EMBRBRAN"/>
#          </direction>
#          ...
#          <path>
#           <point lat="37.7695171" lon="-122.4287571"/>
#           <point lat="37.7695099" lon="-122.42887"/>
#          </path>
#          <path>
# <point lat="37.77551" lon="-122.39513"/> <point lat="37.77449" lon="-122.39642"/> <point lat="37.77413" lon="-122.39687"/> <point lat="37.77385" lon="-122.39721"/> <point lat="37.7737399" lon="-122.39734"/> <point lat="37.77366" lon="-122.39744"/> <point lat="37.77358" lon="-122.39754"/> <point lat="37.77346" lon="-122.39766"/> <point lat="37.77338" lon="-122.39772"/> <point lat="37.77329" lon="-122.39778"/> <point lat="37.77317" lon="-122.39784"/>
#         </path>
#         <path>
# <point lat="37.76025" lon="-122.50927"/> <point lat="37.76023" lon="-122.50928"/> <point lat="37.76017" lon="-122.50928"/> <point lat="37.7601299" lon="-122.50927"/> <point lat="37.76008" lon="-122.50924"/>
# </path>
# ... </route>
# </body>
