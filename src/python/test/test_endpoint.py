import requests
import time
from datetime import datetime

baseUrl = "https://uci-cubesat-server-dev.herokuapp.com/api/v1"
tleUrl = f"{baseUrl}/tle"
heartBeatUrl = f"{baseUrl}/heartbeat"
availableSatelliteUrl = f"{baseUrl}/available_satellite"
predictionUrl = f"{baseUrl}/prediction"


def testStatus():
    getStatus = requests.get(heartBeatUrl)
    assert getStatus.json()["status"] == "online"
    assert getStatus.json()["satnogs"]["status"] == "online"
    assert getStatus.json()["database"]["status"] == "online"


def testTle():
    getTle = requests.get(tleUrl)
    assert getTle.status_code == 200


def testAvailableSatellite():
    getAvailableSatellite = requests.get(availableSatelliteUrl)
    assert getAvailableSatellite.status_code == 200
    assert str(type(getAvailableSatellite.json())) == "<class 'list'>"
    assert len(getAvailableSatellite.json()) != 0


def testPrediction():
    def isValidIso(datimeString):
        try:
            datetime.fromisoformat(datimeString)
        except Exception:
            return False
        return True

    getAvailableSatellite = requests.get(availableSatelliteUrl)
    testKey: list = getAvailableSatellite.json()
    t = time.perf_counter()
    successCount = 0
    failCount = 0
    for key in testKey:
        testPredictionUrl = f"{predictionUrl}?" \
                            f"satellite={key}&latitude=33.6405&longitude=-117.8443&duration={3600.0 * 1.0 * 24.0}"
        try:
            response: dict = requests.get(testPredictionUrl).json()
            if response == dict():
                continue
            successCount += 1
            for peak in response.keys():
                assert isValidIso(peak) and isValidIso(
                    response[peak]["rise"]) and isValidIso(
                    response[peak]["set"])
        except Exception:
            failCount += 1

    assert time.perf_counter() - t < 90
    assert len(testKey) // 2 < successCount
    assert len(testKey) // 10 > failCount


if __name__ == "__main__":
    pass
