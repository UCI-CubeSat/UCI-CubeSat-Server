import asyncio
import cProfile
import pstats
from datetime import datetime
from pstats import Stats

from skyfield.toposlib import wgs84
from src.python.service import tleService, skyfieldService


async def profileReadTwoLineElement() -> None:
    with cProfile.Profile() as profiler:
        await tleService.readTwoLineElement()

    stat: Stats = pstats.Stats(profiler)
    stat.sort_stats(pstats.SortKey.TIME)
    stat.print_stats()


async def profileGetHorizon() -> None:
    twoLineElement: dict[
        str, dict[str, str | datetime]
    ] = await tleService.readTwoLineElement()
    with cProfile.Profile() as profiler:
        skyfieldService.findHorizonTime(
            twoLineElement[next(iter(twoLineElement.keys()))],
            3600 * 24 * 1.0,
            wgs84.latlon(33.6405, -117.8443, elevation_m=0),
        )

    stat: Stats = pstats.Stats(profiler)
    stat.sort_stats(pstats.SortKey.TIME)
    stat.print_stats()


if __name__ == "__main__":
    for funcName in dir():
        if funcName[: len("profile")] != "profile":
            continue

        asyncio.run(locals()[funcName]())
