import hashlib


async def md5(string: str):
    return hashlib.md5(string.encode('utf-8')).hexdigest()