# -*- coding: utf-8 -*-
import requests
import pandas as pd
from datetime import datetime
import os

# ==================== 配置区 ====================
chat_id = "-4966987679"
TOKEN = "8444348700:AAGqkeUUuB_0rI_4qIaJxrTylpRGh020wU0"
BASE_URL = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
LOCK_FILE = "155_multi_signal_lock.txt"

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
            if (now - tm).total_seconds() < 3600:
                valid.append((t, tm))
                if t == sig_type:
                    return False

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
    df["e8"]  = df["close"].ewm(span=8, adjust=False).mean()
    df["e21"] = df["close"].ewm(span=21, adjust=False).mean()
    df["e55"] = df["close"].ewm(span=55, adjust=False).mean()

    df["sma20"] = df["close"].rolling(20).mean()
    df["std20"] = df["close"].rolling(20).std()
    df["upper"] = df["sma20"] + 2 * df["std20"]
    df["lower"] = df["sma20"] - 2 * df["std20"]

    df["vol20"] = df["vol"].rolling(20).mean()
    return df

# ==================== 双顶 / 双底 ====================
def detect_double_pattern(df, window=40, tolerance=0.03):
    if len(df) < window + 10:
        return 'none', None

    hist = df.iloc[:-1]   # ★ 不包含当前K
    current_price = df["close"].iloc[-1]

    highs = hist["high"].values
    lows  = hist["low"].values

    peaks, troughs = [], []

    for i in range(3, len(highs)-3):
        if highs[i] == highs[i-3:i+4].max():
            peaks.append((i, highs[i]))

    for i in range(3, len(lows)-3):
        if lows[i] == lows[i-3:i+4].min():
            troughs.append((i, lows[i]))

    if len(peaks) >= 2:
        p2_idx, p2 = peaks[-1]
        for j in range(len(peaks)-2, -1, -1):
            p1_idx, p1 = peaks[j]
            if 8 <= p2_idx - p1_idx <= window and abs(p1 - p2)/max(p1,p2) <= tolerance:
                neckline = hist["low"].iloc[p1_idx:p2_idx+1].min()
                if current_price < neckline * 0.99:
                    return "double_top_confirmed", {
                        "peak1": p1, "peak2": p2, "neckline": neckline
                    }
                return "double_top_forming", {
                    "peak1": p1, "peak2": p2, "neckline": neckline
                }

    if len(troughs) >= 2:
        t2_idx, t2 = troughs[-1]
        for j in range(len(troughs)-2, -1, -1):
            t1_idx, t1 = troughs[j]
            if 8 <= t2_idx - t1_idx <= window and abs(t1 - t2)/max(t1,t2) <= tolerance:
                neckline = hist["high"].iloc[t1_idx:t2_idx+1].max()
                if current_price > neckline * 1.01:
                    return "double_bottom_confirmed", {
                        "trough1": t1, "trough2": t2, "neckline": neckline
                    }
                return "double_bottom_forming", {
                    "trough1": t1, "trough2": t2, "neckline": neckline
                }

    return "none", None

# ==================== 主程序 ====================
def main():
    df15 = add_tech(get("15m")).dropna().reset_index(drop=True)
    if len(df15) < 120:
        return

    l15 = df15.iloc[-1]
    price = l15["close"]
    ts = l15["ts"].strftime("%m-%d %H:%M")

    pattern, details = detect_double_pattern(df15)

    if pattern == "double_top_confirmed" and can_send("DT_CONF"):
        send(f"""【15m 双顶确认·强空】
{ts}  ${price:.1f}
跌破颈线 {details['neckline']:.1f}
建议：清多 / 试空""")
        record("DT_CONF")

    elif pattern == "double_bottom_confirmed" and can_send("DB_CONF"):
        send(f"""【15m 双底确认·强多】
{ts}  ${price:.1f}
突破颈线 {details['neckline']:.1f}
建议：顺势做多""")
        record("DB_CONF")

    print(f"[{datetime.now().strftime('%H:%M:%S')}] BTC {price:.0f} | {pattern}")

if __name__ == "__main__":
    main()