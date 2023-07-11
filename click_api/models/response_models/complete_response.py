from pydantic import BaseModel
from typing import Optional


class CompleteResponse(BaseModel):
    click_trans_id: int
    merchant_trans_id: str
    merchant_confirm_id: Optional[int]
    error: int
    error_note: str
