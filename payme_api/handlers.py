from payme_api.funcs import (check_perform_transaction,
                             create_transaction,
                             perform_transaction,
                             cancel_transaction,
                             check_transaction,
                             get_statement,)
from aiohttp import web
from payme_api.check_authorization import authorization_check


methods = {
    "CheckPerformTransaction": check_perform_transaction,
    "CreateTransaction": create_transaction,
    "PerformTransaction": perform_transaction,
    "CancelTransaction": cancel_transaction,
    "CheckTransaction": check_transaction,
    "GetStatement": get_statement,
}


@authorization_check
async def post_requests(transaction):
    data = await transaction.json()
    if methods.get(data.get("method")) is None:
        return web.json_response({"method": False}, status=200)
    else:
        return await methods[data["method"]](transaction=data)
