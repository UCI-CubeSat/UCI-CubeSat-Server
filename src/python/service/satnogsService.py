"""
Fetch TLE data from satnog API
"""

import requests
from src.python.config import appConfig

TRANSMITTER_URL: str = f"https://db.satnogs.org/api/transmitters/?key={appConfig.satnogsApiKey}&format=json"
SATELLITE_URL: str = (
    f"https://db.satnogs.org/api/satellites/?key={appConfig.satnogsApiKey}&format=json"
)
TLE_URL: str = (
    f"https://db.satnogs.org/api/tle/?key={appConfig.satnogsApiKey}&format=json"
)


def getIdentifier() -> set[str]:
    return {sat["norad_cat_id"] for sat in requests.get(SATELLITE_URL).json()}


def getSatellite() -> list[dict[str, str]]:
    """
    :return: A list of all available Satellite's basic info from Satnogs
    """
    sat: dict[str, str] = {
        s["norad_cat_id"]: s["name"] for s in requests.get(SATELLITE_URL).json()
    }

    return [
        {
            "name": sat[s["norad_cat_id"]],
            "description": s["description"],
            "norad_cat_id": s["norad_cat_id"],
            "service": s["service"],
            "mode": s["mode"],
            "baud": s["baud"],
            "time": s["updated"],
        }
        for s in requests.get(TRANSMITTER_URL).json()
        if s["alive"]
    ]


def getTwoLineElement() -> dict[str, dict[str, str]]:
    """
    :return: A list of all available Satellite's TLE from Satnogs
    """
    # get TLE response from api, TLE is used to calculate flight path
    return {tle["tle0"]: tle for tle in requests.get(TLE_URL).json()}


def satelliteFilter(
    satelliteList: list[dict[str, str]],
    mode: str = "AFSK",
    baud: int = 1200,
) -> list[dict[str, str]]:
    """
    filter the list of satellite by modulation mode and baud rate
    :param satelliteList: List of Satellite information from Satnogs
    :param mode: Modulation Type
    :param baud: Data Transfer Rate
    :return: List of Satellite information filtered
    """

    return [
        sat
        for sat in satelliteList
        if sat["mode"] is not None
        and mode in sat["mode"]
        and sat["baud"] is not None
        and baud == sat["baud"]
    ]


def sortMostRecent(
    satelliteList: list[dict[str, str]], recent: bool = True
) -> list[dict[str, str]]:
    """
    filter the list of satellite by modulation mode and baud rate
    :param satelliteList: List of Satellite information from Satnogs
    :param recent: True = Most recent first
    :return: List of Satellite information sorted
    """

    # sort the list of satellite by timestamp (last known communication)
    return [
        sat
        for sat in sorted(satelliteList, key=lambda x: x["time"], reverse=recent)
        if int(sat["time"][0:4]) >= 2021
    ]


def getNoradId(satelliteList: list[dict[str, str]]) -> set[str]:
    """
    get a set of NoradID from dict, using set to improve
    search performance from O(n) to O(1)
    :param satelliteList: List of Satellite information from Satnogs
    :return: Set of NoRadID in String format
    """

    return {sat["norad_cat_id"] for sat in satelliteList}


def tleFilter(satelliteList: list[dict[str, str]]) -> list[dict[str, str]]:
    """
    Push TLE information from Satnogs based on given NoRadID
    :param satelliteList: List of Satellite information from Satnogs
    :return: List of Satellite's TLE information from Satnogs
    """

    return [
        sat
        for sat in getTwoLineElement().values()
        if sat["norad_cat_id"] in getNoradId(satelliteList)
    ]


if __name__ == "__main__":
    pass
