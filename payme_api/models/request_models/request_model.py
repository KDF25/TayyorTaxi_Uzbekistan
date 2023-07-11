from pydantic import BaseModel
from typing import Dict


class Request(BaseModel):
    jsonrpc: str
    id: str
    method: str
    params: Dict

