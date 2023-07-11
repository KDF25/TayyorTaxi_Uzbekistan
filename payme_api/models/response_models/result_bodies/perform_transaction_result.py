from payme_api.models.response_models.response_model import Response
from pydantic import BaseModel


class Result(BaseModel):
    transaction: str
    perform_time: int
    state: int


class ResultPerformTransaction(Response):
    result: Result

