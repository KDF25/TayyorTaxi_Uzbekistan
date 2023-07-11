from pydantic import BaseModel
from typing import Dict


class Response(BaseModel):
    jsonrpc: str = "2.0"
    result: Dict

