from pydantic import BaseModel
from payme_api.models.request_models.account import Account
from payme_api.models.request_models.request_model import Request


class Params(BaseModel):
    id: str
    time: int
    amount: int
    account: Account


class RequestCreateTransaction(Request):
    params: Params


