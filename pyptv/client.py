#!/usr/bin/env python

from datetime import datetime
import hmac
from hashlib import sha1
import json
import urlparse  # TODO: remove in favour of better lib
import urllib

import requests

from pyptv.platform_ import Platform  # don't clobber the builtin platform
from pyptv.direction import Direction
from pyptv.stop import StopFactory
from pyptv.line import LineFactory
from pyptv.run import RunFactory
from pyptv.outlet import OutletFactory
from pyptv.disruption import DisruptionFactory
from pyptv.location import parse_location
from pyptv.utils import parse_datetime_tz


API_BASE_URL = "http://timetableapi.ptv.vic.gov.au/"


class PTVClient(object):
    MODES = {"train":      0,
             "tram":       1,
             "bus":        2,
             "vline":      3,
             "nightrider": 4,
             "ticket_outlet": 100,
             }

    FLAGS = {"RR": "Reservations Required",
             "GC": "Guaranteed Connection",
             "DOO": "Drop Off Only",
             "PUO": "Pick Up Only",
             "MO": "Mondays only",
             "TU": "Tuesdays only",
             "WE": "Wednesdays only",
             "TH": "Thursdays only",
             "FR": "Fridays only",
             "SS": "School days only",
             }

    def __init__(self, developer_id=None, api_key=None):

        self.developer_id = developer_id
        self.api_key = api_key

    def api_request(self, api_path, timed=True):
        """ Call some api end point
        API request will have proper signing key appended.
        """

        parsed = urlparse.urlparse(api_path)

        # parse out current query
        query = urlparse.parse_qsl(parsed.query)

        # add timestamp
        if timed:
            now = datetime.utcnow().replace(microsecond=0).isoformat() + 'Z'
            query.append(('timestamp', now))

        # add developer id
        query.append(('devid', self.developer_id))

        unsigned_query = urllib.urlencode(query)
        unsigned_parsed = parsed._replace(query=unsigned_query)

        unsigned_path = unsigned_parsed.geturl()

        digest = hmac.new(self.api_key, unsigned_path, sha1)

        signature = digest.hexdigest()

        query.append(('signature', signature))
        signed_query = urllib.urlencode(query)
        signed_parsed = unsigned_parsed._replace(query=signed_query)

        signed_path = signed_parsed.geturl()

        signed_url = urlparse.urljoin(API_BASE_URL, signed_path)

        req = requests.get(signed_url)

        data = json.loads(req.content)

        return data

    # API methods:

    def healthcheck(self):
        """ send off a health check to check the status of the system, the
        local clock and the API credentials.
        """
        return self.api_request("/v2/healthcheck")

    def stops_nearby(self, location, mode=None, limit=None, with_distance=False):
        """ Get stops near a location.
        location: one of (lat, lon), a Location object, or something that has a
            location property (which would be a Location object)
        mode: (optional) filter results for only this tramsport mode
        limit: (optional) only return this many results
        with_distance: (optional) return tuples of (Stop, distance)
        """

        lat, lon = parse_location(location)

        base_path = "/v2/nearme/latitude/{lat}/longitude/{lon}"

        path = base_path.format(lat=lat, lon=lon)

        stops = self.api_request(path)

        stop_factory = StopFactory(self)

        out = [stop_factory.create(**stop['result']) for stop in stops]

        # only provide certain stop types if we are provided with a mode
        if mode is not None:
            out = [stop for stop in out if stop.transport_type == mode]
        
        # enforce limit if provided
        if limit is not None:
            out = out[:limit]

        # convert into tuple of (Stop, distance)
        if with_distance:
            out = [(stop, location.distance(stop.location)) for stop in out]

        return out

    def transport_pois_by_map(self, poi, location1,
                              location2, griddepth, limit=20):
        """ list of points of interest within a map grid defined by location1
        & location2
        poi: either a transport mode or outlet. A list of poi types can be
            passed in as a comma separated
        location1 & location2:
            - are one of (lat, lon), a Location object, or something that has a
              location property (which would be a Location object).
            - define the top left corner (location1) and bottom right corner
              (location2) of a rectangle on a map
        griddepth: number of cell blocks per cluster
        limit: minimum number of POIs required to create a cluster as well as
            the maximum number of POIs returned
        """

        lat1, lon1 = parse_location(location1)
        lat2, lon2 = parse_location(location2)

        base_path = "/v2/poi/{poi}/lat1/{lat1}/long1/{lon1}/" + \
                    "lat2/{lat2}/long2/{lon2}/" + \
                    "griddepth/{griddepth}/limit/{limit}"

        poi_ids = ','.join([str(self.MODES[p]) for p in poi.split(',')])

        path = base_path.format(poi=poi_ids, lat1=lat1, lon1=lon1,
                                lat2=lat2, lon2=lon2,
                                griddepth=griddepth, limit=limit)

        data = self.api_request(path)

        stop_factory = StopFactory(self)
        outlet_factory = OutletFactory(self)

        out = {}
        for k, v in data.items():
            if k == "locations":
                out['locations'] = []
                for location in v:
                    # either a Stop of an Outlet
                    if 'transport_type' in location:
                        item = stop_factory.create(**location)
                    else:
                        outlet_type = location.pop('outlet_type')
                        item = outlet_factory.create(transport_type=outlet_type,
                                                     **location)
                    out['locations'].append(item)
            else:
                out[k] = v

        return out

    def search(self, term):
        """ all stops and lines that match the search term
        """

        path = "/v2/search/%s" % urllib.quote(term)

        data = self.api_request(path)

        stop_factory = StopFactory(self)
        line_factory = LineFactory(self)

        out = []
        for result in data:
            if result['type'] == 'stop':
                out.append(stop_factory.create(**result['result']))
            elif result['type'] == 'line':
                out.append(line_factory.create(**result['result']))
            else:
                out.append(result)

        return out

    def lines_by_mode(self, mode, name=None):
        """ all the lines for a particular transport mode """
        base_path = "/v2/lines/mode/{mode}"

        mode_id = self.MODES[mode]

        path = base_path.format(mode=mode_id)

        if name is not None:
            path += "?name=%s" % name

        data = self.api_request(path)

        line_factory = LineFactory(self)

        out = []
        for line in data:
            out.append(line_factory.create(**line))

        return out

    def stops_on_a_line(self, mode, line):
        """ all the stops for a particular transport mode on a given line
        mode: transport mode
        line: the line_id of a particular line
        """

        base_path = "/v2/mode/{mode}/line/{line}/stops-for-line"

        mode_id = self.MODES[mode]

        path = base_path.format(mode=mode_id, line=line)

        data = self.api_request(path)

        stop_factory = StopFactory(self)

        out = []
        for line in data:
            out.append(stop_factory.create(**line))

        return out

    def _process_departures(self, departures):
        """ common reponse parser for handling a list of departures """

        line_factory = LineFactory(self)
        stop_factory = StopFactory(self)
        run_factory = RunFactory(self)

        out = []
        for departure in departures:
            # - platform
            # -- direction
            # --- line
            platform_details = departure['platform']
            direction_details = platform_details.pop('direction')
            line_details = direction_details.pop('line')
            line = line_factory.create(**line_details)
            direction_details['line'] = line
            direction = Direction(**direction_details)
            platform_details['direction'] = direction
            # --- stop
            stop_details = platform_details.pop('stop')
            stop = stop_factory.create(**stop_details)
            platform_details['stop'] = stop
            platform = Platform(**platform_details)
            # - run
            run_details = departure['run']
            run = run_factory.create(**run_details)

            timetable = parse_datetime_tz(departure["time_timetable_utc"])
            if departure["time_realtime_utc"] is not None:
                realtime = parse_datetime_tz(departure["time_realtime_utc"])
            else:
                realtime = None

            if departure['flags']:
                flags = ', '.join([self.FLAGS[f] for f
                                   in departure['flags'].split('-')
                                   if f != 'E'])
            else:
                flags = None

            out.append({"platform": platform,
                        "run": run,
                        "flags": flags,
                        "time_timetable_utc": timetable,
                        "time_realtime_utc": realtime,
                        })
        return out

    def broad_next_departures(self, mode, stop, limit=5):
        """ departure times at a particular stop, irrespective of line or
        direction.
        mode: transport mode
        stop: stop_id of a stop
        limit: max results to return
        """

        base_path = "/v2/mode/{mode}/stop/{stop}/" + \
                    "departures/by-destination/limit/{limit}"
        mode_id = self.MODES[mode]
        path = base_path.format(mode=mode_id, stop=stop, limit=limit)
        departures = self.api_request(path)

        return self._process_departures(departures["values"])

    def specific_next_departures(self, mode, line, stop,
                                 direction, limit=5, for_utc=None):
        """ departure times at a particular stop for a given line and direction
        mode: transport mode
        line: line_id of transport line
        stop: stop_id of a stop on the line
        direction: direction_id of run's direction
        limit: max results to return
        for_utc: (optional) date and time of the request
        """

        base_path = "/v2/mode/{mode}/line/{line}/stop/{stop}/" + \
                    "directionid/{direction}/departures/all/limit/{limit}"

        mode_id = self.MODES[mode]

        path = base_path.format(mode=mode_id, line=line, stop=stop,
                                direction=direction, limit=limit)

        if for_utc is not None:
            path += "?for_utc=%s" % for_utc

        departures = self.api_request(path)

        return self._process_departures(departures["values"])

    def specific_next_departures_gtfs(self, mode, route_id, stop, direction,
                                      for_utc=None):
        """ TODO: explain how this differs from previous method """

        base_path = "/v2/mode/{mode}/route_id/{route_id}/stop/{stop}/" + \
                    "direction/{direction}/departures/all/limit/{limit}"

        path = base_path.format(mode=mode, route_id=route_id, stop=stop,
                                direction=direction)

        if for_utc is not None:
            path += "?for_utc=%s" % for_utc

        departures = self.api_request(path)

        return self._process_departures(departures["values"])


    def stopping_pattern(self, mode, run, stop, for_utc=None):
        """ stopping pattern for a particular run from a given stop
        mode: transport mode
        run: transport run_id
        stop: stop_id of a stop
        for_utc: (optional) date and time of the request
        """

        base_path = "/v2/mode/{mode}/run/{run}/stop/{stop}/stopping-pattern"
        mode_id = self.MODES[mode]
        path = base_path.format(mode=mode_id, run=run, stop=stop)

        if for_utc is not None:
            path += "?for_utc=%s" % for_utc

        data = self.api_request(path)

        return self._process_departures(data['values'])

    def disruptions(self, modes="general"):
        """ planned and unplanned disruptions on the transport network.
        modes: one or more of the following in a comma separted string format:
            general
            metro-bus
            metro-train
            metro-tram
            regional-bus
            regional-coach
            regional-train
        """

        path = "/v2/disruptions/modes/%s" % modes

        data = self.api_request(path)

        factory = DisruptionFactory(self)

        out = []
        for mode, items in data.items():
            for item in items:
                out.append(factory.create(transport_type=mode, **item))
        return out
