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
LOCK_FILE = "multi_signal_lock.txt"   # 防刷屏（同类信号1小时内只发1次）

# ==================== 工具函数 ====================
def send(msg):
    try:
        requests.post(BASE_URL, json={"chat_id": chat_id, "text": msg, "parse_mode": "HTML", "disable_web_page_preview": True}, timeout=10)
    except:
        pass

def can_send(sig_type):  # sig_type = "S1","S2",..."W1" 等
    if not os.path.exists(LOCK_FILE):
        return True
    try:
        with open(LOCK_FILE) as f:
            for line in f.read().strip().split("\n"):
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
    df["e8"]  = df["close"].ewm(span=8,  adjust=False).mean()
    df["e21"] = df["close"].ewm(span=21, adjust=False).mean()
    df["e55"] = df["close"].ewm(span=55, adjust=False).mean()

    df["sma20"] = df["close"].rolling(20).mean()
    df["std20"] = df["close"].rolling(20).std()
    df["upper"] = df["sma20"] + 2*df["std20"]
    df["lower"] = df["sma20"] - 2*df["std20"]
    df["bw"] = df["upper"] - df["lower"]
    df["bw_exp"] = df["bw"] > df["bw"].shift(1) * 1.06

    df["vol20"] = df["vol"].rolling(20).mean()
    df["v1"] = df["vol"] > df["vol20"] * 1.6   # 轻度放量
    df["v2"] = df["vol"] > df["vol20"] * 2.2   # 重度放量

    df["up"] = df["close"] > df["upper"]
    df["dn"] = df["close"] < df["lower"]

    df["gold"] = (df["e8"] > df["e21"]) & (df["e8"].shift(1) <= df["e21"].shift(1))
    df["dead"] = (df["e8"] < df["e21"]) & (df["e8"].shift(1) >= df["e21"].shift(1))

    return df

# ==================== 主程序 ====================
def main():
    df15 = add_tech(get("15m"))
    df30 = add_tech(get("30m"))
    if len(df15)<100 or len(df30)<80:
        return

    l15 = df15.iloc[-1]
    p15 = df15.iloc[-2]
    l30 = df30.iloc[-1]

    price = l15["close"]
    ts    = l15["ts"].strftime("%m-%d %H:%M")
    vr    = l15["vol"]/l15["vol20"]

    # ====================== 信号大全（由强到弱） ======================
    # S1级：核弹级主升浪起点（一天1~2次）
    if (l15["gold"] and l15["v2"] and l15["bw_exp"] and l15["up"] and
        l15["low"] >= p15["low"] and l30["e8"] > l30["e21"] > l30["e55"] and can_send("S1")):
        send(f"""【S1 核弹级多头】主升浪已启动！
{ts}  ${price:.1f}
• 15m金叉+重度放量{vr:.2f}x+破上轨
• 30m三线多头排列
立即全仓或分批进多！目标+15%~40%""")
        record("S1")

    # S2级：强趋势金叉（一天3~6次）
    elif (l15["gold"] and l15["v1"] and l15["bw_exp"] and l30["e8"]>l30["e21"] and can_send("S2")):
        send(f"""【S2 强势金叉】短线多单机会
{ts}  ${price:.1f}
• 15m金叉+放量{vr:.2f}x+布林张口
• 30m多头趋势
建议：现价或回踩EMA8进多""")
        record("S2")

    # S3级：突破上轨放量（追涨信号）
    if (l15["up"] and l15["v1"] and l30["e8"]>l30["e21"] and can_send("S3")):
        send(f"""【S3 突破上轨】短线追涨
{ts}  ${price:.1f}  已收在上轨之上
30m多头背景，可轻仓追""")
        record("S3")

    # W1级：轻度回调结束（回踩买入）
    if (p15["close"] < p15["lower"] and l15["close"] > l15["lower"] and l15["v1"] and l30["e8"]>l30["e21"] and can_send("W1")):
        send(f"""【W1 超跌反弹】绝佳抄底点！
{ts}  ${price:.1f}
上一根砸穿下轨，本根收回+放量
30m仍多头 → 暴力反弹概率极高""")
        record("W1")

    # W2级：轻度恐慌（可减仓观察）
    if (l15["dn"] and l15["v2"] and l30["e8"]>l30["e21"] and can_send("W2")):
        send(f"""【W2 短线恐慌】多头洗盘
{ts}  ${price:.1f}
击穿下轨+巨量，通常是洗盘
持仓不动，敢抄的可以轻仓低吸""")
        record("W2")

    # 空头信号（只在明确空头趋势下发）
    if (l15["dead"] and l15["v2"] and l15["dn"] and l30["e8"]<l30["e21"]<l30["e55"] and can_send("K1")):
        send(f"""【K1 强空信号】可短空
{ts}  ${price:.1f}
15m死叉+重度放量击穿下轨
30m三线空头 → 短线做空机会""")
        record("K1")

    # 调试
    print(f"[{datetime.now().strftime('%H:%M:%S')}] BTC ${price:.0f} | 15m{'多' if l15['e8']>l15['e21'] else '空'} | 30m{'多' if l30['e8']>l30['e21'] else '空'}")

if __name__ == '__main__':
    main()