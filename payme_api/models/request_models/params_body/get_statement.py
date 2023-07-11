from pydantic import BaseModel
from payme_api.models.request_models.request_model import Request


class Params(BaseModel):
    from_: int
    to: int


class RequestGetStatement(Request):
    params: Params
