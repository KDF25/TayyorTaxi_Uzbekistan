from payme_api.models.response_models.response_model import Response
from pydantic import BaseModel


class Result(BaseModel):
    allow: bool = True


class ResultCheckPerformTransaction(Response):
    result: Result


result_check_perform_transaction = ResultCheckPerformTransaction(result=Result()).dict()
