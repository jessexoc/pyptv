from pyptv.factory import TypeFactory

from pyptv.utils import parse_datetime_tz


class Disruption(object):

    def __repr__(self):

        max_len = 40

        if len(self.title) > (max_len - 3):
            title = self.title[:max_len - 3] + "..."
        else:
            title = self.title
        return "<%s: %s>" % (self.__class__.__name__, title)

    @property
    def mode(self):
        raise NotImplementedError

    def __init__(self, description, publishedOn, title, url):
        self.description = description
        self.publishedOn = parse_datetime_tz(publishedOn)
        self.title = title
        self.url = url


class GeneralDisruption(Disruption):
    mode = "general"


class MetroBusDisruption(Disruption):
    mode = "metro-bus"


class MetroTrainDisruption(Disruption):
    mode = "metro-train"


class MetroTramDisruption(Disruption):
    mode = "metro-tram"


class RegionalBusDisruption(Disruption):
    mode = "regional-bus"


class RegionalCoachDisruption(Disruption):
    mode = "regional-coach"


class RegionalTrainDisruption(Disruption):
    mode = "regional-train"


class DisruptionFactory(TypeFactory):

    classes = {"general": GeneralDisruption,
               "metro-bus": MetroBusDisruption,
               "metro-train": MetroTrainDisruption,
               "metro-tram": MetroTramDisruption,
               "regional-bus": RegionalBusDisruption,
               "regional-coach": RegionalCoachDisruption,
               "regional-train": RegionalTrainDisruption,
               }
