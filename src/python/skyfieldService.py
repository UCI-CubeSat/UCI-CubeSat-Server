import json
import numpy
from skyfield.toposlib import wgs84
from skyfield.api import EarthSatellite, load
from skyfield.timelib import Time


def selectSat(tle: dict, name: str) -> dict:
    if name not in tle.keys():
        return dict()

    return tle[name]


def getPath(data: dict, mode: str = "latlong", duration: float = 10 * 3600, resolution: float = 4.0) -> dict:
    if mode == "latlong":
        return getSphericalPath(data, duration, resolution)
    if mode == "xyz":
        return getCartesianPath(data, duration, resolution)
    return getSphericalPath(data, duration, resolution)


def getSphericalPath(data: dict, duration: float, resolution: float) -> dict:
    response = dict()
    satellite = EarthSatellite(data["tle1"], data["tle2"], data["tle0"], load.timescale())
    ts = load.timescale()
    t = ts.now()
    start = t.utc.second

    interval = ts.utc(t.utc.year, t.utc.month, t.utc.day, t.utc.hour, t.utc.minute,
                      numpy.arange(start, start + duration, resolution * 60))
    location = satellite.at(interval)
    path = wgs84.subpoint(location)

    response["timestamp"] = t.utc
    response["identifier"] = data["tle0"]
    response["origin"] = (wgs84.subpoint(satellite.at(t)).latitude.degrees,
                          wgs84.subpoint(satellite.at(t)).longitude.degrees)
    response["latArray"] = path.latitude.degrees
    response["longArray"] = path.longitude.degrees
    response["elevationArray"] = path.elevation.au
    response["interval"] = interval

    return response


def getCartesianPath(data, duration, resolution):
    response = dict()
    satellite = EarthSatellite(data["tle1"], data["tle2"], data["tle0"], load.timescale())
    ts = load.timescale()
    t = ts.now()
    start = t.utc.second

    interval = ts.utc(t.utc.year, t.utc.month, t.utc.day, t.utc.hour, t.utc.minute,
                      numpy.arange(start, start + duration, resolution * 60))
    location = satellite.at(interval)
    d = numpy.array([])

    for i in range(len(location.position.km[0])):
        numpy.append(d, (numpy.linalg.norm(numpy.array(
            [location.position.km[0][i], location.position.km[1][i], location.position.km[2][i]])
                                           - numpy.array([0, 0, 0]))))

    response["identifier"] = data["tle0"]
    response["x"] = location.position.km[0]
    response["y"] = location.position.km[1]
    response["z"] = location.position.km[2]
    response["d"] = d  # euclidean distance
    response["interval"] = interval

    return response


def getSerializedPath(data: dict):
    for k in data.keys():
        if str(type(data[k])) == "<class 'numpy.ndarray'>":
            data[k] = data[k].tolist()
        else:
            data[k] = str(data[k])

    return data


def findHorizonTime(data, duration, receiverLocation: wgs84.latlon) -> json:
    satellite = EarthSatellite(data["tle1"], data["tle2"], data["tle0"], load.timescale())
    ts = load.timescale()
    start = load.timescale().now()

    end = ts.utc(start.utc.year, start.utc.month, start.utc.day, start.utc.hour, start.utc.minute,
                 start.utc.second + duration)
    condition = {"bare": 1.0, "marginal": 25.0, "good": 50.0, "excellent": 75.0}
    degree = condition["bare"]  # peak is at 90
    t_utc, events = satellite.find_events(receiverLocation, start, end, altitude_degrees=degree)

    if not numpy.array_equal(events[:1], [0]):
        start = ts.utc(start.utc.year, start.utc.month, start.utc.day, start.utc.hour, start.utc.minute,
                       start.utc.second - 15 * 60)
        t_utc, events = satellite.find_events(receiverLocation, start, end, altitude_degrees=degree)

    if not numpy.array_equal(events[-1:], [2]):
        end = ts.utc(start.utc.year, start.utc.month, start.utc.day, start.utc.hour, start.utc.minute,
                     start.utc.second + duration + 15 * 60)
        t_utc, events = satellite.find_events(receiverLocation, start, end, altitude_degrees=degree)
    t_utc = list(t_utc)

    if events.size == 0:
        pass
    elif events.size == 1:
        events = numpy.array([])
    elif events.size == 2:  # [0,1], [1,2], [2,0]
        if numpy.array_equal(events, [0, 1]):
            events = numpy.append(events, 2)
            t_utc.append(t_utc[-1])
        elif numpy.array_equal(events, [1, 2]):
            events = numpy.insert(events, 0, 0)
            t_utc = numpy.insert(t_utc, 0, t_utc[0])
        elif numpy.array_equal(events, [2, 0]):
            events = numpy.array([])
            t_utc = numpy.array([])
    else:
        if not numpy.array_equal(events[:1], [0]):
            # startswith 1 [1,2,0,1,2,0] ==> [1,1,2,0,1,2,0]
            if events[0] == 1:
                events = numpy.insert(events, 0, 0)
                t_utc.insert(0, t_utc[0])
            # startswith 2 ==> delete
            elif events[0] == 2:
                events = numpy.delete(events, 0)
                t_utc.pop(0)

        if not numpy.array_equal(events[-1:], [2]):  # [1,1,2,0,1,2,0,1]
            # endswith 1 ==> 0,1 ==> []
            if events[-1] == 1:
                events = numpy.append(events, 2)
                t_utc.append(t_utc[-1])
            # endswith 0 ==> delete
            elif events[-1] == 0:
                events = numpy.delete(events, -1)
                t_utc.pop(-1)

    # what if events contains multiple 1s?
    removed_index = []
    for i in range(1, events.size - 1):
        previous = events[i - 1]
        if events[i] == previous:
            removed_index.append(i)
    formattedEvents = []
    formattedTimeStamps = []
    for i in range(events.size):
        if i not in removed_index:
            formattedEvents.append(events[i])
            formattedTimeStamps.append(t_utc[i])

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

    retDict = {}
    retJson = {}
    for index in range(0, len(formattedEvents), 3):
        try:
            formattedTimeStamps[index + 2]
        except IndexError:
            raise IndexError
        else:
            datetime_rise = Time.utc_datetime(formattedTimeStamps[index])
            datetime_peak = Time.utc_datetime(formattedTimeStamps[index + 1])
            datetime_set = Time.utc_datetime(formattedTimeStamps[index + 2])
            t0 = ts.utc(datetime_rise.year, datetime_rise.month, datetime_rise.day, datetime_rise.hour,
                        datetime_rise.minute, datetime_rise.second)

            diff = numpy.float64((datetime_set - datetime_rise).total_seconds())
            t0_sec = t0.utc.second
            t1_sec = t0_sec + diff
            eventDuration = ts.utc(t0.utc.year, t0.utc.month, t0.utc.day, t0.utc.hour, t0.utc.minute,
                                   numpy.arange(t0_sec, t1_sec, 60))
            eventTimeArray = eventDuration.utc_strftime('%Y %b %d %H:%M:%S')

            retJson[str(datetime_peak)] = json.dumps({'rise': str(eventTimeArray[0]),
                                                      'set': str(eventTimeArray[-1]),
                                                      'duration': len(eventTimeArray),
                                                      'interval': str(eventDuration)}, indent=4)

            retDict[str(datetime_peak)] = {'rise': str(eventTimeArray[0]),
                                           'set': str(eventTimeArray[-1]),
                                           'duration': len(eventTimeArray),
                                           'interval': str(eventDuration)}

    return json.dumps(retJson, indent=4), retDict
