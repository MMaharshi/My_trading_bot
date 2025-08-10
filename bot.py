# bot.py
# Automated trading bot based on your TradingView strategy
# Author: maharshimankodi

import ccxt
import pandas as pd
import time

# ===== CONFIG =====
EXCHANGE = 'binance'
SYMBOL = 'BTC/USDT'
TIMEFRAME = '5m'
ATR_PERIOD = 14
ATR_MULTIPLIER = 1.4
RSI_PERIOD = 21
RSI_MA_PERIOD = 16
FETCH_LIMIT = 100
API_KEY = 'YOUR_API_KEY'
API_SECRET = 'YOUR_API_SECRET'

# ===== INITIALIZE EXCHANGE =====
exchange = getattr(ccxt, EXCHANGE)({
    'apiKey': API_KEY,
    'secret': API_SECRET
})

# ===== INDICATORS =====
def supertrend(df, period=ATR_PERIOD, multiplier=ATR_MULTIPLIER):
    df['H-L'] = df['high'] - df['low']
    df['H-C'] = abs(df['high'] - df['close'].shift())
    df['L-C'] = abs(df['low'] - df['close'].shift())
    df['TR'] = df[['H-L', 'H-C', 'L-C']].max(axis=1)
    df['ATR'] = df['TR'].rolling(period).mean()

    df['upperband'] = (df['high'] + df['low']) / 2 + multiplier * df['ATR']
    df['lowerband'] = (df['high'] + df['low']) / 2 - multiplier * df['ATR']

    df['supertrend'] = 0.0
    for i in range(period, len(df)):
        if df['close'][i] > df['upperband'][i-1]:
            df['supertrend'][i] = df['lowerband'][i]
        elif df['close'][i] < df['lowerband'][i-1]:
            df['supertrend'][i] = df['upperband'][i]
        else:
            df['supertrend'][i] = df['supertrend'][i-1]
    return df

def rsi(df, period=RSI_PERIOD):
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))
    return df

# ===== STRATEGY CHECK =====
def strategy(df):
    latest = df.iloc[-1]
    prev = df.iloc[-2]

    rsi_ma = df['rsi'].rolling(RSI_MA_PERIOD).mean().iloc[-1]

    buy_signal = (
        (latest['close'] > latest['supertrend']) and
        (latest['rsi'] > rsi_ma) and
        (latest['volume'] > prev['volume']) and
        (latest['close'] > latest['open']) and
        (latest['close'] > prev['high'])
    )

    return buy_signal

# ===== MAIN LOOP =====
while True:
    print("Fetching data...")
    ohlcv = exchange.fetch_ohlcv(SYMBOL, TIMEFRAME, limit=FETCH_LIMIT)
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])

    df = supertrend(df)
    df = rsi(df)

    if strategy(df):
        print("BUY SIGNAL DETECTED 🚀")
        # exchange.create_market_buy_order(SYMBOL, 0.001)  # Uncomment when ready
    else:
        print("No trade signal.")

    time.sleep(60)  # Wait 1 minute before checking again
