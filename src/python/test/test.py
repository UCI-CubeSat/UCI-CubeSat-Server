import requests

baseUrl = "http://127.0.0.1:5000/api/v1"

if __name__ == "__main__":
    predictionUrl = f"{baseUrl}/prediction?satellite=OSCAR%207%20(AO-7)"
    assert requests.get(predictionUrl).status_code == 200
    assert requests.get(predictionUrl).json() == {}

    predictionUrl = f"{baseUrl}/prediction?satellite=OSCAR%207%20(AO-7)&latitude=33.6405&longitude=-117.8443"
    assert requests.get(predictionUrl).status_code == 200
    assert requests.get(predictionUrl).json() != {}

    tleUrl = f"{baseUrl}/tle"
    assert requests.get(predictionUrl).status_code == 200
    assert requests.get(predictionUrl).json() != {}

    availableSatelliteUrl = f"{baseUrl}/available_satellite"
    assert requests.get(availableSatelliteUrl).status_code == 200
    assert type(requests.get(availableSatelliteUrl).json()) is type([])
