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
LOCK_SECONDS = 1800  # 30分钟冷却（可根据需要调短到 900=15min）

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

    # 清理过期
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
    params = {"instId": "BTC-USDT", "bar": bar, "limit": 500}  # 拉多一点数据
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
    # 布林带
    df["sma20"] = df["close"].rolling(20).mean()
    df["std20"] = df["close"].rolling(20).std()
    df["upper"] = df["sma20"] + 2 * df["std20"]
    df["lower"] = df["sma20"] - 2 * df["std20"]
    df["bb_width"] = (df["upper"] - df["lower"]) / df["sma20"] * 100  # 布林带宽度%

    # EMA 快慢线
    df["ema9"] = df["close"].ewm(span=9, adjust=False).mean()
    df["ema21"] = df["close"].ewm(span=21, adjust=False).mean()

    return df

def find_recent_high(df, lookback=80):
    return df.iloc[-lookback-1:-1]["high"].max()

def find_recent_low(df, lookback=80):
    return df.iloc[-lookback-1:-1]["low"].min()

# ==================== 信号逻辑 ====================
def main():
    df = add_tech(get("15m"))
    df = df.dropna().reset_index(drop=True)

    if len(df) < 100:
        return

    current = df.iloc[-1]
    prev = df.iloc[-2]
    prev2 = df.iloc[-3]  # 用于更严格的交叉判断

    price = current["close"]
    ts = current["ts"].strftime("%m-%d %H:%M")

    # 公共变量
    recent_high = find_recent_high(df)
    recent_low = find_recent_low(df)
    decline = (price - recent_high) / recent_high * 100
    rise = (price - recent_low) / recent_low * 100

    # ============ 信号 1：经典布林中轨穿越（降低到 0.75%） ============
    # 空头
    if (current["close"] < current["open"] and
        prev["close"] >= prev["sma20"] and current["close"] < current["sma20"] and
        decline <= -0.75 and can_send("BEAR_CROSS")):
        send(f"""<b>【15m 空头穿越】</b> {ts} ${price:.1f}
阴线下穿布林中轨 • 距高点回调 {abs(decline):.2f}%
建议：短空 / 减多
止损：{recent_high:.1f} 上方""")
        record("BEAR_CROSS")

    # 多头
    if (current["close"] > current["open"] and
        prev["close"] <= prev["sma20"] and current["close"] > current["sma20"] and
        rise >= 0.75 and can_send("BULL_CROSS")):
        send(f"""<b>【15m 多头穿越】</b> {ts} ${price:.1f}
阳线上穿布林中轨 • 距低点反弹 {rise:.2f}%
建议：短多 / 加多
止损：{recent_low:.1f} 下方""")
        record("BULL_CROSS")

    # ============ 信号 2：布林带挤压后突破（宽度 < 2% 后突破） ============
    squeeze = prev["bb_width"] < 2.0 and current["bb_width"] > prev["bb_width"]

    if squeeze and current["close"] > current["upper"] and can_send("BB_UP_BREAK"):
        send(f"""<b>【15m 布林上轨突破】强信号</b> {ts} ${price:.1f}
布林带挤压后向上突破
距低点已涨 {rise:.2f}%
建议：激进追多""")
        record("BB_UP_BREAK")

    if squeeze and current["close"] < current["lower"] and can_send("BB_DN_BREAK"):
        send(f"""<b>【15m 布林下轨突破】强信号</b> {ts} ${price:.1f}
布林带挤压后向下突破
距高点已跌 {abs(decline):.2f}%
建议：激进追空""")
        record("BB_DN_BREAK")

    # ============ 信号 3：EMA9/21 金叉死叉 ============
    golden_cross = (prev2["ema9"] <= prev2["ema21"] and
                    prev["ema9"] > prev["ema21"] and
                    current["close"] > current["sma20"])
    death_cross = (prev2["ema9"] >= prev2["ema21"] and
                   prev["ema9"] < prev["ema21"] and
                   current["close"] < current["sma20"])

    if golden_cross and rise >= 0.7 and can_send("EMA_GOLDEN"):
        send(f"""<b>【15m EMA金叉】</b> {ts} ${price:.1f}
EMA9 上穿 EMA21 • 反弹 {rise:.2f}%
建议：短多 / 加多""")
        record("EMA_GOLDEN")

    if death_cross and decline <= -0.7 and can_send("EMA_DEATH"):
        send(f"""<b>【15m EMA死叉】</b> {ts} ${price:.1f}
EMA9 下穿 EMA21 • 回调 {abs(decline):.2f}%
建议：短空 / 减多""")
        record("EMA_DEATH")

    # ============ 信号 4：靠近上下轨反弹 ============
    # 接近下轨 + 阳线 + 反弹力度
    if (current["close"] < current["lower"] * 1.005 and
        current["close"] > current["open"] and
        rise >= 1.0 and can_send("BULL_BOUNCE")):
        send(f"""【15m 下轨支撑反弹】 {ts} ${price:.1f}
阳线 + 距低点反弹 {rise:.2f}%
建议：短多 / 低吸""")
        record("BULL_BOUNCE")

    # 接近上轨 + 阴线 + 回调
    if (current["close"] > current["upper"] * 0.995 and
        current["close"] < current["open"] and
        decline <= -1.0 and can_send("BEAR_REJECT")):
        send(f"""【15m 上轨遇阻回调】 {ts} ${price:.1f}
阴线 + 距高点回调 {abs(decline):.2f}%
建议：短空 / 高抛""")
        record("BEAR_REJECT")

    print(f"[{datetime.now().strftime('%H:%M:%S')}] BTC {price:.0f} | "
          f"高:{decline:5.2f}% | 低:+{rise:5.2f}% | BB宽:{current['bb_width']:.2f}%")

if __name__ == "__main__":
    main()