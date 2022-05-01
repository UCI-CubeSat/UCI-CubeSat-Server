import flask
import requests
from flask import request
from skyfield.toposlib import wgs84
import urllib
import time

from src.python.config import appConfig
from src.python.service import bingMapService, skyfieldService, satnogsService, tleService
from src.python.config.appConfig import flaskServer, flaskWebSocket


@flaskServer.route(f'/', methods=['GET'])
def getHomePage():
    return flask.jsonify({
        "Name": "UCI CubeSat Flask Server",
        "Github": "https://github.com/UCI-CubeSat/UCI-CubeSat-Server",
        "Endpoint": {"GET": [
            f"{flask.request.host_url}api/v1/heartbeat",
            f"{flask.request.host_url}api/v1/tle",
            f"{flask.request.host_url}api/v1/states",
            f"{flask.request.host_url}api/v1/prediction",
            f"{flask.request.host_url}api/v1/available_satellite",
        ]}
    })


@flaskServer.route(f'{appConfig.apiBaseUrl}/heartbeat', methods=['GET'])
def getServerStatus():
    satnogsRequest = requests.get(satnogsService.TLE_URL)
    dbRequest: dict = tleService.readTwoLineElement()
    try:
        response = flask.jsonify({
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


@flaskServer.route(f'{appConfig.apiBaseUrl}/tle', methods=['GET'])
def getTwoLineElement():
    refresh = request.args.get("refresh", default="false", type=str)
    return flask.jsonify(tleService.refreshTwoLineElement()) if refresh.lower() == "true" \
        else flask.jsonify(tleService.readTwoLineElement())


@flaskServer.route(f'{appConfig.apiBaseUrl}/geocoding', methods=['POST'])
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


@flaskServer.route(f'{appConfig.apiBaseUrl}/available_satellite', methods=['GET'])
def getAvailableSatellite():
    return flask.jsonify(list(tleService.readTwoLineElement().keys()))


@flaskServer.route(f'{appConfig.apiBaseUrl}/states', methods=['GET'])
def getSatelliteState():
    name = request.args.get("name", default="AmicalSat", type=str).upper()
    duration = request.args.get("duration", default=3600.0, type=float)
    data = tleService.readTwoLineElement()

    try:
        satellite_tle = data[name] if name in data.keys(
        ) else data[f'0 {name}']
    except KeyError:
        return flask.jsonify({})

    response = skyfieldService.getSphericalPath(
        satellite_tle, duration, 60.0 / 60.0)
    currLatLng: tuple = response["origin"]
    currLatPath: list = response["latArray"]
    currLngPath: list = response["lngArray"]
    currLatLngPath: list = response["latLngArray"]
    return flask.jsonify({"latLng": {"lat": currLatLng[0], "lng": currLatLng[1]},
                          "latPath": list(currLatPath),
                          "lngPath": list(currLngPath),
                          "latLngPath": currLatLngPath
                          })


@flaskServer.route(f'{appConfig.apiBaseUrl}/prediction', methods=['GET'])
def getHorizon():
    satellite = urllib.parse.unquote(
        request.args.get(
            "satellite",
            default="",
            type=str))
    latitude = request.args.get("latitude", type=float)
    longitude = request.args.get("longitude", type=float)
    elevation = request.args.get("elevation", default=0, type=int)
    duration = request.args.get(
        "duration",
        default=1 * 24 * 3600.0,
        type=float)

    if satellite == "" or not (longitude and longitude):
        return flask.jsonify({})

    return flask.jsonify(skyfieldService.findHorizonTime(
        tleService.readTwoLineElement()[satellite], duration, wgs84.latlon(
            latitude, longitude, elevation_m=elevation)))


@flaskServer.route(f'{appConfig.apiBaseUrl}/emailSignup', methods=['POST'])
def addEmailSubscriber():
    # TODO: integrate with React.js frontend /src/components/emailSignup.js
    pass


@flaskServer.route(f'{appConfig.apiBaseUrl}/serverMetric', methods=['GET'])
def serverMetric():
    duration = request.args.get("duration", default=3600.0 * 24, type=float)

    t = time.perf_counter()
    kvSet = tleService.readTwoLineElement()
    initialLoadTime = time.perf_counter() - t
    keySet: list = kvSet.keys()
    t = time.perf_counter()
    for satellite in keySet:
        _ = skyfieldService.findHorizonTime(
            kvSet[satellite], duration, wgs84.latlon(
                33.6405, -117.8443, elevation_m=0))

    calculationTime = time.perf_counter() - t

    return flask.jsonify({
        "Initial Load Cost:": initialLoadTime,
        "Prediction Calculation Cost:": calculationTime,
        "Prediction Calculation Size:": {
            "Duration": duration // 3600,
            "Number of Satellite:": len(keySet)
        }
    })


if __name__ == '__main__':
    flaskWebSocket.run(flaskServer)
