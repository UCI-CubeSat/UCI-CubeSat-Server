"""
Read/Write TLE data from:
a. satnog API
b. postgre Database
c. memcache
"""

import ast
import logging
import subprocess
from datetime import datetime

from pymemcache.client import base

from src.python.database import dbUtils
from src.python.config import appConfig
from src.python.service import satnogsService

# config for memcache
client = base.Client(('localhost', 11211))


def getTwoLineElement() -> {dict}:
    tleList = satnogsService.tleFilter(
        satnogsService.sortMostRecent(
            satnogsService.getSatellite()))
    keys = [tle['tle0'] for tle in tleList]
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
    if not client.get("keySet") is None:
        keySet = ast.literal_eval((client.get("keySet")).decode("utf-8"))
        for key in keySet:
            client.set(key.replace(" ", "_"), None)

    client.set("currTime", None)
    client.set("keySet", None)
    client.flush_all()


def writeMemcache(data):
    if not appConfig.enableMemcache:
        return

    currTime = datetime.now()
    client.set("currTime", currTime)
    keySet = set(data.keys())
    client.set("keySet", keySet)
    for key in keySet:
        client.set(key.replace(" ", "_"), data[key])


def readMemcache():
    if not appConfig.enableMemcache:
        return None

    try:
        timestamp = client.get("currTime")
    except ConnectionRefusedError:
        timestamp = None
        subprocess.run(["brew", "services", "stop", "memcached"])
        subprocess.run(["brew", "install", "memcached"])
        subprocess.run(["brew", "services", "start", "memcached"])

    if timestamp is None:
        logging.warning("WARNING: cache miss")
        return None

    if not isRecent(timestamp):
        logging.warning("WARNING: cache outdated")
        return None

    logging.info("LOGGING: cache hit")
    data = {}
    keySet: list = ast.literal_eval((client.get("keySet")).decode("utf-8"))

    for key in keySet:
        value = client.get(key.replace(" ", "_")).decode(
            "utf-8")  # byte -> str
        # TODO:
        #  ast.literal_eval is crashing here, if appConfig.enableMemcache = True
        #  we keep track of when data is last fetch, db and memcache is using
        #  different way of storing that information
        #  memcache is using cache[currTime], while db is using tle[updated]
        #  tle[updated] is a datetime object:
        #  'updated': datetime.datetime(2022, 2, 23, 20, 11, 46, 245761)
        #  cache[currTime] is a string:
        #  2022-02-24 12:38:43.867728
        data[key] = ast.literal_eval(value)  # str -> dict
    return data


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


def readDatabase():
    if not appConfig.enableDB:
        return saveTwoLineElement()

    timestamp, = dbUtils.fetch("getTimestamp")

    if not timestamp:
        return saveTwoLineElement()

    if not isRecent(timestamp):
        logging.warning("WARNING: db outdated")
        return saveTwoLineElement()

    dbData: dict = dbUtils.fetchAll("getTwoLineElementAll", dict=True)
    data: dict = dict(zip([tle['tle0']
                           for tle in dbData], [dict(kv) for kv in dbData]))

    if data:
        writeMemcache(data)
        return data

    return saveTwoLineElement()


def saveTwoLineElement() -> {dict}:
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


def loadTwoLineElement() -> {dict}:
    data = readMemcache()
    return data if data else readDatabase()


def refreshTwoLineElement() -> {dict}:
    clearMemcache()
    dbUtils.truncateTable("two_line_element")

    return loadTwoLineElement()


if __name__ == "__main__":
    # clear cache && db
    clearMemcache()
    # dbUtils.truncateTable("two_line_element")
    # change setting
    appConfig.enableDB = True
    appConfig.enableMemcache = False
    # test db clear/read/write
    for _ in range(10):
        print(loadTwoLineElement())
