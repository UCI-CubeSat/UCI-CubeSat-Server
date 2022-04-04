import requests

KEY = "36ff1b885dafa497e93073092cdac1c9887e510c"
TRANSMITTER_URL = "https://db.satnogs.org/api/transmitters/?key=36ff1b885dafa497e93073092cdac1c9887e510c&format=json"
SATELLITE_URL = "https://db.satnogs.org/api/satellites/?key=36ff1b885dafa497e93073092cdac1c9887e510c&format=json"
TLE_URL = "https://db.satnogs.org/api/tle/?key=36ff1b885dafa497e93073092cdac1c9887e510c&format=json"


def getID() -> set:
    return {sat["norad_cat_id"] for sat in requests.get(SATELLITE_URL).json()}


def getSatellites() -> [dict]:
    """
    :return: A list of all available Satellite's basic info from Satnogs
    """
    sat = {s["norad_cat_id"]: s["name"] for s in requests.get(SATELLITE_URL).json()}

    return [{"name": sat[s["norad_cat_id"]], "description": s["description"],
             "norad_cat_id": s["norad_cat_id"],
             "service": s["service"], "mode": s["mode"],
             "baud": s["baud"], "time": s["updated"]}
            for s in requests.get(TRANSMITTER_URL).json() if s["alive"]]


def getTLE() -> {dict}:
    """
    :return: A list of all available Satellite's TLE from Satnogs
    """
    # get TLE response from api, TLE is used to calculate flight path
    return {tle["tle0"]: tle for tle in requests.get(TLE_URL).json()}


def satelliteFilter(satelliteList: [dict], mode: str = "AFSK", baud: int = 1200) -> [dict]:
    """
    filter the list of satellite by modulation mode and baud rate
    :param satelliteList: List of Satellite information from Satnogs
    :param mode: Modulation Type
    :param baud: Data Transfer Rate
    :return: List of Satellite information filtered
    """

    return [sat for sat in satelliteList if sat["mode"] is not None and mode in sat["mode"]
            and sat["baud"] is not None and baud == sat["baud"]]


def sortMostRecent(satelliteList: [dict], recent: bool = True) -> [dict]:
    """
    filter the list of satellite by modulation mode and baud rate
    :param satelliteList: List of Satellite information from Satnogs
    :param recent: True = Most recent first
    :return: List of Satellite information sorted
    """

    # sort the list of satellite by timestamp (last known communication)
    return [sat for sat in sorted(satelliteList, key=lambda x: x["time"], reverse=recent)
            if int(sat["time"][0:4]) >= 2021]


def getNoradID(satelliteList: [dict]) -> {str}:
    """
    get a set of NoradID from dict, using set to improve
    search performance from O(n) to O(1)
    :param satelliteList: List of Satellite information from Satnogs
    :return: Set of NoRadID in String format
    """

    return {sat["norad_cat_id"] for sat in satelliteList}


def tleFilter(satelliteList: [dict]) -> [dict]:
    """
    Push TLE information from Satnogs based on given NoRadID
    :param satelliteList: List of Satellite information from Satnogs
    :return: List of Satellite's TLE information from Satnogs
    """

    return [sat for sat in getTLE().values() if sat["norad_cat_id"] in getNoradID(satelliteList)]

