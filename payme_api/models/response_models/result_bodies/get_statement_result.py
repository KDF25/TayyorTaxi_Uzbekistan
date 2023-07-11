from payme_api.models.request_models.account import Account
from payme_api.models.response_models.response_model import Response
from pydantic import BaseModel
import typing
from pgsql import pg


class Transaction(BaseModel):
    id: str
    time: int
    amount: int
    account: Account
    create_time: int
    perform_time: int
    cancel_time: int
    transaction: str
    state: int
    reason: typing.Union[int, None]


class Result(BaseModel):
    transactions: typing.List[Transaction]


class ResultGetStatementTransaction(Response):
    result: Result


class FromTo(typing.NamedTuple):
    from_: int
    to: int


async def response_get_statement(times: FromTo) -> [Transaction]:
    lst = []
    for transaction in await pg.from_to(from_=times.from_, to=times.to):
        lst.append(Transaction(id=[*transaction][0],
                               time=[*transaction][1],
                               amount=[*transaction][2],
                               account=Account(order=str([*transaction][3])),
                               create_time=[*transaction][4],
                               perform_time=[*transaction][5],
                               cancel_time=[*transaction][6],
                               transaction=[*transaction][7],
                               state=[*transaction][8],
                               reason=[*transaction][9]).dict())
    return lst


