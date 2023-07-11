from typing import NamedTuple


class Click_Data(NamedTuple):
    service_id: int
    merchant_id: int
    secret_key: str
    merchant_user_id: int