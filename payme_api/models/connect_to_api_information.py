from typing import NamedTuple


class ApiKeys(NamedTuple):
    status: bool
    testkey: str
    prod_key: str
    payme_key: bytes
    merchant_id: str
    payme_url: str

