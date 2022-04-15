import requests
from src.python.service import tleService
from datetime import datetime

baseUrl = "https://uci-cubesat-server-dev.herokuapp.com/api/v1"
tleUrl = f"{baseUrl}/tle"
heartBeatUrl = f"{baseUrl}/heartbeat"
availableSatelliteUrl = f"{baseUrl}/available_satellite"


def testStatus():
    getStatus = requests.get(heartBeatUrl)
    assert getStatus.json()["status"] == "online"
    assert getStatus.json()["satnogs"]["status"] == "online"
    assert getStatus.json()["database"]["status"] == "online"
    assert tleService.isRecent(datetime(getStatus.json()["database"]["updated"]))


def testTle():
    getTle = requests.get(tleUrl)
    assert getTle.status_code == 200


def testAvailableSatellite():
    getAvailableSatellite = requests.get(availableSatelliteUrl)
    assert getAvailableSatellite.status_code == 200
    assert str(type(getAvailableSatellite.json())) == "<class 'list'>"
    assert len(getAvailableSatellite.json()) != 0


if __name__ == "__main__":
    pass
