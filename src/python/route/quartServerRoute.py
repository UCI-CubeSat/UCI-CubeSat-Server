import logging
from datetime import datetime
import quart
from quart import request, Response, Blueprint
from requests import Response
from skyfield.toposlib import wgs84
import urllib
import time
import aiohttp

from src.python.config.appConfig import apiBaseUrl
from src.python.service import (
    bingMapService,
    skyfieldService,
    satnogsService,
    tleService,
)
from src.python.util.asyncUtil import asyncRequest


serverRoute: Blueprint = Blueprint("server", __name__)


@serverRoute.route(f"/", methods=["GET"])
async def getIndex():
    return quart.jsonify(
        {
            "Name": "UCI CubeSat Backend Server",
            "Github": "https://github.com/UCI-CubeSat/UCI-CubeSat-Server",
            "Endpoint": {
                "GET": [
                    f"{quart.request.host_url}api/v1/heartbeat",
                    f"{quart.request.host_url}api/v1/tle",
                    f"{quart.request.host_url}api/v1/states",
                    f"{quart.request.host_url}api/v1/prediction",
                    f"{quart.request.host_url}api/v1/available_satellite",
                    f"{quart.request.host_url}api/v1/ws_message?message=HELLO",
                ]
            },
        }
    )


@serverRoute.route(f"{apiBaseUrl}/heartbeat", methods=["GET"])
async def getServerStatus():
    try:
        async with aiohttp.ClientSession() as session:
            data: dict[str, dict[str, str | datetime]] = await asyncRequest(
                session, satnogsService.TLE_URL
            )
    except Exception as asyncError:
        data = dict()
        logging.WARNING(f"{asyncError}")
    dbRequest: dict[
        str, dict[str, str | datetime]
    ] = await tleService.readTwoLineElement()
    try:
        response: Response = quart.jsonify(
            {
                "status": "online",
                "satnogs": {"status": "online" if data else "offline"},
                "database": {
                    "status": "online" if len(dbRequest) != 0 else "offline",
                    "length": len(dbRequest),
                    "updated": dbRequest[list(dbRequest.keys())[0]]["updated"],
                },
            }
        )
    except Exception as error:
        response = quart.jsonify({"status": str(f"{str(type(error))}: {error}")})

    return response


@serverRoute.route(f"{apiBaseUrl}/tle", methods=["GET"])
async def getTwoLineElement():
    refresh: str = request.args.get("refresh", default="false", type=str)
    return (
        quart.jsonify(await tleService.refreshTwoLineElement())
        if refresh.lower() == "true"
        else quart.jsonify(await tleService.readTwoLineElement())
    )


@serverRoute.route(f"{apiBaseUrl}/geocoding", methods=["POST"])
async def getLatLong():
    addressLine = request.get_json().get("address")
    city = request.get_json().get("city")
    postalCode = request.get_json().get("postalCode")
    country = request.get_json().get("country")
    adminDistrict = request.get_json().get("adminDistrict")

    return quart.jsonify(
        bingMapService.getLatLong(
            addressLine, city, adminDistrict, postalCode, country
        )[0]
    )


@serverRoute.route(f"{apiBaseUrl}/available_satellite", methods=["GET"])
async def getAvailableSatellite():
    return quart.jsonify(list((await tleService.readTwoLineElement()).keys()))


@serverRoute.route(f"{apiBaseUrl}/states", methods=["GET"])
async def getSatelliteState():
    name: str = request.args.get("name", default="AmicalSat", type=str).upper()
    duration: float = request.args.get("duration", default=3600.0, type=float)
    data: dict[str, dict[str, str | datetime]] = await tleService.readTwoLineElement()

    try:
        satellite_tle: dict[str, str | datetime] = (
            data[name] if name in data.keys() else data[f"0 {name}"]
        )
    except KeyError:
        return quart.jsonify({})

    response: dict[str, object] = skyfieldService.getSphericalPath(
        satellite_tle, duration, 60.0 / 60.0
    )
    currLatLng: tuple[float, float] = response["origin"]
    currLatPath: list[float] = response["latArray"]
    currLngPath: list[float] = response["lngArray"]
    currLatLngPath: list[tuple[float, float]] = response["latLngArray"]
    return quart.jsonify(
        {
            "latLng": {"lat": currLatLng[0], "lng": currLatLng[1]},
            "latPath": list(currLatPath),
            "lngPath": list(currLngPath),
            "latLngPath": currLatLngPath,
        }
    )


@serverRoute.route(f"{apiBaseUrl}/prediction", methods=["GET"])
async def getHorizon():
    satellite: str = urllib.parse.unquote(
        request.args.get("satellite", default="", type=str)
    )
    latitude: float | None = request.args.get("latitude", type=float)
    longitude: float | None = request.args.get("longitude", type=float)
    elevation: int = request.args.get("elevation", default=0, type=int)
    duration: float = request.args.get("duration", default=1 * 24 * 3600.0, type=float)

    if satellite == "" or not (longitude and longitude):
        return quart.jsonify({})

    return quart.jsonify(
        skyfieldService.findHorizonTime(
            (await tleService.readTwoLineElement())[satellite],
            duration,
            wgs84.latlon(latitude, longitude, elevation_m=elevation),
        )
    )


@serverRoute.route(f"{apiBaseUrl}/emailSignup", methods=["POST"])
async def postEmailSubscriber():
    # TODO: integrate with React.js frontend /src/components/emailSignup.js
    pass


@serverRoute.route(f"{apiBaseUrl}/serverMetric", methods=["GET"])
async def getServerMetric():
    duration: float = request.args.get("duration", default=3600.0 * 24, type=float)

    t: float = time.perf_counter()
    kvSet: dict[str, dict[str, str | datetime]] = await tleService.readTwoLineElement()
    initialLoadTime: float = time.perf_counter() - t
    keySet: list = kvSet.keys()
    t = time.perf_counter()
    for satellite in keySet:
        _ = skyfieldService.findHorizonTime(
            kvSet[satellite], duration, wgs84.latlon(33.6405, -117.8443, elevation_m=0)
        )

    calculationTime: float = time.perf_counter() - t

    return quart.jsonify(
        {
            "Initial Load Cost:": initialLoadTime,
            "Prediction Calculation Cost:": calculationTime,
            "Prediction Calculation Size:": {
                "Duration": duration // 3600,
                "Number of Satellite:": len(keySet),
            },
        }
    )
