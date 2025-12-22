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
LOCK_SECONDS = 1800  # 30分钟冷却，可调短到900（15min）

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

    with open(LOCK_FILE, "w", encoding="utf-8") as f:
        for t, tm in valid:
            f.write(f"{t}|{tm.isoformat()}\n")

    return True

def record(sig_type):
    with open(LOCK_FILE, "a", encoding="utf-8") as f:
        f.write(f"{sig_type}|{datetime.now().isoformat()}\n")

# ==================== K线 & 指标 ====================
def get(bar="15m", limit=500):
    url = "https://www.okx.com/api/v5/market/candles"
    params = {"instId": "BTC-USDT", "bar": bar, "limit": limit}
    try:
        d = requests.get(url, params=params, timeout=10).json()["data"]
        df = pd.DataFrame(
            d,
            columns=["ts","open","high","low","close","vol","volCcy","volCcyQuote","confirm"]
        )
        df["ts"] = pd.to_datetime(df["ts"].astype(int), unit='ms') + pd.Timedelta(hours=7)  # 亚洲时间
        df = df.astype({
            "open": float, "high": float, "low": float, "close": float, "vol": float
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

# ==================== 形态检测（增强版） ====================
def detect_patterns(df, window=60, tolerance=0.05):
    if len(df) < window + 20:
        return "none", None

    hist = df.iloc[:-1]  # 不含当前K
    current_price = df["close"].iloc[-1]

    highs = hist["high"].values
    lows = hist["low"].values

    peaks = []
    troughs = []

    # 找局部高点和低点
    for i in range(5, len(highs)-5):
        if highs[i] == highs[i-5:i+6].max():
            peaks.append((i, highs[i]))
    for i in range(5, len(lows)-5):
        if lows[i] == lows[i-5:i+6].min():
            troughs.append((i, lows[i]))

    # --- 双顶/双底 ---
    if len(peaks) >= 2:
        p2_idx, p2 = peaks[-1]
        for j in range(len(peaks)-2, -1, -1):
            p1_idx, p1 = peaks[j]
            span = p2_idx - p1_idx
            if 10 <= span <= window and abs(p1 - p2)/max(p1,p2) <= tolerance:
                neckline = hist["low"].iloc[p1_idx:p2_idx+1].min()
                if current_price < neckline * 0.995:
                    return "double_top_confirmed", {"neckline": neckline, "type": "DT"}
                elif abs(current_price - neckline)/neckline < 0.01:
                    return "double_top_near_break", {"neckline": neckline, "type": "DT"}
                else:
                    return "double_top_forming", {"neckline": neckline, "type": "DT"}

    if len(troughs) >= 2:
        t2_idx, t2 = troughs[-1]
        for j in range(len(troughs)-2, -1, -1):
            t1_idx, t1 = troughs[j]
            span = t2_idx - t1_idx
            if 10 <= span <= window and abs(t1 - t2)/max(t1,t2) <= tolerance:
                neckline = hist["high"].iloc[t1_idx:t2_idx+1].max()
                if current_price > neckline * 1.005:
                    return "double_bottom_confirmed", {"neckline": neckline, "type": "DB"}
                elif abs(current_price - neckline)/neckline < 0.01:
                    return "double_bottom_near_break", {"neckline": neckline, "type": "DB"}
                else:
                    return "double_bottom_forming", {"neckline": neckline, "type": "DB"}

    # --- 简单头肩顶/底（3个峰/谷） ---
    if len(peaks) >= 3:
        p3_idx, p3 = peaks[-1]
        p2_idx, p2 = peaks[-2]
        p1_idx, p1 = peaks[-3]
        if 15 <= p3_idx - p1_idx <= window*1.5:
            if abs(p1 - p3)/max(p1,p3) <= tolerance*1.2 and p2 > max(p1,p3)*1.005:
                neckline = hist["low"].iloc[p1_idx:p3_idx+1].min()
                if current_price < neckline * 0.995:
                    return "head_shoulder_top_confirmed", {"neckline": neckline}
                elif abs(current_price - neckline)/neckline < 0.01:
                    return "head_shoulder_top_near_break", {"neckline": neckline}

    if len(troughs) >= 3:
        t3_idx, t3 = troughs[-1]
        t2_idx, t2 = troughs[-2]
        t1_idx, t1 = troughs[-1]
        if 15 <= t3_idx - t1_idx <= window*1.5:
            if abs(t1 - t3)/max(t1,t3) <= tolerance*1.2 and t2 < min(t1,t3)*0.995:
                neckline = hist["high"].iloc[t1_idx:t3_idx+1].max()
                if current_price > neckline * 1.005:
                    return "head_shoulder_bottom_confirmed", {"neckline": neckline}
                elif abs(current_price - neckline)/neckline < 0.01:
                    return "head_shoulder_bottom_near_break", {"neckline": neckline}

    return "none", None

# ==================== 主程序 ====================
def main():
    df15 = add_tech(get("15m", limit=500)).dropna().reset_index(drop=True)
    if len(df15) < 150:
        return

    l15 = df15.iloc[-1]
    price = l15["close"]
    ts = l15["ts"].strftime("%m-%d %H:%M")

    pattern, details = detect_patterns(df15)

    msg = ""
    sig_type = ""

    if pattern == "double_top_confirmed" and can_send("DT_CONF"):
        msg = f"""<b>【15m 双顶确认·强空】</b> {ts} ${price:.1f}
跌破颈线 {details['neckline']:.1f}
建议：清多 / 试空"""
        sig_type = "DT_CONF"

    elif pattern == "double_bottom_confirmed" and can_send("DB_CONF"):
        msg = f"""<b>【15m 双底确认·强多】</b> {ts} ${price:.1f}
突破颈线 {details['neckline']:.1f}
建议：顺势做多"""
        sig_type = "DB_CONF"

    elif pattern == "double_top_near_break" and can_send("DT_NEAR"):
        msg = f"""【15m 双顶接近突破】 {ts} ${price:.1f}
颈线 {details['neckline']:.1f} 附近
警惕空头信号"""
        sig_type = "DT_NEAR"

    elif pattern == "double_bottom_near_break" and can_send("DB_NEAR"):
        msg = f"""【15m 双底接近突破】 {ts} ${price:.1f}
颈线 {details['neckline']:.1f} 附近
警惕多头信号"""
        sig_type = "DB_NEAR"

    elif pattern == "head_shoulder_top_confirmed" and can_send("HST_CONF"):
        msg = f"""<b>【15m 头肩顶确认·强空】</b> {ts} ${price:.1f}
跌破颈线 {details['neckline']:.1f}
建议：清多 / 试空"""
        sig_type = "HST_CONF"

    elif pattern == "head_shoulder_bottom_confirmed" and can_send("HSB_CONF"):
        msg = f"""<b>【15m 头肩底确认·强多】</b> {ts} ${price:.1f}
突破颈线 {details['neckline']:.1f}
建议：顺势做多"""
        sig_type = "HSB_CONF"

    if msg and sig_type:
        send(msg)
        record(sig_type)

    print(f"[{datetime.now().strftime('%H:%M:%S')}] BTC {price:.0f} | {pattern}")

if __name__ == "__main__":
    main()