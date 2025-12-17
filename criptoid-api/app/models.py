from sqlalchemy import String, Integer, DateTime, Numeric, func
from sqlalchemy.orm import Mapped, mapped_column
from .db import Base

class Favorite(Base):
    __tablename__ = "favorites"
    symbol: Mapped[str] = mapped_column(String(32), primary_key=True)

class PriceSnapshot(Base):
    __tablename__ = "price_snapshots"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    symbol: Mapped[str] = mapped_column(String(32), index=True)
    price: Mapped[float] = mapped_column(Numeric(18, 8))
    currency: Mapped[str] = mapped_column(String(8))
    fetched_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)
