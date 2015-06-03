
class Platform(object):

    def __repr__(self):
        return "<Platform: %s>" % self.stop.location_name

    def __init__(self, direction, stop, realtime_id):
        self.direction = direction
        self.stop = stop
        self.realtime_id = realtime_id

    def specific_next_departures(self, for_utc=None):
        line_id = self.direction.line.line_id
        direction_id = self.direction.direction_id
        return self.stop.specific_next_departures(line_id, direction_id,
                                                  for_utc=None)
