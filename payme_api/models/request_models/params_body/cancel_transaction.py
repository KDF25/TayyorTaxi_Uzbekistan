from pydantic import BaseModel
from payme_api.models.request_models.request_model import Request


class Params(BaseModel):
    id: str
    reason: int


class RequestCancelTransaction(Request):
    params: Params
