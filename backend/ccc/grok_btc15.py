# -*- coding: utf-8 -*-
"""
BTC 15分钟布林线趋势监控脚本（2025版 - 只做空，无去重）
核心：以15分钟布林线（25,2）作为主要空头趋势判断依据
- 只检测空头信号
- 信号1: 1根阴线实体直接从中轨碰到下轨（开盘 >= 中轨, 收盘 <= 下轨, 是阴线）
- 信号2: 连续三根阴线，其中至少一根实体下穿中轨（某根 open > 中轨 and close < 中轨），且三个阴线的中心点 ((open + close)/2) 向下移动（递减）
- 结合EMA死叉、ADX、射击之星（反转为空头）、放量等辅助确认（仅空头相关）
- 每次运行只要有信号就发送消息（无去重，适合实时监控）
- 所有触发信号一次性整合成一条消息，避免刷屏
"""

import requests
import pandas as pd
import numpy as np
from datetime import datetime

# ==================== 配置区 ====================
CHAT_ID = "-4850300375"
TOKEN = "8444348700:AAGqkeUUuB_0rI_4qIaJxrTylpRGh020wU0"
BASE_URL = f"https://api.telegram.org/bot{TOKEN}"


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
        df = pd.DataFrame(data,
                          columns=["ts", "open", "high", "low", "close", "vol", "volCcy", "volCcyQuote", "confirm"])
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
    df["ema12"] = df["close"].ewm(span=12, adjust=False).mean()
    df["ema21"] = df["close"].ewm(span=21, adjust=False).mean()
    df["ema_cross_up"] = (df["ema12"].shift(1) <= df["ema21"].shift(1)) & (df["ema12"] > df["ema21"])
    df["ema_cross_dn"] = (df["ema12"].shift(1) >= df["ema21"].shift(1)) & (df["ema12"] < df["ema21"])
    df["trend_ema"] = np.where(df["ema12"] > df["ema21"], 1, -1)

    # BOLL 25,2（核心）
    df["sma25"] = df["close"].rolling(25).mean()
    df["std25"] = df["close"].rolling(25).std()
    df["upper"] = df["sma25"] + 2 * df["std25"]
    df["lower"] = df["sma25"] - 2 * df["std25"]
    df["mid"] = df["sma25"]

    # 射击之星（上影线长，实体小，暗示空头反转）
    df["upper_shadow"] = (df["high"] - df[["open", "close"]].max(axis=1)) / (df["high"] - df["low"] + 1e-8)
    df["is_shooting_star"] = (df["upper_shadow"] > 0.65) & (df["close"] < df["open"]) & (
                abs(df["close"] - df["open"]) / (df["high"] - df["low"] + 1e-8) < 0.3)

    # 放量
    df["vol_ma20"] = df["vol"].rolling(20).mean()
    df["vol_spike"] = df["vol"] > df["vol_ma20"] * 1.5

    # 阴线/阳线
    df["is_bear"] = df["close"] < df["open"]
    df["entity_size"] = abs(df["close"] - df["open"])

    # 中心点
    df["center"] = (df["open"] + df["close"]) / 2

    return df


def trend_alert(df_15m):
    if df_15m.empty or len(df_15m) < 4:
        return

    latest = df_15m.iloc[-1]  # 当前K线
    prev = df_15m.iloc[-2]
    prev_prev = df_15m.iloc[-3]

    close = latest["close"]
    ts = latest["ts"].strftime("%m-%d %H:%M")
    title = f"15m BTC-USDT - {ts}"

    # 核心：布林方向（只关注空头相关）
    boll_direction = "震荡"
    if close < latest["mid"]:
        boll_direction = "空头方向"

    # 收集所有触发信号（只空头）
    signals = []

    # 信号1: 1根阴线实体直接从中轨碰到下轨
    if latest["is_bear"] and latest["open"] >= latest["mid"] and latest["close"] <= latest["lower"]:
        signals.append(f"⚠️1根阴线实体从中轨直达下轨 → 空头强势下杀")

    # 信号2: 连续三根阴线，其中至少一根实体下穿中轨，且三个中心点向下移动
    three_bears = prev_prev["is_bear"] and prev["is_bear"] and latest["is_bear"]
    centers_down = (prev_prev["center"] > prev["center"]) and (prev["center"] > latest["center"])
    has_cross_mid = False
    for candle in [prev_prev, prev, latest]:
        if candle["open"] > candle["mid"] and candle["close"] < candle["mid"]:
            has_cross_mid = True
            break
    if three_bears and has_cross_mid and centers_down:
        signals.append(f"⚠️连续三根阴线 + 实体下穿中轨 + 中心点向下 → 空头加速")

    # 辅助信号: 射击之星顶部反转
    if latest["is_shooting_star"] and latest["close"] < latest["mid"] and latest["vol_spike"]:
        signals.append(f"💥射击之星顶部反转（上影{latest['upper_shadow']:.1%}）+ 放量 → 顶部见顶")

    # 辅助信号: 连续破轨（只空头：连续2根破布林下轨）
    if (prev["close"] < prev["lower"]) and (latest["close"] < latest["lower"]) and close < latest["mid"]:
        signals.append(f"⚠️连续2根破布林下轨 + 空头方向 → 恐慌加剧")

    # 辅助信号: 放量确认（只空头）
    if latest["vol_spike"] and close < latest["mid"]:
        signals.append(f"📉放量下跌 + 布林空头方向 → 趋势增强")

    # 构建并发送消息（只要有信号就发，无去重）
    if signals:
        msg = f"【15分钟布林空头趋势报告】{title}\n\n"
        msg += f"当前方向：{boll_direction}\n"
        msg += f"价格：${close:.0f} | 中轨：${latest['mid']:.0f}\n"
        msg += "──────────────\n"

        for sig in signals:
            msg += f"{sig}\n"

        send_message(msg)
        print(f"【{datetime.now().strftime('%H:%M')}】发送布林空头趋势报告 - {len(signals)}个信号")
    else:
        print(f"【{datetime.now().strftime('%H:%M')}】无空头信号")

    # 控制台打印当前状态
    print(f"{datetime.now().strftime('%m-%d %H:%M')} | BTC ${close:.0f} | 布林方向: {boll_direction}")


def main():
    df_15m = get_candles("BTC-USDT", "15m", 300)
    if df_15m.empty:
        print("无法获取15分钟K线")
        return

    df_15m = add_technical_indicators(df_15m)
    trend_alert(df_15m)


if __name__ == '__main__':
    print("BTC 15分钟布林线空头趋势监控启动（无去重）...")
    main()
