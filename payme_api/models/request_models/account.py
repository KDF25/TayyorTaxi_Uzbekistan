from pydantic import BaseModel

order_id = str


class Account(BaseModel):
    order: order_id

