from pydantic import BaseModel


class PrepareResponse(BaseModel):
    click_trans_id: int
    merchant_trans_id: int
    merchant_prepare_id: int
    error: int
    error_note: str
