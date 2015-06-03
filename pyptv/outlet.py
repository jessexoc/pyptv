from pyptv.factory import TypeFactory
from pyptv.location import Location, LocationMixin


class Outlet(LocationMixin):

    @property
    def transport_type(self):
        raise NotImplementedError

    def __init__(self, lat, lon, location_name, suburb,
                 business_name, distance):
        self.location = Location(lat, lon)
        self.location_name = location_name
        self.subrub = suburb
        self.business_name = business_name

    def __repr__(self):
        return "<%s: %s>" % (self.__class__.__name__, self.business_name)


class RetailOutlet(Outlet):
    transport_type = "Retail"


class StopOutlet(Outlet):
    transport_type = "Stop"


class OutletFactory(TypeFactory):

    classes = {'Retail': RetailOutlet,
               'Stop': StopOutlet,
               }
