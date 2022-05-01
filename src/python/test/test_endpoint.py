import requests
from datetime import datetime
from urllib.parse import quote

from ..util.asyncUtil import asyncRequest, asyncRequestAll, aiohttp, asyncio
from ..service.mockDataService import generateLngLat

# baseUrl for production
baseUrl = "https://uci-cubesat-server-dev.herokuapp.com/api/v1"
# baseUrl if you are running pytest locally
# baseUrl = "http://127.0.0.1:5000/api/v1"
tleUrl = f"{baseUrl}/tle"
heartBeatUrl = f"{baseUrl}/heartbeat"
availableSatelliteUrl = f"{baseUrl}/available_satellite"
predictionUrl = f"{baseUrl}/prediction"
calculationUrl = f"{baseUrl}/serverMetric"


def isValidIso(datetimeString):
    try:
        datetime.fromisoformat(datetimeString)
    except Exception:
        return False
    return True


def testStatus():
    async def asyncTestStatus():
        async with aiohttp.ClientSession() as session:
            data = await asyncRequest(session, heartBeatUrl)
        assert isinstance(data, dict)
        assert data["status"] == "online"
        assert data["satnogs"]["status"] == "online"
        assert data["database"]["status"] == "online"

    asyncio.run(asyncTestStatus())


def testTle():
    getTle = requests.get(tleUrl)
    assert getTle.status_code == 200
    getTle = requests.get(f"{tleUrl}?refresh=true")
    assert getTle.status_code == 200
    getTle = requests.get(tleUrl)
    assert getTle.status_code == 200
    assert isinstance(getTle.json(), dict)


def testCalculation():
    runCalculation = requests.get(calculationUrl)
    assert runCalculation.status_code == 200
    assert isinstance(runCalculation.json(), dict)


def testAvailableSatellite():
    getAvailableSatellite = requests.get(availableSatelliteUrl)
    assert getAvailableSatellite.status_code == 200
    assert len(getAvailableSatellite.json()) != 0
    assert isinstance(getAvailableSatellite.json(), list)


def testPrediction():
    async def asyncTestPrediction():
        async with aiohttp.ClientSession() as session:
            requestUrls = [f"{predictionUrl}?satellite={quote(key)}" +
                           f"&latitude=33.6405&longitude=-117.8443" +
                           f"&duration={3600.0 * 1.0 * 24.0} "
                           for key in requests.get(availableSatelliteUrl).json()]
            asyncResponse = await asyncRequestAll(session, requestUrls)

            for data in asyncResponse:
                assert isinstance(data, dict)
                for peak in data.keys():
                    assert isValidIso(peak) and isValidIso(
                        data[peak]["rise"]) and isValidIso(
                        data[peak]["set"])

    asyncio.run(asyncTestPrediction())


# def testPredictionWithMockLngLat():
#     async def asyncTestPredictionWithMockLngLat():
#         async with aiohttp.ClientSession() as session:
#             asyncResponse = await asyncRequestAll(session, [f"{predictionUrl}?satellite={quote(key)}" +
#                                                             f"&latitude={generateLngLat()['lat']}" +
#                                                             f"&longitude={generateLngLat()['lng']}" +
#                                                             f"&duration={3600.0 * 1.0 * 24.0}"
#                                                             for key in requests.get(availableSatelliteUrl).json()])
#
#             for data in asyncResponse:
#                 assert isinstance(data, dict)
#                 for peak in data.keys():
#                     assert isValidIso(peak) and isValidIso(
#                         data[peak]["rise"]) and isValidIso(
#                         data[peak]["set"])
#
#     asyncio.run(asyncTestPredictionWithMockLngLat())


if __name__ == "__main__":
    pass
