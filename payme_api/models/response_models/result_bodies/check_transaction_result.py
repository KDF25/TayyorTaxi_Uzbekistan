from payme_api.models.response_models.response_model import Response
from pydantic import BaseModel
import typing


class Result(BaseModel):
    create_time: int
    perform_time: int
    cancel_time: int
    transaction: str
    state: int
    reason: typing.Union[int, None]


class ResultCheckTransaction(Response):
    result: Result
