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
LOCK_FILE = "155_multi_signal_lock.txt"   # 防刷屏（同类信号1小时内只发1次）

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
        df = df[["ts","open","high","low","close","vol"]].rename(columns={"open":"o","high":"h","low":"l","close":"c"})
        df = df.sort_values("ts").reset_index(drop=True)
        return df
    except:
        return pd.DataFrame()

def add_tech(df):
    df["e8"]  = df["close"].ewm(span=8,  adjust=False).mean()
    df["e21"] = df["close"].ewm(span=21, adjust=False).mean()
    df["e55"] = df["close"].ewm(span=55, adjust=False).mean()

    df["sma20"] = df["close"].rolling(20).mean()
    df["std20"] = df["close"].rolling(20).std()
    df["upper"] = df["sma20"] + 2*df["std20"]
    df["lower"] = df["sma20"] - 2*df["std20"]

    df["vol20"] = df["vol"].rolling(20).mean()
    df["v1"] = df["vol"] > df["vol20"] * 1.6   # 轻度放量
    df["v2"] = df["vol"] > df["vol20"] * 2.2   # 重度放量

    return df

# ==================== 双顶 / 双底 检测函数（仅15m） ====================
def detect_double_pattern(df, window=40, tolerance=0.03):
    """
    在15m df中检测最近的双顶（M头）或双底（W底）
    返回: ('none' | 'double_top_forming' | 'double_top_confirmed' | 'double_bottom_forming' | 'double_bottom_confirmed', details)
    """
    if len(df) < window + 10:
        return 'none', None

    highs = df['high'].values
    peaks = []
    for i in range(3, len(highs)-3):
        if (highs[i] == highs[i-3:i+4].max()):  # 更宽松的局部高点判断
            peaks.append((i, highs[i]))

    lows = df['low'].values
    troughs = []
    for i in range(3, len(lows)-3):
        if (lows[i] == lows[i-3:i+4].min()):
            troughs.append((i, lows[i]))

    current_price = df['close'].iloc[-1]

    # 双顶检测
    if len(peaks) >= 2:
        p2_idx, p2 = peaks[-1]
        for j in range(len(peaks)-2, -1, -1):
            p1_idx, p1 = peaks[j]
            if 8 <= (p2_idx - p1_idx) <= window and abs(p1 - p2)/max(p1,p2) <= tolerance:
                neckline = df['low'][p1_idx:p2_idx+1].min()
                details = {'type': 'double_top', 'peak1': p1, 'peak2': p2, 'neckline': neckline,
                           'peak1_idx': p1_idx, 'peak2_idx': p2_idx}
                if current_price < neckline * 0.99:
                    return 'double_top_confirmed', details
                else:
                    return 'double_top_forming', details

    # 双底检测
    if len(troughs) >= 2:
        t2_idx, t2 = troughs[-1]
        for j in range(len(troughs)-2, -1, -1):
            t1_idx, t1 = troughs[j]
            if 8 <= (t2_idx - t1_idx) <= window and abs(t1 - t2)/max(t1,t2) <= tolerance:
                neckline = df['high'][t1_idx:t2_idx+1].max()
                details = {'type': 'double_bottom', 'trough1': t1, 'trough2': t2, 'neckline': neckline,
                           'trough1_idx': t1_idx, 'trough2_idx': t2_idx}
                if current_price > neckline * 1.01:
                    return 'double_bottom_confirmed', details
                else:
                    return 'double_bottom_forming', details

    return 'none', None

# ==================== 主程序（只用15分钟K线） ====================
def main():
    df15 = add_tech(get("15m"))
    if len(df15) < 100:
        return

    l15 = df15.iloc[-1]
    price = l15["close"]
    ts    = l15["ts"].strftime("%m-%d %H:%M")
    vr    = l15["vol"]/l15["vol20"] if l15["vol20"] > 0 else 1

    # 双顶/双底信号检测（仅15m）
    pattern, details = detect_double_pattern(df15, window=40, tolerance=0.03)

    if pattern == 'double_top_confirmed' and can_send("DT_CONF"):
        send(f"""【15m 双顶确认·强空转折】趋势反转向下！
{ts}  ${price:.1f}
双顶高点 ≈{details['peak1']:.1f} / {details['peak2']:.1f}
已有效跌破颈线 {details['neckline']:.1f}
建议：清多仓，可短空或观望
目标下探 {price * 0.90:.1f} ~ {price * 0.85:.1f}""")
        record("DT_CONF")

    elif pattern == 'double_top_forming' and can_send("DT_FORM"):
        send(f"""【15m 双顶形成中】警惕短期见顶
{ts}  ${price:.1f}
双顶高点 ≈{details['peak1']:.1f} / {details['peak2']:.1f}
颈线位 {details['neckline']:.1f}
若跌破颈线 → 短线转空，注意减仓""")
        record("DT_FORM")

    elif pattern == 'double_bottom_confirmed' and can_send("DB_CONF"):
        send(f"""【15m 双底确认·强多启动】短线反转向上！
{ts}  ${price:.1f}
双底低点 ≈{details['trough1']:.1f} / {details['trough2']:.1f}
已有效突破颈线 {details['neckline']:.1f}
建议：大胆做多，短线主升概率极高
目标上探 {price * 1.10:.1f} ~ {price * 1.15:.1f}+""")
        record("DB_CONF")

    elif pattern == 'double_bottom_forming' and can_send("DB_FORM"):
        send(f"""【15m 双底形成中】潜在短期底部
{ts}  ${price:.1f}
双底低点 ≈{details['trough1']:.1f} / {details['trough2']:.1f}
颈线位 {details['neckline']:.1f}
若突破颈线 → 短线转多，可提前埋伏""")
        record("DB_FORM")

    # 调试输出
    print(f"[{datetime.now().strftime('%H:%M:%S')}] BTC ${price:.0f} | 15m Pattern: {pattern}")

if __name__ == '__main__':
    main()