from datetime import datetime
import quart
from quart import request, Blueprint
from quart_cors import cors
from skyfield.toposlib import wgs84
import urllib

from src.python.config.appConfig import apiBaseUrl
from src.python.service import (
    bingMapService,
    skyfieldService,
    tleService,
)

trackerRoute: Blueprint = Blueprint("tracker", __name__)
cors(trackerRoute)


@trackerRoute.route(f"{apiBaseUrl}/tle", methods=["GET"])
async def getTwoLineElement():
    refresh: str = request.args.get("refresh", default="false", type=str)
    return (
        quart.jsonify(await tleService.refreshTwoLineElement())
        if refresh.lower() == "true"
        else quart.jsonify(await tleService.readTwoLineElement())
    )


@trackerRoute.route(f"{apiBaseUrl}/geocoding", methods=["POST"])
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


@trackerRoute.route(f"{apiBaseUrl}/available_satellite", methods=["GET"])
async def getAvailableSatellite():
    return quart.jsonify(list((await tleService.readTwoLineElement()).keys()))


@trackerRoute.route(f"{apiBaseUrl}/states", methods=["GET"])
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


@trackerRoute.route(f"{apiBaseUrl}/prediction", methods=["GET"])
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
