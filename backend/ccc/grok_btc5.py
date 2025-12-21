# -*- coding: utf-8 -*-
import requests
import pandas as pd
from datetime import datetime, timedelta
import os

# ==================== 配置区 ====================
chat_id = "-5068436114"
TOKEN = "8444348700:AAGqkeUUuB_0rI_4qIaJxrTylpRGh020wU0"
BASE_URL = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
LOCK_FILE = "1555_multi_signal_lock.txt"
LOCK_SECONDS = 3600

# ==================== 工具函数 ====================
def send(msg):
    try:
        requests.post(
            BASE_URL,
            json={
                "chat_id": chat_id,
                "text": msg,
                "parse_mode": "HTML",
                "disable_web_page_preview": True
            },
            timeout=10
        )
    except:
        pass

def can_send(sig_type):
    if not os.path.exists(LOCK_FILE):
        return True

    now = datetime.now()
    valid = []

    with open(LOCK_FILE, encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            t, tm = line.strip().split("|")
            tm = datetime.fromisoformat(tm)
            if (now - tm).total_seconds() < LOCK_SECONDS:
                valid.append((t, tm))
                if t == sig_type:
                    return False

    # 清理旧记录
    with open(LOCK_FILE, "w", encoding="utf-8") as f:
        for t, tm in valid:
            f.write(f"{t}|{tm.isoformat()}\n")

    return True

def record(sig_type):
    with open(LOCK_FILE, "a", encoding="utf-8") as f:
        f.write(f"{sig_type}|{datetime.now().isoformat()}\n")

# ==================== K线 & 指标 ====================
def get(bar="15m"):
    url = "https://www.okx.com/api/v5/market/candles"
    params = {"instId": "BTC-USDT", "bar": bar, "limit": 300}
    try:
        d = requests.get(url, params=params, timeout=10).json()["data"]
        df = pd.DataFrame(
            d,
            columns=["ts","open","high","low","close","vol","volCcy","volCcyQuote","confirm"]
        )
        df["ts"] = pd.to_datetime(df["ts"].astype(int), unit="ms")
        df = df.astype({
            "open": float,
            "high": float,
            "low": float,
            "close": float,
            "vol": float
        })
        return df.sort_values("ts").reset_index(drop=True)
    except:
        return pd.DataFrame()

def add_tech(df):
    df["sma20"] = df["close"].rolling(20).mean()
    df["std20"] = df["close"].rolling(20).std()
    df["upper"] = df["sma20"] + 2 * df["std20"]
    df["lower"] = df["sma20"] - 2 * df["std20"]
    return df

def find_recent_high(df, lookback=60):
    return df.iloc[-lookback-1:-1]["high"].max()

def find_recent_low(df, lookback=60):
    return df.iloc[-lookback-1:-1]["low"].min()

# ==================== 主程序 ====================
def main():
    df = add_tech(get("15m"))
    df = df.dropna().reset_index(drop=True)

    if len(df) < 80:
        return

    current = df.iloc[-1]
    prev = df.iloc[-2]

    price = current["close"]
    ts = current["ts"].strftime("%m-%d %H:%M")

    # ========= 空头 =========
    is_bearish = current["close"] < current["open"]
    cross_down = prev["close"] >= prev["sma20"] and current["close"] < current["sma20"]

    recent_high = find_recent_high(df)
    decline = (price - recent_high) / recent_high * 100

    if is_bearish and cross_down and decline <= -1.1 and can_send("BEAR_SIGNAL"):
        send(f"""【15m 空头转折信号】
{ts}  ${price:.1f}
• 阴线下穿布林中轨
• 距高点 {recent_high:.1f} 已回调 {abs(decline):.2f}%
建议：短空 / 减多
止损：高点上方
目标：下轨""")
        record("BEAR_SIGNAL")

    # ========= 多头 =========
    is_bullish = current["close"] > current["open"]
    cross_up = prev["close"] <= prev["sma20"] and current["close"] > current["sma20"]

    recent_low = find_recent_low(df)
    rise = (price - recent_low) / recent_low * 100

    if is_bullish and cross_up and rise >= 1.1 and can_send("BULL_SIGNAL"):
        send(f"""【15m 多头启动信号】
{ts}  ${price:.1f}
• 阳线上穿布林中轨
• 距低点 {recent_low:.1f} 已反弹 {rise:.2f}%
建议：短多 / 加多
止损：低点下方
目标：上轨""")
        record("BULL_SIGNAL")

    print(f"[{datetime.now().strftime('%H:%M:%S')}] BTC {price:.0f} | 高:{decline:.2f}% | 低:+{rise:.2f}%")

if __name__ == "__main__":
    main()