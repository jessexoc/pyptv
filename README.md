# Disclamer
I am not affiliated with PTV. This in not an official API client.

# Getting started

## API KEY
Before you can make requests, you need to apply for an API key. This is done via email at this point in time.
You can follow this [link](mailto:APIKeyRequest@ptv.vic.gov.au ?Subject=PTV Timetable API - request for key&Body=Can%20I%20please%20get%20an%20API%20key%20for%20the%20PTV%20Timetable%20API%3F%0A%0ARegards%2C)

## Using the client

    >>> from pyptv import PTVClient
    >>> DEVELOPER_ID = "<your addigned developer id>"
    >>> API_KEY = "<your assigned api key>"
    >>> client = PTVClient(developer_id=DEVELOPER_ID, api_key=API_KEY)

## Check that everything is working

    >>> client.healthcheck()
    {u'securityTokenOK': True, u'clientClockOK': True, u'memcacheOK': True, u'databaseOK': True}

## Some examples
Let's say we want to find the next tram into the city from outside the Retreat Hotel in Brunswick.

Via some other method we determine that the latitude & longitude of the Retreat Hotel is: -37.771141, 144.961599

First fetch the stop

    >>> client.stops_nearby((-37.771141, 144.961599), mode='tram')
    [<TramStop: (2809) Glenlyon Rd/Sydney Rd #21 >,
     <TramStop: (2810) Brunswick Town Hall/Sydney Rd #21 >,
     <TramStop: (2808) Albert St/Sydney Rd #22 >,
     ...
     ]
    >>> this_stop = client.stops_nearby((-37.771141, 144.961599), mode='tram')[0]
    >>> this_stop
    <TramStop: (2809) Glenlyon Rd/Sydney Rd #21 >

Then look at the next upcoming departures from this stop:

    >>> this_stop.broad_next_departures(limit=3)
    [{'flags': None,
      'platform': <Platform: Glenlyon Rd/Sydney Rd #21>,
      'run': <TramRun: Flinders Street Railway Station/Elizabeth St #1>,
      'time_realtime_utc': datetime.datetime(2015, 6, 4, 5, 34, tzinfo=<DstTzInfo 'Australia/Melbourne' AEST+10:00:00 STD>),
      'time_timetable_utc': datetime.datetime(2015, 6, 4, 5, 34, tzinfo=<DstTzInfo 'Australia/Melbourne' AEST+10:00:00 STD>)},
     {'flags': None,
      'platform': <Platform: Glenlyon Rd/Sydney Rd #21>,
      'run': <TramRun: Flinders Street Railway Station/Elizabeth St #1>,
      'time_realtime_utc': datetime.datetime(2015, 6, 4, 5, 47, tzinfo=<DstTzInfo 'Australia/Melbourne' AEST+10:00:00 STD>),
      'time_timetable_utc': datetime.datetime(2015, 6, 4, 5, 47, tzinfo=<DstTzInfo 'Australia/Melbourne' AEST+10:00:00 STD>)},
     {'flags': None,
      'platform': <Platform: Glenlyon Rd/Sydney Rd #21>,
      'run': <TramRun: Flinders Street Railway Station/Elizabeth St #1>,
      'time_realtime_utc': datetime.datetime(2015, 6, 4, 6, 0, tzinfo=<DstTzInfo 'Australia/Melbourne' AEST+10:00:00 STD>),
      'time_timetable_utc': datetime.datetime(2015, 6, 4, 6, 0, tzinfo=<DstTzInfo 'Australia/Melbourne' AEST+10:00:00 STD>)}]

Let's say we missed this tram and so need to find bus stops nearby this one. All stops have a location, so can search for other stops nearby directly:

    >>> this_stop.stops_nearby(mode='bus', limit=5)
    [<BusStop: (25381) Sydney Rd/Glenlyon Rd >,
     <BusStop: (25380) 18 Dawson St >,
     <BusStop: (25663) Charles St/Glenlyon Rd >,
     <BusStop: (25382) Blair St/Glenlyon Rd >,
     <BusStop: (25379) Police Complex/20 Dawson St >]

TODO:

- More docs
- Multi-api-call convenience methods for common operations
