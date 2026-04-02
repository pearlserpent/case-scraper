import hashlib
import hmac
import requests
import time
from config import get_settings

settings = get_settings()
BASE_URL = "https://cdn-ind.testnet.deltaex.org"

def generate_signature(secret: str, message: str) -> str:
    return hmac.new(
        bytes(secret, "utf-8"),
        bytes(message, "utf-8"),
        hashlib.sha256
    ).hexdigest()

def signed_request(method: str, path: str, params: dict | None = None, payload: str = "") -> requests.Response:
    timestamp = str(int(time.time()))
    
    # Build query string manually to match what requests will send
    query_string = ""
    if params:
        query_string = "?" + "&".join(f"{k}={v}" for k, v in params.items())
    
    signature_data = method.upper() + timestamp + path + query_string + payload
    signature = generate_signature(settings.api_secret, signature_data)

    headers = {
        "api-key": settings.api_key,
        "timestamp": timestamp,
        "signature": signature,
        "User-Agent": "python-rest-client",
        "Content-Type": "application/json",
    }

    url = f"{BASE_URL}{path}"
    return requests.request(
        method, url,
        params=params,
        data=payload or None,
        headers=headers,
        timeout=(3, 27),
    )

# Get wallet balances
""" r = signed_request("GET", "/v2/wallet/balances")
print(r.json())
 """
# Get open orders
""" r = signed_request("GET", "/v2/products/ETHUSD", params={})
print(r.json()) """

from datetime import datetime, timedelta
import pandas as pd

def get_candles(
    symbol: str,
    resolution: str = "1h",
    days_back: int = 7,
) -> pd.DataFrame:
    """
    resolution options: 1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 1d, 7d, 30d, 1w, 2w
    """
    end = int(datetime.now().timestamp())
    start = int((datetime.now() - timedelta(days=days_back)).timestamp())

    params = {
        "symbol": symbol,
        "resolution": resolution,
        "start": start,
        "end": end,
    }

    headers = {
        'Accept': 'application/json'
        }
    r = requests.get(f"https://api.india.delta.exchange/v2/history/candles", params=params, headers=headers)
    r.raise_for_status()

    data = r.json().get("result", [])
    if not data:
        return pd.DataFrame()

    df = pd.DataFrame(data, columns=["time", "open", "high", "low", "close", "volume"])
    df["time"] = pd.to_datetime(df["time"], unit="s", utc=True)
    df = df.sort_values("time").set_index("time")
    return df.astype({"open": float, "high": float, "low": float, "close": float, "volume": float})


# Usage
df = get_candles("ETHUSD", resolution="15m", days_back=1)
print(df)


