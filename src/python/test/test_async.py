import requests
import time
from ..util.asyncUtil import asyncRequest, asyncRequestAll, asyncio, aiohttp
from ..service.satnogsService import TRANSMITTER_URL, TLE_URL, SATELLITE_URL


def testSyncRequest():
    t = time.perf_counter()
    for _ in range(0, 10):
        _ = requests.get(TLE_URL).json()
        _ = requests.get(TRANSMITTER_URL).json()
        _ = requests.get(SATELLITE_URL).json()

    assert time.perf_counter() - t > 60


def testAsyncRequest():
    t = time.perf_counter()

    async def asyncTestAsyncRequest():
        async with aiohttp.ClientSession() as session:
            asyncRequestUrls = []
            for _ in range(0, 10):
                asyncRequestUrls.append(TLE_URL)
                asyncRequestUrls.append(TRANSMITTER_URL)
                asyncRequestUrls.append(SATELLITE_URL)

            asyncResponseData = await asyncRequestAll(session, asyncRequestUrls)

            for data in asyncResponseData:
                _ = data

    asyncio.run(asyncTestAsyncRequest())
    assert time.perf_counter() - t < 20


if __name__ == "__main__":
    pass
