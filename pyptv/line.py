from pyptv.factory import TypeFactory


class Line(object):

    @property
    def transport_type(self):
        raise NotImplementedError

    def __repr__(self):

        return "<%s: %s>" % (self.__class__.__name__, self.line_name)

    def __init__(self, line_id, line_name, line_number):
        self.line_id = line_id
        self.line_name = line_name
        self.line_number = line_number

    def stops(self):

        return self._client.stops_on_a_line(mode=self.transport_type,
                                            line=self.line_id)


class TramLine(Line):
    transport_type = "tram"


class TrainLine(Line):
    transport_type = "train"


class BusLine(Line):
    transport_type = "bus"


class VlineLine(Line):
    transport_type = "vline"


class NightriderLine(Line):
    transport_type = "nightrider"


class LineFactory(TypeFactory):

    classes = {'train': TrainLine,
               'tram': TramLine,
               'bus': BusLine,
               'vline': VlineLine,
               'nightrider': NightriderLine,
               }
