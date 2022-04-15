import requests

baseUrl = "https://uci-cubesat-server.herokuapp.com/api/v1"
tleUrl = f"{baseUrl}/tle"
heartBeatUrl = f"{baseUrl}/heartbeat"
availableSatelliteUrl = f"{baseUrl}/available_satellite"


def testTle():
    getTle = requests.get(tleUrl)
    getHeartBeat = requests.get(heartBeatUrl)
    assert getTle.status_code == 200
    assert getHeartBeat.status_code == 200
    assert len(getHeartBeat.json()) >= len(getTle.json()) > 0


def testAvailableSatellite():
    getAvailableSatellite = requests.get(availableSatelliteUrl)
    assert getAvailableSatellite.status_code == 200
    assert str(type(getAvailableSatellite.json())) == "<class 'list'>"


if __name__ == "__main__":
    pass
