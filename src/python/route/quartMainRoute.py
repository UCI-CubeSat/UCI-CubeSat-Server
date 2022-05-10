import logging
from datetime import datetime
import quart
from quart import request, Response, Blueprint
from quart_cors import cors
from requests import Response
from skyfield.toposlib import wgs84
import time
import aiohttp

from src.python.config.appConfig import apiBaseUrl
from src.python.service import (
    skyfieldService,
    satnogsService,
    tleService,
)
from src.python.util.asyncUtil import asyncRequest


mainRoute: Blueprint = Blueprint("main", __name__)
cors(mainRoute)


@mainRoute.route(f"/", methods=["GET"])
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


@mainRoute.route(f"{apiBaseUrl}/heartbeat", methods=["GET"])
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


@mainRoute.route(f"{apiBaseUrl}/serverMetric", methods=["GET"])
async def getServerMetric():
    duration: float = request.args.get("duration", default=3600.0 * 24, type=float)

    t: float = time.perf_counter()
    kvSet: dict[str, dict[str, str | datetime]] = await tleService.readTwoLineElement()
    initialLoadTime: float = time.perf_counter() - t
    keySet: list = kvSet.keys()
    t = time.perf_counter()
    for satellite in keySet:
        _ = skyfieldService.findHorizonTime(
            kvSet[satellite],
            duration,
            wgs84.latlon(33.6405, -117.8443, elevation_m=0),
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
