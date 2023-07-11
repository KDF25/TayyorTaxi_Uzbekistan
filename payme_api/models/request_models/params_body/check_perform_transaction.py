from pydantic import BaseModel
from payme_api.models.request_models.account import Account
from payme_api.models.request_models.request_model import Request


class Params(BaseModel):
    amount: int
    account: Account


class RequestCheckPerformTransaction(Request):
    params: Params

