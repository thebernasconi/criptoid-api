import requests
from typing import List, Dict, Any
from ..settings import settings

def fetch_quotes(symbols: List[str]) -> List[Dict[str, Any]]:
    """
    Chama a API secundária (Quotes Service), que por sua vez consulta Yahoo Finance.
    """
    url = f"{settings.quotes_service_url}/v1/quotes"
    r = requests.post(url, json={"symbols": symbols}, timeout=15)
    r.raise_for_status()
    return r.json()["prices"]
