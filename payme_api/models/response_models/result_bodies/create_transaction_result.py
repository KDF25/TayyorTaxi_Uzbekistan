from payme_api.models.response_models.response_model import Response
from pydantic import BaseModel


class Result(BaseModel):
    create_time: int
    transaction: str
    state: int


class ResultCreateTransaction(Response):
    result: Result


