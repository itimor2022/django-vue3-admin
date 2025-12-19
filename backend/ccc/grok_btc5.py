# -*- coding: utf-8 -*-
import requests
import pandas as pd
import numpy as np
from datetime import datetime
import os

# ==================== 配置区 ====================
chat_id = "-4966987679"
TOKEN = "8444348700:AAGqkeUUuB_0rI_4qIaJxrTylpRGh020wU0"
BASE_URL = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
LOCK_FILE = "1555_multi_signal_lock.txt"   # 防刷屏（同类信号1小时内只发1次）

# ==================== 工具函数 ====================
def send(msg):
    try:
        requests.post(BASE_URL, json={"chat_id": chat_id, "text": msg, "parse_mode": "HTML", "disable_web_page_preview": True}, timeout=10)
    except:
        pass

def can_send(sig_type):
    if not os.path.exists(LOCK_FILE):
        return True
    try:
        with open(LOCK_FILE) as f:
            lines = f.read().strip().split("\n")
            for line in lines:
                if not line: continue
                t, tm = line.split("|")
                if t == sig_type and (datetime.now() - datetime.fromisoformat(tm)).total_seconds() < 3600:
                    return False
        return True
    except:
        return True

def record(sig_type):
    with open(LOCK_FILE, "a", encoding="utf-8") as f:
        f.write(f"{sig_type}|{datetime.now().isoformat()}\n")

# ==================== K线 & 指标 ====================
def get(bar="15m"):
    url = "https://www.okx.com/api/v5/market/candles"
    p = {"instId": "BTC-USDT", "bar": bar, "limit": 300}
    try:
        d = requests.get(url, params=p, timeout=10).json()["data"]
        df = pd.DataFrame(d, columns=["ts","o","h","l","c","vol","volCcy","volCcyQuote","confirm"])
        df["ts"] = pd.to_datetime(df["ts"].astype(int), unit='ms')
        df = df.astype({"o":float,"h":float,"l":float,"c":float,"vol":float})
        df = df[["ts","open","high","low","close","vol"]].sort_values("ts").reset_index(drop=True)
        return df
    except:
        return pd.DataFrame()

def add_tech(df):
    # 布林带
    df["sma20"] = df["close"].rolling(20).mean()          # 中轨
    df["std20"] = df["close"].rolling(20).std()
    df["upper"] = df["sma20"] + 2 * df["std20"]
    df["lower"] = df["sma20"] - 2 * df["std20"]

    # 成交量均线（可选后续加放量过滤）
    df["vol20"] = df["vol"].rolling(20).mean()

    return df

# ==================== 寻找最近高点 / 低点 ====================
def find_recent_high(df, lookback=60):
    recent = df.iloc[-lookback:]
    idx = recent["high"].idxmax()
    return df.loc[idx, "high"]

def find_recent_low(df, lookback=60):
    recent = df.iloc[-lookback:]
    idx = recent["low"].idxmin()
    return df.loc[idx, "low"]

# ==================== 主程序（15分钟 多空双信号） ====================
def main():
    df = add_tech(get("15m"))
    if len(df) < 100:
        return

    current = df.iloc[-1]   # 当前最新K线
    prev    = df.iloc[-2]   # 前一根K线

    price = current["close"]
    ts    = current["ts"].strftime("%m-%d %H:%M")

    # ========== 空头信号：阴线下穿中轨 + 从最近高点已跌超1.1% ==========
    is_bearish_candle = current["close"] < current["open"]
    cross_down_mid = (prev["close"] >= prev["sma20"]) and (current["close"] < current["sma20"])

    recent_high = find_recent_high(df, lookback=60)
    decline_percent = (price - recent_high) / recent_high * 100

    if is_bearish_candle and cross_down_mid and decline_percent <= -1.1 and can_send("BEAR_SIGNAL"):
        send(f"""【15m 空头转折信号】阴线下穿中轨 + 已回调超1.1%
{ts}  ${price:.1f}
• 当前阴线实体下穿布林中轨
• 距最近高点 {recent_high:.1f} 已下跌 {abs(decline_percent):.2f}%
建议：可短空或减多仓
止损设最近高点上方，目标下轨附近""")
        record("BEAR_SIGNAL")

    # ========== 多头信号：阳线上穿中轨 + 比最近低点已涨超1.1% ==========
    is_bullish_candle = current["close"] > current["open"]
    cross_up_mid = (prev["close"] <= prev["sma20"]) and (current["close"] > current["sma20"])

    recent_low = find_recent_low(df, lookback=60)
    rise_percent = (price - recent_low) / recent_low * 100

    if is_bullish_candle and cross_up_mid and rise_percent >= 1.1 and can_send("BULL_SIGNAL"):
        send(f"""【15m 多头启动信号】阳线上穿中轨 + 已反弹超1.1%
{ts}  ${price:.1f}
• 当前阳线实体上穿布林中轨
• 距最近低点 {recent_low:.1f} 已上涨 {rise_percent:.2f}%
建议：可短多或加多仓
止损设最近低点下方，目标上轨附近""")
        record("BULL_SIGNAL")

    # 调试输出
    print(f"[{datetime.now().strftime('%H:%M:%S')}] BTC ${price:.0f} | "
          f"距高点: {decline_percent:.2f}% | 距低点: +{rise_percent:.2f}% | "
          f"空信号: {is_bearish_candle and cross_down_mid and decline_percent <= -1.1} | "
          f"多信号: {is_bullish_candle and cross_up_mid and rise_percent >= 1.1}")

if __name__ == '__main__':
    main()