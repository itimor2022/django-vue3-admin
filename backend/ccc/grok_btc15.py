# -*- coding: utf-8 -*-
"""
BTC 15分钟趋势监控脚本（2025版）
只判断15分钟信号，保留EMA金叉死叉、ADX过滤、趋势结构、布林破轨、锤头线等核心逻辑
运行一次立即触发当前信号，适合定时任务或手动运行
"""

import requests
import pandas as pd
import numpy as np
from datetime import datetime
import os

# ==================== 配置区 ====================
CHAT_ID = "-4850300375"
TOKEN = "8444348700:AAGqkeUUuB_0rI_4qIaJxrTylpRGh020wU0"
BASE_URL = f"https://api.telegram.org/bot{TOKEN}"

pd.set_option('display.max_columns', 20)
pd.set_option('display.width', 1000)


def send_message(msg):
    url = f"{BASE_URL}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": msg,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    try:
        r = requests.get(url, params=payload, timeout=10)
        if not r.json().get("ok"):
            print("Telegram发送失败:", r.json())
    except Exception as e:
        print("发送异常:", e)


def get_candles(instId="BTC-USDT", bar="15m", limit=300):
    url = "https://www.okx.com/api/v5/market/candles"
    params = {"instId": instId, "bar": bar, "limit": limit}
    try:
        r = requests.get(url, params=params, timeout=10)
        data = r.json()["data"]
        df = pd.DataFrame(data, columns=["ts", "open", "high", "low", "close", "vol", "volCcy", "volCcyQuote", "confirm"])
        df["ts"] = pd.to_datetime(df["ts"].astype(int), unit='ms') + pd.Timedelta(hours=7)  # 亚洲时间
        df = df.astype({"open": float, "high": float, "low": float, "close": float, "vol": float})
        df = df[["ts", "open", "high", "low", "close", "vol"]].sort_values("ts").reset_index(drop=True)
        return df
    except Exception as e:
        print("获取K线失败:", e)
        return pd.DataFrame()


def add_technical_indicators(df):
    if len(df) < 50:
        return df

    # 基础指标
    df["return"] = df["close"].pct_change() * 100
    df["hl2"] = (df["high"] + df["low"]) / 2
    df["ema12"] = df["close"].ewm(span=12, adjust=False).mean()
    df["ema21"] = df["close"].ewm(span=21, adjust=False).mean()
    df["ema50"] = df["close"].ewm(span=50, adjust=False).mean()
    df["ema200"] = df["close"].ewm(span=200, adjust=False).mean()

    # EMA趋势
    df["trend_ema"] = np.where(df["ema12"] > df["ema21"], 1, -1)
    df["trend_ema_prev"] = df["trend_ema"].shift(1)
    df["ema_cross_up"] = (df["trend_ema"] == 1) & (df["trend_ema_prev"] == -1)
    df["ema_cross_dn"] = (df["trend_ema"] == -1) & (df["trend_ema_prev"] == 1)

    # BOLL 25,2
    df["sma25"] = df["close"].rolling(25).mean()
    df["std25"] = df["close"].rolling(25).std()
    df["upper"] = df["sma25"] + 2 * df["std25"]
    df["lower"] = df["sma25"] - 2 * df["std25"]

    # ADX
    def calc_adx(high, low, close, period=14):
        df_temp = pd.DataFrame({"high": high, "low": low, "close": close})
        plus_dm = high.diff()
        minus_dm = low.diff()
        plus_dm[plus_dm < 0] = 0
        minus_dm[minus_dm > 0] = 0
        minus_dm = abs(minus_dm)

        tr1 = pd.DataFrame(high - low)
        tr2 = pd.DataFrame(abs(high - close.shift(1)))
        tr3 = pd.DataFrame(abs(low - close.shift(1)))
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(period).mean()

        plus_di = 100 * (plus_dm.ewm(alpha=1/period).mean() / atr)
        minus_di = 100 * (minus_dm.ewm(alpha=1/period).mean() / atr)
        dx = (abs(plus_di - minus_di) / (plus_di + minus_di)) * 100
        adx = dx.ewm(alpha=1/period).mean()
        return adx

    df["adx"] = calc_adx(df["high"], df["low"], df["close"])

    # 波段高低点（原版，稳定使用）
    df["swing_high"] = df["high"][(df["high"] == df["high"].rolling(11, center=True).max())]
    df["swing_low"] = df["low"][(df["low"] == df["low"].rolling(11, center=True).min())]

    # 趋势结构
    recent_highs = df["swing_high"].dropna().tail(3)
    recent_lows = df["swing_low"].dropna().tail(3)

    structure = "震荡"
    if len(recent_highs) >= 2 and len(recent_lows) >= 2:
        last_h = recent_highs.iloc[-1]
        prev_h = recent_highs.iloc[-2]
        last_l = recent_lows.iloc[-1]
        prev_l = recent_lows.iloc[-2]
        if last_h > prev_h and last_l > prev_l:
            structure = "强势上涨（HH+HL）"
        elif last_h < prev_h and last_l < prev_l:
            structure = "强势下跌（LH+LL）"
        elif last_h < prev_h and last_l > prev_l:
            structure = "潜在底背离（LH+HL）"
        elif last_h > prev_h and last_l < prev_l:
            structure = "潜在顶背离（HH+LL）"

    df.loc[df.index[-1], "current_structure"] = structure

    # 下影线（锤头线）
    df["lower_shadow"] = (df[["open", "close"]].min(axis=1) - df["low"]) / (df["high"] - df["low"] + 1e-8)
    df["is_hammer"] = (df["lower_shadow"] > 0.6) & (df["close"] > df["open"])

    return df


def trend_alert(df_15m):
    if df_15m.empty:
        return

    latest = df_15m.iloc[-1]
    prev = df_15m.iloc[-2]
    close = latest["close"]
    ts = latest["ts"].strftime("%m-%d %H:%M")
    title = f"15m BTC-USDT - {ts}"

    # 记录已发信号（防止重复）
    log_file = "btc_signal_log.txt"
    sent_signals = set()
    if os.path.exists(log_file):
        with open(log_file, "r", encoding="utf-8") as f:
            sent_signals = set(f.read().strip().split("\n"))

    def try_send(key, message):
        if key not in sent_signals:
            send_message(message)
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(key + "\n")
            print(f"【{datetime.now().strftime('%H:%M')}】发送: {key}")

    # 1. EMA金叉/死叉 + ADX过滤
    if latest["ema_cross_up"] and latest["adx"] > 20:
        strength = "强" if latest["adx"] > 35 else "中"
        key = f"EMA_UP_{ts.split()[0]}"
        msg = f"🚀15m多头趋势启动\n{title}\nEMA12上穿EMA21 + ADX={latest['adx']:.1f} ({strength})\n价格: ${close:.0f}"
        try_send(key, msg)

    if latest["ema_cross_dn"] and latest["adx"] > 20:
        strength = "强" if latest["adx"] > 35 else "中"
        key = f"EMA_DN_{ts.split()[0]}"
        msg = f"⚠️15m空头趋势启动\n{title}\nEMA12下穿EMA21 + ADX={latest['adx']:.1f} ({strength})\n价格: ${close:.0f}"
        try_send(key, msg)

    # 2. 趋势结构 + 放量确认
    structure = latest["current_structure"]
    vol_up = latest["vol"] > df_15m["vol"].rolling(20).mean().iloc[-1] * 1.5

    if "强势上涨" in structure and vol_up:
        key = f"UP_STR_{ts.split()[0]}"
        msg = f"上涨结构确认\n{title}\nHigher High + Higher Low 成立\n放量突破，趋势转强！\n价格: ${close:.0f}"
        try_send(key, msg)

    if "强势下跌" in structure and vol_up:
        key = f"DN_STR_{ts.split()[0]}"
        msg = f"下跌结构确认\n{title}\nLower High + Lower Low 成立\n放量下破，趋势转空！\n价格: ${close:.0f}"
        try_send(key, msg)

    # 3. 连续2根破布林
    if (prev["close"] < prev["lower"]) and (latest["close"] < latest["lower"]) and latest["trend_ema"] == -1:
        key = f"BB_DOWN_{ts.split()[0]}"
        msg = f"⚠️连续2阴破下轨 + 空头排列\n{title}\n极度恐慌，可考虑超短反弹\n价格: ${close:.0f}"
        try_send(key, msg)

    if (prev["close"] > prev["upper"]) and (latest["close"] > latest["upper"]) and latest["trend_ema"] == 1:
        key = f"BB_UP_{ts.split()[0]}"
        msg = f"🚀连续2阳破上轨 + 多头排列\n{title}\n疯狂追涨，注意冲顶风险\n价格: ${close:.0f}"
        try_send(key, msg)

    # 4. 锤头线探底回升
    if latest["is_hammer"] and latest["lower_shadow"] > 0.7 and latest["close"] > latest["ema21"]:
        key = f"HAMMER_{ts.split()[0]}"
        msg = f"🔥锤头线探底回升\n{title}\n下影占比 {latest['lower_shadow']:.1%}\n多头反击信号\n价格: ${close:.0f}"
        try_send(key, msg)

    # 打印当前状态（调试）
    print(f"{datetime.now().strftime('%m-%d %H:%M')} | BTC ${close:.0f} | ADX: {latest['adx']:.1f} | 趋势: {'多' if latest['trend_ema']==1 else '空'} | 结构: {structure}")


def main():
    df_15m = get_candles("BTC-USDT", "15m", 300)
    if df_15m.empty:
        print("无法获取15分钟K线")
        return

    df_15m = add_technical_indicators(df_15m)
    trend_alert(df_15m)


if __name__ == '__main__':
    print("BTC 15分钟趋势监控启动（仅15m信号）...")
    main()