from aiohttp import web
from pgsql import pg
from config import bot
from datetime_now.datetime_now import dt_now
from text.driver.form_personal_data import FormPersonalData
import json

from payme_api.models.request_models.params_body.check_perform_transaction import RequestCheckPerformTransaction
from payme_api.models.request_models.params_body.create_transaction import RequestCreateTransaction
from payme_api.models.request_models.params_body.perform_transaction import RequestPerformTransaction
from payme_api.models.request_models.params_body.cancel_transaction import RequestCancelTransaction
from payme_api.models.request_models.params_body.check_transaction import RequestCheckTransaction

from payme_api.models.response_models.error_response import (error_invalid_account,
                                                             error_invalid_amount,
                                                             error_could_not_perform,
                                                             error_transaction_not_found,
                                                             error_could_not_cansel, )
from payme_api.models.response_models.result_bodies.check_perform_transaction_result \
    import ResultCheckPerformTransaction, Result
from payme_api.models.response_models.result_bodies import create_transaction_result as ctr
from payme_api.models.response_models.result_bodies import perform_transaction_result as ptr
from payme_api.models.response_models.result_bodies import cancel_transaction_result as can_tr
from payme_api.models.response_models.result_bodies import check_transaction_result as ch_tr
from payme_api.models.response_models.result_bodies import get_statement_result as get_st
form = FormPersonalData()

# check perform transaction
async def check_perform_transaction(transaction: dict, return_bool: bool = False):
    data = RequestCheckPerformTransaction(**transaction)
    state = await pg.get_state(order_id=data.params.account.order)
    if await pg.get_order(order_id=data.params.account.order) is False:
        return web.json_response(error_invalid_account, status=200)
    elif state in (-1, -2, 1, 2):
        return web.json_response(error_invalid_account, status=200)
    elif data.params.amount != await pg.get_amount(order_id=data.params.account.order):
        return web.json_response(error_invalid_amount, status=200)
    else:
        if return_bool:
            return True
        result_check_perform_transaction = ResultCheckPerformTransaction(result=Result(allow=True)).dict()
        return web.json_response(result_check_perform_transaction, status=200)


# create transaction
async def create_transaction(transaction: dict):
    data = RequestCreateTransaction(**transaction)
    if await pg.get_transaction_id(transaction_id=data.params.id, order_id=data.params.account.order):
        return await create_transaction_get_transaction_true(transaction=transaction)
    else:
        return await create_transaction_get_transaction_false(transaction=transaction)


async def create_transaction_get_transaction_true(transaction: dict):
    data = RequestCreateTransaction(**transaction)
    state = await pg.get_state(order_id=data.params.account.order)
    create_time = await pg.get_create_time(order_id=data.params.account.order, transaction_id=data.params.id)
    if state == 1:
        if data.params.time - create_time < 43_200_000:
            result_create_transaction = ctr.ResultCreateTransaction(result=ctr.Result(
                create_time=data.params.time,
                transaction=await pg.get_transaction(order_id=data.params.account.order),
                state=1)).dict()
            return web.json_response(result_create_transaction, status=200)
        elif data.params.time - create_time >= 43_200_000:
            await pg.update_state(state=-1, order_id=data.params.account.order)
            await pg.update_reason(reason=4, order_id=data.params.account.order, transaction_id=data.params.id)
            return web.json_response(error_could_not_perform, status=200)
    else:
        return web.json_response(error_could_not_perform, status=200)


async def create_transaction_get_transaction_false(transaction: dict):
    data = RequestCreateTransaction(**transaction)
    if await check_perform_transaction(transaction=transaction, return_bool=True) is True:
        await pg.update_state(state=1, order_id=data.params.account.order)
        await pg.update_transaction_id(transaction_id=data.params.id, order_id=data.params.account.order)
        await pg.update_create_time(create_time=data.params.time, order_id=data.params.account.order,
                                    transaction_id=data.params.id)
        result_create_transaction = ctr.ResultCreateTransaction(result=ctr.Result(
            create_time=data.params.time,
            transaction=await pg.get_transaction(order_id=data.params.account.order),
            state=1)).dict()
        return web.json_response(result_create_transaction, status=200)
    else:
        return await check_perform_transaction(transaction=transaction)


# perform transaction
async def perform_transaction(transaction: dict):
    data = RequestPerformTransaction(**transaction)
    create_time = await pg.get_create_time_by_transaction_id(transaction_id=data.params.id)
    if await pg.get_transaction_by_id(transaction_id=data.params.id):
        if await pg.get_state_by_transaction_id(transaction_id=data.params.id) == 1:
            if dt_now.now().timestamp() * 1000 - create_time < 43_200_000:
                return await positive_part(transaction=transaction)
            else:
                await pg.update_state_by_transaction_id(state=-1, transaction_id=data.params.id)
                await pg.update_reason_by_transaction_id(reason=4, transaction_id=data.params.id)
                return web.json_response(error_could_not_perform, status=200)
        elif await pg.get_state_by_transaction_id(transaction_id=data.params.id) == 2:
            return await positive_response(transaction=transaction)
        else:
            return web.json_response(error_could_not_perform, status=200)
    else:
        return web.json_response(error_transaction_not_found, status=200)


async def positive_part(transaction: dict):
    data = RequestPerformTransaction(**transaction)
    await pg.update_perform_time(perform_time=dt_now.now().timestamp() * 1000,
                                 transaction_id=data.params.id)
    driver_id = await pg.get_user_id(transaction_id=data.params.id)
    language = await pg.select_language(user_id=driver_id)
    cash = await pg.select_cash(transaction_id=data.params.id)
    text = await form.payment_accept(language=language, cash=cash)
    await bot.send_message(chat_id=driver_id, text=text)
    await pg.update_state_by_transaction_id(state=2, transaction_id=data.params.id)
    await pg.update_cash_to_wallet(
        cash=(await pg.select_current_driver_cash(transaction_id=data.params.id) +
              await pg.select_cash(transaction_id=data.params.id)),
        transaction_id=data.params.id)
    await pg.update_status(status=True, transaction_id=data.params.id)
    return await positive_response(transaction=transaction)

async def positive_response(transaction: dict):
    data = RequestPerformTransaction(**transaction)
    result = ptr.ResultPerformTransaction(result=ptr.Result(
        transaction=await pg.get_transaction_incr(transaction_id=data.params.id),
        perform_time=await pg.get_perform_time(transaction_id=data.params.id),
        state=await pg.get_state_by_transaction_id(transaction_id=data.params.id))).dict()
    return web.json_response(result, status=200)


# cancel transaction
async def cancel_transaction(transaction: dict):
    data = RequestCancelTransaction(**transaction)
    create_time = await pg.get_create_time_by_transaction_id(transaction_id=data.params.id)
    if await pg.get_transaction_by_id(transaction_id=data.params.id):
        if await pg.get_state_by_transaction_id(transaction_id=data.params.id) == 1:
            await pg.update_state_by_transaction_id(state=-1, transaction_id=data.params.id)
            await pg.update_reason_by_transaction_id(reason=data.params.reason, transaction_id=data.params.id)
            await pg.update_cansel_time(cansel_time=dt_now.now().timestamp() * 1000,
                                        transaction_id=data.params.id)
            return await cancel_yes(transaction=transaction)
        elif await pg.get_state_by_transaction_id(transaction_id=data.params.id) == 2:
            if dt_now.now().timestamp() * 1000 - create_time < 43_200_000:
                await pg.update_state_by_transaction_id(state=-2, transaction_id=data.params.id)
                await pg.update_reason_by_transaction_id(reason=data.params.reason, transaction_id=data.params.id)
                await pg.update_cansel_time(cansel_time=dt_now.now().timestamp() * 1000,
                                            transaction_id=data.params.id)
                return await cancel_yes(transaction=transaction)
            elif dt_now.now().timestamp() * 1000 - create_time > 43_200_000:
                return web.json_response(error_could_not_cansel, status=200)
        else:
            return await cancel_yes(transaction=transaction)
    else:
        return web.json_response(error_transaction_not_found, status=200)


async def cancel_yes(transaction: dict):
    data = RequestCancelTransaction(**transaction)
    result = can_tr.ResultCancelTransaction(result=can_tr.Result(
        transaction=await pg.get_transaction_incr(transaction_id=data.params.id),
        cancel_time=await pg.get_cancel_time(transaction_id=data.params.id),
        state=await pg.get_state_by_transaction_id(transaction_id=data.params.id))).dict()
    await bot.send_message(chat_id=await pg.get_user_id(transaction_id=data.params.id),
                           text="Оплата отменена успешно.\nTo'lov bekor qilindi")
    return web.json_response(result, status=200)


# check transaction
async def check_transaction(transaction: dict):
    data = RequestCheckTransaction(**transaction)
    if await pg.get_transaction_by_id(transaction_id=data.params.id):
        result = ch_tr.ResultCheckTransaction(result=ch_tr.Result(
            create_time=await pg.get_create_time_by_transaction_id(transaction_id=data.params.id),
            perform_time=await pg.get_perform_time(transaction_id=data.params.id),
            cancel_time=await pg.get_cancel_time(transaction_id=data.params.id),
            transaction=await pg.get_transaction_incr(transaction_id=data.params.id),
            state=await pg.get_state_by_transaction_id(transaction_id=data.params.id),
            reason=await pg.get_reason(transaction_id=data.params.id))).dict()
        return web.json_response(result, status=200)
    else:
        return web.json_response(error_transaction_not_found, status=200)


# get statement
async def get_statement(transaction: dict):
    times = get_st.FromTo(from_=transaction["params"]["from"], to=transaction["params"]["to"])
    result = get_st.ResultGetStatementTransaction(result=get_st.Result(
        transactions=await get_st.response_get_statement(times=times))).dict()
    return web.json_response(result, status=200)
