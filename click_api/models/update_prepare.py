import typing


class PrepareUpdate(typing.NamedTuple):
    click_trans_id: int
    click_paydoc_id: int
    action: int
    sign_time: str
    merchant_trans_id: str

