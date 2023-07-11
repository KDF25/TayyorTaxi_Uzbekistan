from pydantic import BaseModel


class PrepareRequest(BaseModel):
    click_trans_id: int
    service_id: int
    click_paydoc_id: int
    merchant_trans_id: str
    amount: int
    action: int
    error: int
    error_note: str
    sign_time: str
    sign_string: str
