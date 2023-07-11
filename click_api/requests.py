from aiohttp import web
from click_api.models.request_models.prepare_request import PrepareRequest
from click_api.models.request_models.complete_request import CompleteRequest
from click_api.models.response_models.prepare_response import PrepareResponse
from click_api.models.response_models.complete_response import CompleteResponse
from click_api.errors import *
from pgsql import pg
from click_api.models.update_prepare import PrepareUpdate
from click_api.check_auth import prepare_authorization_check, complete_authorization_check
from click_api.check_merchant_trans_id import merchant_trans_id_does_not_exist
from typing import Union
from config import bot
from text.driver.form_personal_data import FormPersonalData
form = FormPersonalData()

@merchant_trans_id_does_not_exist
@prepare_authorization_check
async def prepare_pay(request: web.Request):
    req = PrepareRequest(**await request.post())
    if await pg.select_action(merchant_trans_id=req.merchant_trans_id) == 1:
        return await trans_does_not_exist(request=req)
    else:
        response = PrepareResponse(click_trans_id=req.click_trans_id,
                                   merchant_trans_id=req.merchant_trans_id,
                                   merchant_prepare_id=await pg.select_prepare_id(
                                       merchant_trans_id=req.merchant_trans_id),
                                   error=success.error,
                                   error_note=success.error_note).dict()
        await pg.update_prepare_parameters(update=PrepareUpdate(click_trans_id=req.click_trans_id,
                                                                click_paydoc_id=req.click_paydoc_id,
                                                                action=0,
                                                                sign_time=req.sign_time,
                                                                merchant_trans_id=req.merchant_trans_id))
        return web.json_response(response, status=200)


@complete_authorization_check
async def complete_pay(request: web.Request):
    req = CompleteRequest(**await request.post())
    if req.amount != await pg.select_amount(merchant_trans_id=req.merchant_trans_id):
        return await wrong_amount(request=req)
    elif await pg.select_action(merchant_trans_id=req.merchant_trans_id) == 1 and req.error == sign_check_failed.error:
        return await already_paid_trans(request=req)
    elif await pg.select_action(merchant_trans_id=req.merchant_trans_id) == 1 and req.error == success.error\
            and await pg.select_canceled(merchant_trans_id=req.merchant_trans_id) is True:
        return await trans_cancelled(request=req)
    elif await pg.select_action(merchant_trans_id=req.merchant_trans_id) == 1 and req.error == success.error:
        return await already_paid_trans(request=req)
    elif await pg.select_prepare_id(merchant_trans_id=req.merchant_trans_id) != req.merchant_prepare_id:
        return await trans_does_not_exist(request=req)
    elif await pg.select_action(merchant_trans_id=req.merchant_trans_id) == 1 and req.error == -5017:
        await pg.update_cancel_trans(cancel=True, merchant_trans_id=req.merchant_trans_id)
        return await trans_cancelled(request=req)
    else:
        response = CompleteResponse(click_trans_id=req.click_trans_id,
                                    merchant_trans_id=req.merchant_trans_id,
                                    merchant_confirm_id=await pg.select_prepare_id(merchant_trans_id=req.merchant_trans_id),
                                    error=success.error,
                                    error_note=success.error_note).dict()
        await pg.update_complete_parameters(action=1, sign_time=req.sign_time, merchant_trans_id=req.merchant_trans_id)
        await pg.update_cash_to_wallet_click(cash=(await pg.select_cash_click(merchant_trans_id=req.merchant_trans_id) +
                                                   await pg.select_current_cash_driver(merchant_trans_id=req.merchant_trans_id)),
                                             merchant_trans_id=req.merchant_trans_id)
        await pg.update_status_click(status=True, merchant_trans_id=req.merchant_trans_id)
        driver_id = await pg.get_user_id_click(merchant_trans_id=req.merchant_trans_id)
        language = await pg.select_language(user_id=driver_id)
        cash = await pg.select_cash_click(merchant_trans_id=req.merchant_trans_id)
        text = await form.payment_accept(language=language, cash=cash)
        await bot.send_message(chat_id=driver_id, text=text)
        return web.json_response(response, status=200)


async def wrong_amount(request: CompleteRequest):
    response = CompleteResponse(click_trans_id=request.click_trans_id,
                                merchant_trans_id=request.merchant_trans_id,
                                merchant_confirm_id=await pg.select_prepare_id(
                                    merchant_trans_id=request.merchant_trans_id),
                                error=incorrect_parameter_amount.error,
                                error_note=incorrect_parameter_amount.error_note).dict()
    return web.json_response(response, status=200)


async def already_paid_trans(request: CompleteRequest):
    response = CompleteResponse(click_trans_id=request.click_trans_id,
                                merchant_trans_id=request.merchant_trans_id,
                                merchant_confirm_id=await pg.select_prepare_id(
                                    merchant_trans_id=request.merchant_trans_id),
                                error=already_paid.error,
                                error_note=already_paid.error_note).dict()
    return web.json_response(response, status=200)


async def trans_does_not_exist(request: Union[CompleteRequest, PrepareRequest]):
    response = CompleteResponse(click_trans_id=request.click_trans_id,
                                merchant_trans_id=request.merchant_trans_id,
                                merchant_confirm_id=await pg.select_prepare_id(
                                    merchant_trans_id=request.merchant_trans_id),
                                error=transaction_does_not_exist.error,
                                error_note=transaction_does_not_exist.error_note).dict()
    return web.json_response(response, status=200)


async def trans_cancelled(request: CompleteRequest):
    response = CompleteResponse(click_trans_id=request.click_trans_id,
                                merchant_trans_id=request.merchant_trans_id,
                                merchant_confirm_id=await pg.select_prepare_id(
                                    merchant_trans_id=request.merchant_trans_id),
                                error=transaction_cancelled.error,
                                error_note=transaction_cancelled.error_note).dict()
    return web.json_response(response, status=200)

