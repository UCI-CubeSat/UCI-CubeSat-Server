import collections
import datetime
import json
import numpy
from skyfield.toposlib import wgs84
from skyfield.api import EarthSatellite, load
from skyfield.timelib import Time


def selectSat(tle: dict, name: str) -> dict:
    if name not in tle.keys():
        return {}

    return tle[name]


def getPath(
        data: dict,
        mode: str = "latLng",
        duration: float = 10 * 3600,
        resolution: float = 4.0) -> dict:
    return getSphericalPath(data, duration, resolution) if mode == "latLng" \
        else getCartesianPath(data, duration, resolution)


def getSphericalPath(data: dict, duration: float, resolution: float) -> dict:
    response = {}
    satellite = EarthSatellite(
        data["tle1"],
        data["tle2"],
        data["tle0"],
        load.timescale())
    ts = load.timescale()
    t = ts.now()
    start = t.utc.second

    interval = ts.utc(
        t.utc.year,
        t.utc.month,
        t.utc.day,
        t.utc.hour,
        t.utc.minute,
        numpy.arange(
            start,
            start +
            duration,
            resolution *
            60))
    location = satellite.at(interval)
    path = wgs84.subpoint(location)

    response["timestamp"]: datetime.time = t.utc
    response["identifier"]: str = data["tle0"]
    response["origin"]: tuple = (
        wgs84.subpoint(
            satellite.at(t)).latitude.degrees, wgs84.subpoint(
            satellite.at(t)).longitude.degrees)
    response["latArray"]: numpy.array = path.latitude.degrees
    response["lngArray"]: numpy.array = path.longitude.degrees
    response["latLngArray"]: list = [[response["latArray"][index], response["lngArray"][index]]
                                     for index in range(len(response["latArray"]))]
    response["elevationArray"]: numpy.array = path.elevation.au
    response["interval"]: datetime.time = interval

    return response


def getCartesianPath(data, duration, resolution):
    response = {}
    satellite = EarthSatellite(
        data["tle1"],
        data["tle2"],
        data["tle0"],
        load.timescale())
    ts = load.timescale()
    t = ts.now()
    start = t.utc.second

    interval = ts.utc(
        t.utc.year,
        t.utc.month,
        t.utc.day,
        t.utc.hour,
        t.utc.minute,
        numpy.arange(
            start,
            start +
            duration,
            resolution *
            60))
    location = satellite.at(interval)
    d = numpy.array([])

    for i in range(len(location.position.km[0])):
        numpy.append(d,
                     (numpy.linalg.norm(numpy.array([location.position.km[0][i],
                                                     location.position.km[1][i],
                                                     location.position.km[2][i]]) - numpy.array([0,
                                                                                                 0,
                                                                                                 0]))))

    response["identifier"]: str = data["tle0"]
    response["x"]: numpy.array = location.position.km[0]
    response["y"]: numpy.array = location.position.km[1]
    response["z"]: numpy.array = location.position.km[2]
    response["d"]: numpy.array = d  # euclidean distance
    response["interval"]: datetime.time = interval

    return response


def getSerializedPath(data: dict):
    for k in data.keys():
        if str(type(data[k])) == "<class 'numpy.ndarray'>":
            data[k] = data[k].tolist()
        else:
            data[k] = str(data[k])

    return data


def findHorizonTime(
        data: list,
        duration: float,
        receiverLocation: wgs84.latlon) -> json:
    satellite = EarthSatellite(
        data["tle1"],
        data["tle2"],
        data["tle0"],
        load.timescale())
    timestamp = load.timescale()
    start = load.timescale().now()

    end = timestamp.utc(
        start.utc.year,
        start.utc.month,
        start.utc.day,
        start.utc.hour,
        start.utc.minute,
        start.utc.second +
        duration)
    condition = {
        "bare": 1.0,
        "marginal": 30.0,
        "good": 45.0,
        "excellent": 60.0}
    degree = condition["bare"]  # peak is at 90
    timestampUtc, events = satellite.find_events(
        receiverLocation, start, end, altitude_degrees=degree)

    if not numpy.array_equal(events[:1], [0]):
        start = timestamp.utc(
            start.utc.year,
            start.utc.month,
            start.utc.day,
            start.utc.hour,
            start.utc.minute,
            start.utc.second - 15 * 60)
        timestampUtc, events = satellite.find_events(
            receiverLocation, start, end, altitude_degrees=degree)

    if not numpy.array_equal(events[-1:], [2]):
        end = timestamp.utc(
            start.utc.year,
            start.utc.month,
            start.utc.day,
            start.utc.hour,
            start.utc.minute,
            start.utc.second +
            duration +
            15 *
            60)
        timestampUtc, events = satellite.find_events(
            receiverLocation, start, end, altitude_degrees=degree)
    timestampUtc = list(timestampUtc)

    if events.size == 0:
        pass
    elif events.size == 1:
        events = numpy.array([])
    elif events.size == 2:  # [0,1], [1,2], [2,0]
        if numpy.array_equal(events, [0, 1]):
            events = numpy.append(events, 2)
            timestampUtc.append(timestampUtc[-1])
        elif numpy.array_equal(events, [1, 2]):
            events = numpy.insert(events, 0, 0)
            timestampUtc = numpy.insert(timestampUtc, 0, timestampUtc[0])
        elif numpy.array_equal(events, [2, 0]):
            events = numpy.array([])
            timestampUtc = numpy.array([])
    else:
        if not numpy.array_equal(events[:1], [0]):
            # startswith 1 [1,2,0,1,2,0] ==> [1,1,2,0,1,2,0]
            if events[0] == 1:
                events = numpy.insert(events, 0, 0)
                timestampUtc.insert(0, timestampUtc[0])
            # startswith 2 ==> delete
            elif events[0] == 2:
                events = numpy.delete(events, 0)
                timestampUtc.pop(0)

        if not numpy.array_equal(events[-1:], [2]):  # [1,1,2,0,1,2,0,1]
            # endswith 1 ==> 0,1 ==> []
            if events[-1] == 1:
                events = numpy.append(events, 2)
                timestampUtc.append(timestampUtc[-1])
            # endswith 0 ==> delete
            elif events[-1] == 0:
                events = numpy.delete(events, -1)
                timestampUtc.pop(-1)

    # what if events contains multiple 1s?
    removedIndex = []
    for i in range(1, events.size - 1):
        previous = events[i - 1]
        if events[i] == previous:
            removedIndex.append(i)
    formattedEvents = []
    formattedTimeStamps = []
    for i in range(events.size):
        if i not in removedIndex:
            formattedEvents.append(events[i])
            formattedTimeStamps.append(timestampUtc[i])

    # FOR DEBUG
    # SEE HOW IT NORMALLY ALWAYS HAVE [riseabove, culminate, setbelow]
    # print(start.utc_strftime('%Y %b %d %H:%M:%S'), "-", end.utc_strftime('%Y %b %d %H:%M:%S'))
    # for ti, event in zip(t_utc, events):
    #     name = (f'rise above {degree}°', 'culminate', f'set below {degree}°')[event]
    #     print(f'{ti.utc_strftime("%Y %b %d %H:%M:%S")} {name}', end="")
    #     if "set below" in name:
    #         print("")
    #     else:
    #         print(", ", end="")
    # END DEBUG

    response = collections.OrderedDict()
    for index in range(0, len(formattedEvents), 3):
        try:
            formattedTimeStamps[index + 2]
        except IndexError:
            raise IndexError
        else:
            datetime_rise = Time.utc_datetime(formattedTimeStamps[index])
            datetime_peak = Time.utc_datetime(formattedTimeStamps[index + 1])
            datetime_set = Time.utc_datetime(formattedTimeStamps[index + 2])
            t0 = timestamp.utc(
                datetime_rise.year,
                datetime_rise.month,
                datetime_rise.day,
                datetime_rise.hour,
                datetime_rise.minute,
                datetime_rise.second)

            diff = numpy.float64(
                (datetime_set - datetime_rise).total_seconds())
            t0Sec = t0.utc.second
            t1Sec = t0Sec + diff
            eventDuration = timestamp.utc(
                t0.utc.year,
                t0.utc.month,
                t0.utc.day,
                t0.utc.hour,
                t0.utc.minute,
                numpy.arange(
                    t0Sec,
                    t1Sec,
                    60))
            skyfieldTimeFormat = "%Y %b %d %H:%M:%S"
            eventTimeArray = eventDuration.utc_strftime(skyfieldTimeFormat)

            riseUtc = datetime.datetime.strptime(
                eventTimeArray[0], skyfieldTimeFormat).replace(
                tzinfo=datetime.timezone.utc)
            setUtc = datetime.datetime.strptime(
                eventTimeArray[-1], skyfieldTimeFormat).replace(tzinfo=datetime.timezone.utc)
            peakUtc = datetime_peak
            riseIso = riseUtc.isoformat(sep='T', timespec='auto')
            setIso = setUtc.isoformat(sep='T', timespec='auto')
            peakIso = peakUtc.isoformat(sep='T', timespec='auto')
            eventInterval = [(datetime.datetime.strptime(e, skyfieldTimeFormat)
                              .replace(tzinfo=datetime.timezone.utc))
                             .isoformat(sep='T', timespec='auto')
                             for e in eventTimeArray]

            response[peakIso] = dict(
                rise=riseIso,
                set=setIso,
                duration=len(eventTimeArray),
                interval=eventInterval)

    return response
