from aiohttp import web
from click_api.errors import sign_check_failed
from click_api.hash_md5_encode import md5
from config import cli_data
from click_api.models.response_models.prepare_response import PrepareResponse
from click_api.models.response_models.complete_response import CompleteResponse
from click_api.models.request_models.prepare_request import PrepareRequest
from click_api.models.request_models.complete_request import CompleteRequest
from pgsql import pg


async def check_auth_prepare(req: web.Request):
    request = await req.post()
    if request["sign_string"] != await md5(string=f"{request['click_trans_id']}"
                                                  f"{cli_data.service_id}"
                                                  f"{cli_data.secret_key}"
                                                  f"{request['merchant_trans_id']}"
                                                  f"{request['amount']}"
                                                  f"{request['action']}"
                                                  f"{request['sign_time']}"):
        return True


async def check_auth_complete(req: web.Request):
    request = await req.post()
    if request["sign_string"] != await md5(string=f"{request['click_trans_id']}"
                                                  f"{cli_data.service_id}"
                                                  f"{cli_data.secret_key}"
                                                  f"{request['merchant_trans_id']}"
                                                  f"{request['merchant_prepare_id']}"
                                                  f"{request['amount']}"
                                                  f"{request['action']}"
                                                  f"{request['sign_time']}"):
        return True


def prepare_authorization_check(func):
    async def wrapper(req: web.Request):
        if await check_auth_prepare(req):
            request = PrepareRequest(**await req.post())
            response = PrepareResponse(click_trans_id=request.click_trans_id,
                                       merchant_trans_id=request.merchant_trans_id,
                                       merchant_prepare_id=await pg.select_prepare_id(
                                           merchant_trans_id=request.merchant_trans_id),
                                       error=sign_check_failed.error,
                                       error_note=sign_check_failed.error_note).dict()
            return web.json_response(response, status=200)
        else:
            return await func(req)

    return wrapper


def complete_authorization_check(func):
    async def wrapper(req: web.Request):
        if await check_auth_complete(req):
            request = CompleteRequest(**await req.post())
            response = CompleteResponse(click_trans_id=request.click_trans_id,
                                        merchant_trans_id=request.merchant_trans_id,
                                        merchant_confirm_id=
                                        await pg.select_prepare_id(merchant_trans_id=request.merchant_trans_id),
                                        error=sign_check_failed.error,
                                        error_note=sign_check_failed.error_note).dict()
            return web.json_response(response, status=200)
        else:
            return await func(req)

    return wrapper
