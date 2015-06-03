from pyptv.factory import TypeFactory
from pyptv.location import Location

from pyptv.location import LocationMixin


class Stop(LocationMixin):

    @property
    def transport_type(self):
        raise NotImplementedError

    def __init__(self, lat, lon, location_name, stop_id, suburb, distance):
        self.location = Location(lat, lon)
        self.location_name = location_name
        self.stop_id = stop_id
        self.subrub = suburb

    def __repr__(self):
        return "<%s: (%s) %s>" % (self.__class__.__name__, self.stop_id,
                                  self.location_name)

    def broad_next_departures(self, limit=5):
        """ next departures for this stop """

        return self._client.broad_next_departures(mode=self.transport_type,
                                                  stop=self.stop_id,
                                                  limit=limit)

    def specific_next_departures(self, line, direction, limit=5, for_utc=None):

        return self._client.specific_next_departures(mode=self.transport_type,
                                                     line=line,
                                                     stop=self.stop_id,
                                                     direction=direction,
                                                     limit=limit,
                                                     for_utc=for_utc)


class TramStop(Stop):
    transport_type = "tram"


class TrainStop(Stop):
    transport_type = "train"


class BusStop(Stop):
    transport_type = "bus"


class VlineStop(Stop):
    transport_type = "vline"


class NightriderStop(Stop):
    transport_type = "nightrider"


class StopFactory(TypeFactory):

    classes = {'train': TrainStop,
               'tram': TramStop,
               'bus': BusStop,
               'vline': VlineStop,
               'nightrider': NightriderStop,
               }
