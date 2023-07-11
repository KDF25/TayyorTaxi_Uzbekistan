import typing


class InsertCreatedOrder(typing.NamedTuple):
    click_trans_id: int
    click_paydoc_id: int
    merchant_trans_id: typing.Union[str, int]
    amount: int
    action: int
    sign_time: str
    canceled: bool

