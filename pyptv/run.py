from pyptv.factory import TypeFactory


class Run(object):
    """
    A specific run on a particular line that may skip certan stops
    """

    @property
    def transport_type(self):
        raise NotImplementedError

    def __repr__(self):
        return "<%s: %s>" % (self.__class__.__name__, self.destination_name)

    def __init__(self, destination_id, destination_name, num_skipped, run_id):

        self.destination_id = destination_id
        self.destination_name = destination_name
        self.num_skipped = num_skipped
        self.run_id = run_id

    def stopping_pattern(self, stop, for_utc=None):
        from stop import Stop

        if isinstance(stop, Stop):
            stop_id = stop.stop_id
        else:
            stop_id = stop

        return self._client.stopping_pattern(mode=self.transport_type,
                                             run=self.run_id,
                                             stop=stop_id,
                                             for_utc=for_utc)


class TramRun(Run):
    transport_type = "tram"


class TrainRun(Run):
    transport_type = "train"


class BusRun(Run):
    transport_type = "bus"


class VlineRun(Run):
    transport_type = "vline"


class NightriderRun(Run):
    transport_type = "nightrider"


class RunFactory(TypeFactory):

    classes = {'train': TrainRun,
               'tram': TramRun,
               'bus': BusRun,
               'vline': VlineRun,
               'nightrider': NightriderRun,
               }
