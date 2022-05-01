import aiohttp
import asyncio


async def asyncRequest(session: aiohttp.ClientSession, url: str) -> object:
    async with session.get(url) as response:
        return await response.json()


async def asyncRequestAll(session: aiohttp.ClientSession, urls: [str]) -> object:
    asyncTask = [
        asyncio.ensure_future(
            asyncRequest(
                session,
                url)) for url in urls]
    return await asyncio.gather(*asyncTask)
