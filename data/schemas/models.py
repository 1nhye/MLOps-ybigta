from pydantic import BaseModel
from typing import Dict, List

class BTCcandle(BaseModel):
    symbol: str
    open_time: str
    open: float
    high: float
    low: float
    close: float
    volume: float
    close_time: str