from datetime import datetime

import pytz

AU_MEL = pytz.timezone('Australia/Melbourne')
UTC = pytz.timezone('UTC')


def parse_datetime_tz(raw):

    # '2015-01-11T16:41:11Z'
    dt = datetime.strptime(raw, "%Y-%m-%dT%H:%M:%SZ")

    dt_utc = UTC.localize(dt)

    dt_tz = dt_utc.astimezone(AU_MEL)

    return dt_tz
