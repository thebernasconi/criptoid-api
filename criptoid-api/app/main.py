from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import select, desc
from typing import List, Optional
from .db import Base, engine, get_db
from .models import Favorite, PriceSnapshot
from .schemas import FavoritesResponse, MessageResponse, RefreshRequest, PricesResponse, PriceOut
from .services.quotes_client import fetch_quotes

DEFAULT_SYMBOLS = ["BTC-USD", "ETH-USD", "SOL-USD", "XRP-USD", "ADA-USD"]

app = FastAPI(title="CRIPTOID API", version="1.0.0")

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)

@app.get("/health", response_model=MessageResponse)
def health():
    return {"message": "ok"}

# ===== FAVORITES (GET/PUT/DELETE) =====

@app.get("/api/v1/favorites", response_model=FavoritesResponse)
def list_favorites(db: Session = Depends(get_db)):
    rows = db.execute(select(Favorite).order_by(Favorite.symbol)).scalars().all()
    return {"favorites": [r.symbol for r in rows]}

@app.put("/api/v1/favorites/{symbol}", response_model=MessageResponse)
def upsert_favorite(symbol: str, db: Session = Depends(get_db)):
    symbol = symbol.strip().upper()
    exists = db.get(Favorite, symbol)
    if not exists:
        db.add(Favorite(symbol=symbol))
        db.commit()
    return {"message": f"{symbol} favoritado"}

@app.delete("/api/v1/favorites/{symbol}", response_model=MessageResponse)
def delete_favorite(symbol: str, db: Session = Depends(get_db)):
    symbol = symbol.strip().upper()
    obj = db.get(Favorite, symbol)
    if not obj:
        raise HTTPException(status_code=404, detail="Favorito não encontrado")
    db.delete(obj)
    db.commit()
    return {"message": f"{symbol} removido dos favoritos"}

# ===== PRICES (GET/POST) =====

@app.get("/api/v1/prices/latest", response_model=PricesResponse)
def latest_prices(
    symbols: Optional[str] = Query(default=None, description="CSV, ex: BTC-USD,ETH-USD"),
    db: Session = Depends(get_db),
):
    sym_list = DEFAULT_SYMBOLS if not symbols else [s.strip().upper() for s in symbols.split(",") if s.strip()]
    out: List[PriceOut] = []

    for sym in sym_list:
        row = db.execute(
            select(PriceSnapshot).where(PriceSnapshot.symbol == sym).order_by(desc(PriceSnapshot.fetched_at)).limit(1)
        ).scalars().first()
        if row:
            out.append(PriceOut(symbol=row.symbol, price=float(row.price), currency=row.currency, fetched_at=row.fetched_at))
        else:
            # ainda sem snapshot no banco -> não quebra o front
            pass

    return {"prices": out}

@app.post("/api/v1/prices/refresh", response_model=PricesResponse)
def refresh_prices(payload: RefreshRequest, db: Session = Depends(get_db)):
    sym_list = payload.symbols or DEFAULT_SYMBOLS
    sym_list = [s.strip().upper() for s in sym_list if s and s.strip()]

    # chama API secundária (que chama Yahoo Finance)
    prices = fetch_quotes(sym_list)

    # persiste snapshots
    snapshots: List[PriceOut] = []
    for p in prices:
        snap = PriceSnapshot(
            symbol=p["symbol"].upper(),
            price=p["price"],
            currency=p.get("currency") or "USD",
        )
        db.add(snap)
        db.flush()  # garante fetched_at disponível
        db.refresh(snap)
        snapshots.append(PriceOut(symbol=snap.symbol, price=float(snap.price), currency=snap.currency, fetched_at=snap.fetched_at))

    db.commit()
    return {"prices": snapshots}
