# python-worker/scripts/fetch_data.py
"""
Fetches historical data from:
- Binance API
- CoinGecko API
- Local database cache
"""
import ccxt
import pandas as pd
from datetime import datetime, timedelta
import time
import sqlite3
from pathlib import Path

DATA_DIR = Path(__file__).parent / "../data"
EXCHANGES = {
    'binance': ccxt.binance(),
    'kraken': ccxt.kraken()
}

def fetch_ohlcv(pair: str, timeframe: str, days: int = 30):
    """Fetch OHLCV data from multiple exchanges"""
    all_data = []
    
    for exchange_name, exchange in EXCHANGES.items():
        try:
            since = exchange.parse8601((datetime.now() - timedelta(days=days)).isoformat())
            ohlcv = exchange.fetch_ohlcv(pair, timeframe, since)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['exchange'] = exchange_name
            all_data.append(df)
            time.sleep(0.5)  # Rate limit
        except Exception as e:
            print(f"Error fetching from {exchange_name}: {e}")
    
    combined = pd.concat(all_data)
    combined['timestamp'] = pd.to_datetime(combined['timestamp'], unit='ms')
    combined.sort_values('timestamp', inplace=True)
    
    # Save
    Path(DATA_DIR).mkdir(exist_ok=True)
    combined.to_csv(DATA_DIR / f"{pair.replace('/', '-')}_{timeframe}.csv", index=False)
    return combined

if __name__ == "__main__":
    fetch_ohlcv('ETH/USDT', '15m', days=180)