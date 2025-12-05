from pydantic import BaseModel
from typing import Optional


class StockPrice(BaseModel):
    symbol: str
    price: Optional[float]
