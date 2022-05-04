"""
Read/Write TLE data from:
a. satnog API
b. postgre Database
c. memcached
"""
import asyncio
import logging
from datetime import datetime
from typing import Dict

from src.python.database import dbUtils
from src.python.config import appConfig
from src.python.config.appConfig import memcached
from src.python.service import satnogsService


def getTwoLineElement() -> dict[str, dict[str, str | datetime]]:
    tleList: list[dict[str, str]] = satnogsService.tleFilter(
        satnogsService.sortMostRecent(
            satnogsService.getSatellite()))
    keys: list[str] = [twoLineElement['tle0'] for twoLineElement in tleList]
    return dict(zip(keys, tleList))


def isRecent(timestamp: datetime) -> bool:
    if timestamp is None:
        return False

    if not isinstance(timestamp, datetime):
        lastTimestamp: datetime = datetime.strptime(
            timestamp.decode("utf-8"), '%Y-%m-%d %H:%M:%S.%f')
    else:
        lastTimestamp: datetime = timestamp
    currentTimestamp: datetime = datetime.now()
    return (
                   currentTimestamp -
                   lastTimestamp).days == 0 and (
                   currentTimestamp -
                   lastTimestamp).seconds < 86400


def clearMemcache() -> None:
    memcached.flush_all()


def writeMemcache(data: dict) -> None:
    if not appConfig.enableMemcache:
        return

    memcached.set("two_line_element",
                  {key: dict(tle0=key,
                             tle1=data[key]['tle1'],
                             tle2=data[key]['tle2'],
                             updated=datetime.now()) for key in data.keys()})


async def readMemcache() -> dict[str, dict[str, str | datetime]]:
    if not appConfig.enableMemcache:
        return None

    twoLineElement: dict[str, dict[str, str | datetime]] | dict[None, None] = memcached.get("two_line_element",
                                                                                            default=dict())

    if twoLineElement:
        key: str = next(iter(twoLineElement.keys()))
        timestamp: datetime = twoLineElement[key]["updated"]
    else:
        return await readDatabase()

    if not isRecent(timestamp):
        logging.warning("WARNING: twoLineElement in memcached is outdated")
        return await readDatabase()

    logging.info("INFO: fetching twoLineElement from memcached")
    return twoLineElement


async def writeDatabase(data) -> None:
    if not appConfig.enableDB:
        return

    # psycopg.mogrify implementation
    # value = ",".join([f"(\'{key}\',\'{data[key]['tle1']}\',\'{data[key]['tle2']}\',\'{datetime.now()}\'::timestamp)"
    #                   for key in data.keys() if not "\'" in key])

    data: list[tuple[str, str, str, datetime]] = [
        (
            key,
            data[key]['tle1'],
            data[key]['tle2'],
            datetime.now()) for key in data.keys()]
    await dbUtils.asyncInsertAll("two_line_element", data)


async def readDatabase() -> dict[str, dict[str, str | datetime]]:
    if not appConfig.enableDB:
        return await writeTwoLineElement()

    timestamp: datetime | None
    timestamp, = dbUtils.fetch("getTimestamp")

    if not timestamp:
        return await writeTwoLineElement()

    if not isRecent(timestamp):
        logging.warning("WARNING: twoLineElement in heroku postgre database is outdated")
        return await writeTwoLineElement()

    dbData: None | tuple[str, str, str, datetime] | list[tuple[str, str, str, datetime]] \
        = await dbUtils.asyncFetchAll("getTwoLineElementAll", dict=True)
    data: dict[str, dict[str, str | datetime]] = dict(zip([twoLineElement['tle0'] for twoLineElement in dbData],
                                                          [dict(kv) for kv in dbData]))

    if data:
        writeMemcache(data)
        logging.info("INFO: fetching twoLineElement from heroku postgre database")
        return data

    return await writeTwoLineElement()


async def writeTwoLineElement() -> dict[str, dict[str, str | datetime]]:
    data: dict[str, dict[str, str | datetime]] = getTwoLineElement()

    if appConfig.enableMemcache:
        logging.info("INFO: writing to memcached")
        writeMemcache(data)

    if appConfig.enableDB:
        logging.info("INFO: writing to heroku postgre database")
        await writeDatabase(data)

    return data


async def readTwoLineElement() -> dict[str, dict[str, str | datetime]]:
    data: dict[str, dict[str, str | datetime]] = await readMemcache()
    return data if data else await readDatabase()


async def refreshTwoLineElement() -> dict[str, dict[str, str | datetime]]:
    if appConfig.enableMemcache:
        clearMemcache()
    if appConfig.enableDB:
        dbUtils.truncateTable("two_line_element")

    return await readTwoLineElement()


if __name__ == "__main__":
    async def runDatabaseFetch() -> None:
        print(await dbUtils.asyncFetchAll("getTwoLineElementAll", dict=True))

    async def runCoroutine() -> None:
        # clear cache && db
        clearMemcache()
        dbUtils.truncateTable("two_line_element")
        # change setting
        appConfig.enableDB = True
        appConfig.enableMemcache = True
        # test clear/read/write
        for _ in range(3):
            tle: dict[str, dict[str, str | datetime]] = await readTwoLineElement()
            print(tle, "\n", len(tle))

    asyncio.run(runCoroutine())
