from datetime import datetime
import flask
import requests
from flask import request, Response, Blueprint
from requests import Response
from skyfield.toposlib import wgs84
import urllib
import time

from src.python.config import appConfig
from src.python.service import bingMapService, skyfieldService, satnogsService, tleService


serverRoute: Blueprint = Blueprint('server', __name__)


@serverRoute.route(f'/', methods=['GET'])
def getIndex():
    return flask.jsonify({
        "Name": "UCI CubeSat Flask Server",
        "Github": "https://github.com/UCI-CubeSat/UCI-CubeSat-Server",
        "Endpoint": {"GET": [
            f"{flask.request.host_url}api/v1/heartbeat",
            f"{flask.request.host_url}api/v1/tle",
            f"{flask.request.host_url}api/v1/states",
            f"{flask.request.host_url}api/v1/prediction",
            f"{flask.request.host_url}api/v1/available_satellite",
            f"{flask.request.host_url}api/v1/websocket",
        ]}
    })


@serverRoute.route(f'{appConfig.apiBaseUrl}/heartbeat', methods=['GET'])
def getServerStatus():
    satnogsRequest: Response = requests.get(satnogsService.TLE_URL)
    dbRequest: dict[str, dict[str, str | datetime]] = tleService.readTwoLineElement()
    try:
        response: Response = flask.jsonify({
            "status": "online",
            "satnogs": {
                "status": "online" if satnogsRequest.status_code == 200 else "offline"
            },
            "database": {
                "status": "online" if len(dbRequest) != 0 else "offline",
                "length": len(dbRequest),
                "updated": dbRequest[list(dbRequest.keys())[0]]["updated"]
            }
        })
    except Exception as error:
        response = flask.jsonify(
            {"status": str(f"{str(type(error))}: {error}")})

    return response


@serverRoute.route(f'{appConfig.apiBaseUrl}/tle', methods=['GET'])
def getTwoLineElement():
    refresh: str = request.args.get("refresh", default="false", type=str)
    return flask.jsonify(tleService.refreshTwoLineElement()) if refresh.lower() == "true" \
        else flask.jsonify(tleService.readTwoLineElement())


@serverRoute.route(f'{appConfig.apiBaseUrl}/geocoding', methods=['POST'])
def getLatLong():
    addressLine = request.get_json().get('address')
    city = request.get_json().get('city')
    postalCode = request.get_json().get('postalCode')
    country = request.get_json().get('country')
    adminDistrict = request.get_json().get('adminDistrict')

    return flask.jsonify(
        bingMapService.getLatLong(
            addressLine,
            city,
            adminDistrict,
            postalCode,
            country)[0])


@serverRoute.route(f'{appConfig.apiBaseUrl}/available_satellite', methods=['GET'])
def getAvailableSatellite():
    return flask.jsonify(list(tleService.readTwoLineElement().keys()))


@serverRoute.route(f'{appConfig.apiBaseUrl}/states', methods=['GET'])
def getSatelliteState():
    name: str = request.args.get("name", default="AmicalSat", type=str).upper()
    duration: float = request.args.get("duration", default=3600.0, type=float)
    data: dict[str, dict[str, str | datetime]] = tleService.readTwoLineElement()

    try:
        satellite_tle: dict[str, str | datetime] = data[name] if name in data.keys(
        ) else data[f'0 {name}']
    except KeyError:
        return flask.jsonify({})

    response: dict[str, object] = skyfieldService.getSphericalPath(
        satellite_tle, duration, 60.0 / 60.0)
    currLatLng: tuple[float, float] = response["origin"]
    currLatPath: list[float] = response["latArray"]
    currLngPath: list[float] = response["lngArray"]
    currLatLngPath: list[tuple[float, float]] = response["latLngArray"]
    return flask.jsonify({"latLng": {"lat": currLatLng[0], "lng": currLatLng[1]},
                          "latPath": list(currLatPath),
                          "lngPath": list(currLngPath),
                          "latLngPath": currLatLngPath
                          })


@serverRoute.route(f'{appConfig.apiBaseUrl}/prediction', methods=['GET'])
def getHorizon():
    satellite: str = urllib.parse.unquote(
        request.args.get(
            "satellite",
            default="",
            type=str))
    latitude: float | None = request.args.get("latitude", type=float)
    longitude: float | None = request.args.get("longitude", type=float)
    elevation: int = request.args.get("elevation", default=0, type=int)
    duration: float = request.args.get(
        "duration",
        default=1 * 24 * 3600.0,
        type=float)

    if satellite == "" or not (longitude and longitude):
        return flask.jsonify({})

    return flask.jsonify(skyfieldService.findHorizonTime(
        tleService.readTwoLineElement()[satellite], duration, wgs84.latlon(
            latitude, longitude, elevation_m=elevation)))


@serverRoute.route(f'{appConfig.apiBaseUrl}/emailSignup', methods=['POST'])
def postEmailSubscriber():
    # TODO: integrate with React.js frontend /src/components/emailSignup.js
    pass


@serverRoute.route(f'{appConfig.apiBaseUrl}/serverMetric', methods=['GET'])
def getServerMetric():
    duration: float = request.args.get("duration", default=3600.0 * 24, type=float)

    t: float = time.perf_counter()
    kvSet: dict[str, dict[str, str | datetime]] = tleService.readTwoLineElement()
    initialLoadTime: float = time.perf_counter() - t
    keySet: list = kvSet.keys()
    t = time.perf_counter()
    for satellite in keySet:
        _ = skyfieldService.findHorizonTime(
            kvSet[satellite], duration, wgs84.latlon(
                33.6405, -117.8443, elevation_m=0))

    calculationTime: float = time.perf_counter() - t

    return flask.jsonify({
        "Initial Load Cost:": initialLoadTime,
        "Prediction Calculation Cost:": calculationTime,
        "Prediction Calculation Size:": {
            "Duration": duration // 3600,
            "Number of Satellite:": len(keySet)
        }
    })
