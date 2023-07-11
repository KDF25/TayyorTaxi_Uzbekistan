import typing
from datetime import datetime


class InsertCreatedCheck(typing.NamedTuple):
    paycom_transaction_id: str
    paycom_time: datetime.timestamp
    paycom_time_datetime: datetime.strftime
    create_time: datetime.timestamp
    perform_time: typing.Union[datetime.timestamp, None]
    cancel_time: typing.Union[datetime.timestamp, None]
    amount: int
    state: int
    reason: typing.Union[int, None]
    receivers: typing.Union[str, None]
    order_id: int

