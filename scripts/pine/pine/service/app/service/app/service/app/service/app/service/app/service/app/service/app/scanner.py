import pandas as pd
import ta
from .executor import EXCHANGE

def fetch_ohlcv(symbol, timeframe='5m', limit=200):
    data = EXCHANGE.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
    df = pd.DataFrame(data, columns=['ts','open','high','low','close','volume'])
    df['open'] = df['open'].astype(float)
    df['high'] = df['high'].astype(float)
    df['low'] = df['low'].astype(float)
    df['close'] = df['close'].astype(float)
    df['volume'] = df['volume'].astype(float)
    return df

def compute_supertrend(df, atr_period=14, multiplier=1.4):
    # ATR
    atr = ta.volatility.AverageTrueRange(high=df['high'], low=df['low'], close=df['close'], window=atr_period).average_true_range()
    hl2 = (df['high'] + df['low'])/2
    upper = hl2 + multiplier * atr
    lower = hl2 - multiplier * atr

    supertrend = [0.0] * len(df)
    in_uptrend = True
    supertrend[0] = lower.iloc[0]
    for i in range(1, len(df)):
        if df['close'].iat[i] > upper.iat[i-1]:
            in_uptrend = True
        elif df['close'].iat[i] < lower.iat[i-1]:
            in_uptrend = False
        supertrend[i] = lower.iat[i] if in_uptrend else upper.iat[i]
    df['supertrend'] = supertrend
    return df

def strategy_signal(df):
    # Compute indicators similarly to Pine
    df = compute_supertrend(df)
    df['rsi'] = ta.momentum.RSIIndicator(close=df['close'], window=21).rsi()
    df['rsi_sma'] = df['rsi'].rolling(window=16).mean()

    latest = df.iloc[-1]
    prev = df.iloc[-2]

    # cross above supertrend (ensure prior <= st and now > st)
    cross_up = (df['close'].iat[-2] <= df['supertrend'].iat[-2]) and (df['close'].iat[-1] > df['supertrend'].iat[-1])

    cond = (
        cross_up and
        (latest['rsi'] > latest['rsi_sma']) and
        (latest['volume'] > prev['volume']) and
        (latest['close'] > latest['open']) and
        (latest['close'] > prev['high'])
    )

    # naive expected return estimate: mean next-candle return from history
    future_returns = (df['close'].shift(-1) / df['close'] - 1).dropna()
    expected_return = float(future_returns.tail(50).mean()) if not future_returns.empty else 0.0

    return {"valid": bool(cond), "expected_return": expected_return}
