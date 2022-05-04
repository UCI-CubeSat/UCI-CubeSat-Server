from typing import Any
import aiohttp
import asyncio
from aiohttp import ClientResponse


async def asyncRequest(session: aiohttp.ClientSession, url: str) -> Any:
    response: ClientResponse
    async with session.get(url) as response:
        return await response.json()


async def asyncRequestAll(session: aiohttp.ClientSession, urls: [str]) -> tuple[Any]:
    asyncTask = [asyncio.ensure_future(asyncRequest(session, url)) for url in urls]
    return await asyncio.gather(*asyncTask)
