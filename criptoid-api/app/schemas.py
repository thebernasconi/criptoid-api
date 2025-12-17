from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class FavoritesResponse(BaseModel):
    favorites: List[str]

class MessageResponse(BaseModel):
    message: str

class RefreshRequest(BaseModel):
    symbols: Optional[List[str]] = None

class PriceOut(BaseModel):
    symbol: str
    price: float
    currency: str
    fetched_at: datetime

class PricesResponse(BaseModel):
    prices: List[PriceOut]
