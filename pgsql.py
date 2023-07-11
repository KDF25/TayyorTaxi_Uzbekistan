from database.postgresql import Database
import asyncio

loop = asyncio.get_event_loop()
pg = Database(loop=loop)
