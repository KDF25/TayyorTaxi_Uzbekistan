import base64
from aiohttp import web
from payme_api.paycom_exceptions import *
from config import payme_keys


async def check_auth(transaction):
    try:
        input_auth = transaction.headers.get('Authorization').split(' ')[1]
        if base64.urlsafe_b64decode(s=input_auth) != payme_keys.payme_key:
            return True
    except AttributeError:
        return True


def authorization_check(func):
    async def wrapper(transaction):
        if await check_auth(transaction=transaction):
            return web.json_response({"error": {"code": ERROR_INSUFFICIENT_PRIVILEGE,
                                                "message": "Недостаточно привилегий для выполнения операции"}},
                                     status=200)
        else:
            return await func(transaction)
    return wrapper
