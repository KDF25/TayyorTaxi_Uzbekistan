from aiohttp import web
from pgsql import pg
from click_api.models.response_models.prepare_response import PrepareResponse
from click_api.models.request_models.prepare_request import PrepareRequest
from click_api.errors import user_does_not_exist


def merchant_trans_id_does_not_exist(func):
    async def wrapper(req: web.Request):
        request = PrepareRequest(**await req.post())
        response = PrepareResponse(click_trans_id=request.click_trans_id,
                                   merchant_trans_id=request.merchant_trans_id,
                                   merchant_prepare_id=request.merchant_trans_id,
                                   error=user_does_not_exist.error,
                                   error_note=user_does_not_exist.error_note).dict()
        try:
            await pg.select_prepare_id(merchant_trans_id=request.merchant_trans_id)
            return await func(req)
        except TypeError:
            return web.json_response(response, status=200)

    return wrapper
