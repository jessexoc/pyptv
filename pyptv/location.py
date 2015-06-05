from math import sin, cos, sqrt, asin, atan2, radians, degrees


EARTH_RADIUS = 6373.0  # KM


class Location(object):

    def __init__(self, lat, lon):
        self.lat = lat
        self.lon = lon

    def __repr__(self):
        return "<Loc: (%s,%s)>" % (self.lat, self.lon)

    def google_maps(self, zoom=16):
        base_url = "http://www.google.com/maps/place/" + \
                   "{lat},{lon}/@{lat},{lon},{zoom}z"
        return base_url.format(lat=self.lat, lon=self.lon, zoom=zoom)

    def bing_maps(self, zoom=8):
        base_url = "http://bing.com/maps/default.aspx" + \
                   "?cp={lat}~{lon}&lvl={zoom}&style=r"
        return base_url.format(lat=self.lat, lon=self.lon, zoom=zoom)

    def openstreetmap(self, zoom=12):
        base_url = "http://www.openstreetmap.org/" + \
                   "?mlat={lat}&mlon={lon}&zoom={zoom}"
        return base_url.format(lat=self.lat, lon=self.lon, zoom=zoom)

    def distance(self, location):
        """ Calculate distance (in km) to another location """

        lat1, lon1 = parse_location(self)
        lat2, lon2 = parse_location(location)

        # calculation adapted from:
        # http://stackoverflow.com/questions/19412462/getting-distance-between-two-points-based-on-latitude-longitude-python

        rlat1 = radians(lat1)
        rlon1 = radians(lon1)
        rlat2 = radians(lat2)
        rlon2 = radians(lon2)

        dlon = rlon2 - rlon1
        dlat = rlat2 - rlat1

        a = sin(dlat / 2)**2 + cos(rlat1) * cos(rlat2) * sin(dlon / 2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))

        distance = EARTH_RADIUS * c

        return distance

    def location_delta(self, distance, bearing):
        """ calculate the location after traving {distance} on {bearing} from
        {start} locaiton.

        start: a Location object (latitude & longitude)
        distance: in km
        bearing: an angle in degrees

        formula for calcualtion adapted from:
        http://www.movable-type.co.uk/scripts/latlong.html
        """
        rlat1 = radians(self.lat)
        rlon1 = radians(self.lon)

        rbearing = radians(bearing)

        rlat2 = asin(sin(rlat1) * cos(distance/EARTH_RADIUS) +
                     cos(rlat1) * sin(distance/EARTH_RADIUS) * cos(rbearing))
        rlon2 = rlon1 + atan2(sin(rbearing) * sin(distance/EARTH_RADIUS) * cos(rlat1),
                              cos(distance/EARTH_RADIUS) - sin(rlat1) * sin(rlat2))

        lat2 = degrees(rlat2)
        lon2 = degrees(rlon2)

        return Location(lat2, lon2)


class LocationMixin(object):

    def stops_nearby(self, *args, **kwargs):
        """ transit stops that are nearby this location """
        return self._client.stops_nearby(self.location, *args, **kwargs)

    def poi_nearby(self, poi, radius, griddepth, limit=20, *args, **kwargs):
        """ Points of Interest that are within {radius} km of this one
        radius: defines the radius of a circle within a bounding square defined
            by two opposing corners
        """

        # since we want outside bounding box, rather than inside,
        # we need 2**0.5 * radius
        distance = 2**0.5 * radius

        north_west = self.location.location_delta(distance, 315)
        south_east = self.location.location_delta(distance, 135)

        return self._client.transport_pois_by_map(poi, north_west, south_east,
                                                  griddepth, limit,
                                                  *args, **kwargs)


def parse_location(location):
    """
    convert a provided location into a tuple of (latitude, longitude) from any
    of the supported forms:
    - a tuple of lat,lon
    - a Location object
    - an object that stores a Location object in its location attribute
    TODO:
    - a google maps point
    - a text street address
    """

    if isinstance(location, tuple) and len(location) == 2:
        return location

    if isinstance(location, Location):
        return (location.lat, location.lon)

    if hasattr('location', location):
        return location.location.lat, location.location.lon

    raise Exception("location is not a supported type")
