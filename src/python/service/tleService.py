"""
Read/Write TLE data from:
a. satnog API
b. postgre Database
c. memcached
"""
import logging
import time
from datetime import datetime

from src.python.database import dbUtils
from src.python.config import appConfig
from src.python.config.appConfig import memcached
from src.python.service import satnogsService


def getTwoLineElement() -> {dict}:
    tleList = satnogsService.tleFilter(
        satnogsService.sortMostRecent(
            satnogsService.getSatellite()))
    keys = [twoLineElement['tle0'] for twoLineElement in tleList]
    return dict(zip(keys, tleList))


def isRecent(timestamp: datetime) -> bool:
    if timestamp is None:
        return False

    if not isinstance(timestamp, datetime):
        lastTimestamp = datetime.strptime(
            timestamp.decode("utf-8"), '%Y-%m-%d %H:%M:%S.%f')
    else:
        lastTimestamp = timestamp
    currentTimestamp: datetime = datetime.now()
    return (
        currentTimestamp -
        lastTimestamp).days == 0 and (
        currentTimestamp -
        lastTimestamp).seconds < 86400


def clearMemcache():
    memcached.flush_all()


def writeMemcache(data: dict):
    if not appConfig.enableMemcache:
        return

    memcached.set("two_line_element",
                  {key: dict(tle0=key,
                             tle1=data[key]['tle1'],
                             tle2=data[key]['tle2'],
                             updated=datetime.now()) for key in data.keys()})


def readMemcache() -> {dict}:
    if not appConfig.enableMemcache:
        return None

    twoLineElement: dict = memcached.get("two_line_element", default=dict())

    if twoLineElement:
        key = next(iter(twoLineElement.keys()))
        timestamp = twoLineElement[key]["updated"]
    else:
        return readDatabase()

    if not isRecent(timestamp):
        logging.warning("WARNING: mc outdated")
        return readDatabase()

    logging.warning("INFO: reading from mc")
    return twoLineElement


def writeDatabase(data):
    if not appConfig.enableDB:
        return

    # psycopg.mogrify implementation
    # value = ",".join([f"(\'{key}\',\'{data[key]['tle1']}\',\'{data[key]['tle2']}\',\'{datetime.now()}\'::timestamp)"
    #                   for key in data.keys() if not "\'" in key])

    data: list = [
        (
            key,
            data[key]['tle1'],
            data[key]['tle2'],
            datetime.now()) for key in data.keys()]
    dbUtils.insertAll("two_line_element", data)


def readDatabase() -> {dict}:
    if not appConfig.enableDB:
        return writeTwoLineElement()

    timestamp, = dbUtils.fetch("getTimestamp")

    if not timestamp:
        return writeTwoLineElement()

    if not isRecent(timestamp):
        logging.warning("WARNING: db outdated")
        return writeTwoLineElement()

    dbData: dict = dbUtils.fetchAll("getTwoLineElementAll", dict=True)
    data: dict = dict(zip([twoLineElement['tle0'] for twoLineElement in dbData], [
                      dict(kv) for kv in dbData]))

    if data:
        writeMemcache(data)
        logging.warning("INFO: reading from db")
        return data

    return writeTwoLineElement()


def writeTwoLineElement() -> {dict}:
    data = getTwoLineElement()

    if appConfig.enableMemcache:
        logging.info("LOGGING: writing to cache")
        writeMemcache(data)
        logging.info("LOGGING: done writing to cache")

    if appConfig.enableDB:
        logging.info("LOGGING: writing to db")
        writeDatabase(data)
        logging.info("LOGGING: done writing to db")

    return data


def readTwoLineElement() -> {dict}:
    data = readMemcache()
    return data if data else readDatabase()


def refreshTwoLineElement() -> {dict}:
    if appConfig.enableMemcache:
        clearMemcache()
    if appConfig.enableDB:
        dbUtils.truncateTable("two_line_element")

    return readTwoLineElement()


if __name__ == "__main__":
    # # test reading from memcached -> 0.5 sec
    # t = time.perf_counter()
    # twoLineElement = memcached.get("two_line_element")
    # print(twoLineElement)
    # print(time.perf_counter() - t)
    #
    # # test reading from memcached -> 2 sec
    # t = time.perf_counter()
    # twoLineElement = readDatabase()
    # print(twoLineElement)
    # print(time.perf_counter() - t)

    # clear cache && db
    clearMemcache()
    dbUtils.truncateTable("two_line_element")
    # change setting
    appConfig.enableDB = True
    appConfig.enableMemcache = True
    # test db clear/read/write
    for _ in range(3):
        tle = readTwoLineElement()
        print(tle, len(tle))
