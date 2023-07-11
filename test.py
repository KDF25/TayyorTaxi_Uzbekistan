# import aiohttp
# import ssl
# import certifi
# from typing import Optional
# import asyncio
#
#
# async def aioreq(url: str, post: bool, parameters: dict, headers: Optional[dict] = None) -> dict:
#     ssl_context = ssl.create_default_context(cafile=certifi.where())
#     conn = aiohttp.TCPConnector(ssl=ssl_context)
#
#     async with aiohttp.ClientSession(connector=conn) as session:
#         if post:
#             async with session.post(url=url, headers=headers,
#                                     json=parameters) as resp:  # [1]
#                 return await resp.json() # [2]
#         else:
#             async with session.get(url=url, params=parameters) as resp:  # [1]
#                 return await resp.json()  # [2]
#
#
# url1 = "http://159.223.200.9:6000/prepare"
# url2 = "http://185.74.5.147:6000"
# url3 = "https://laappetit.uz/prepare"
#
# loop = asyncio.get_event_loop()
# print(loop.run_until_complete(aioreq(url=url1, post=True, parameters={"name": "John"})))
