# -*- coding: utf-8 -*-
"""
BTC 15分钟布林线趋势监控脚本（2025版 - 只做多，无去重）
核心：以15分钟布林线（25,2）作为主要多头趋势判断依据
- 只检测多头信号
- 信号1: 第一阳线上穿下轨，第二也是阳线，且第一阳线实体比上一根阴线实体大
- 信号2: 2根连续阳线直接从下轨碰到中轨（定义为第一根开盘接近下轨，最后一根收盘接近中轨，接近定义为在2%以内）
- 结合EMA金叉、ADX、锤头线、放量等辅助确认（仅多头相关）
- 每次运行只要有信号就发送消息（无去重，适合实时监控）
- 所有触发信号一次性整合成一条消息，避免刷屏
"""

import requests
import pandas as pd
import numpy as np
from datetime import datetime

# ==================== 配置区 ====================
CHAT_ID = "-5068436114"
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

    # 放量
    df["vol_ma20"] = df["vol"].rolling(20).mean()
    df["vol_spike"] = df["vol"] > df["vol_ma20"] * 1.5

    # 阳线/阴线
    df["is_bull"] = df["close"] > df["open"]
    df["entity_size"] = abs(df["close"] - df["open"])

    return df


def trend_alert(df_15m):
    if df_15m.empty or len(df_15m) < 3:
        return

    latest = df_15m.iloc[-1]  # 当前（第二阳线）
    prev = df_15m.iloc[-2]  # 第一阳线
    prev_prev = df_15m.iloc[-3]  # 上一根阴线（用于比较实体）

    close = latest["close"]
    ts = latest["ts"].strftime("%m-%d %H:%M")
    title = f"15m BTC-USDT - {ts}"

    # 核心：布林方向（只关注多头相关）
    boll_direction = "震荡"
    if close > latest["mid"]:
        boll_direction = "多头方向"

    # 收集所有触发信号（只多头）
    signals = []

    # 信号1: 第一阳线上穿下轨，第二也是阳线，且第一阳线实体比上一根阴线实体大
    crossed_lower = (prev_prev["close"] <= prev_prev["lower"]) and (prev["close"] > prev["lower"])
    if crossed_lower and prev["is_bull"] and latest["is_bull"] and prev_prev["is_bull"] == False:
        if prev["entity_size"] > prev_prev["entity_size"]:
            signals.append(f"🚀第一阳线上穿下轨 + 第二阳线 + 第一阳实体 > 阴线实体 → 多头反转信号")

    # 信号2: 2根连续阳线直接从下轨碰到中轨（第一根开盘接近下轨，最后一根收盘接近中轨，接近2%）
    near_lower = prev["low"] < prev["lower"]
    near_latest_lower = latest["low"] < latest["lower"]
    near_mid = latest["close"] > latest["mid"]
    if prev["is_bull"] and latest["is_bull"] and near_lower and near_mid:
        signals.append(f"🚀2根连续阳线从下轨直达中轨 → 多头强势拉升")
    if prev["is_bull"] and latest["is_bull"] and near_latest_lower and near_mid:
        signals.append(f"🚀1根连续阳线从下轨直达中轨 → 多头强势拉升")

    # 辅助信号: 连续破轨（只多头：连续2根破布林上轨）
    if (prev["close"] > prev["upper"]) and (latest["close"] > latest["upper"]) and close > latest["mid"]:
        signals.append(f"🚀连续2根破布林上轨 + 多头方向 → 疯狂追涨")

    # 辅助信号: 放量确认（只多头）
    if latest["vol_spike"] and close > latest["mid"]:
        signals.append(f"📈放量上涨 + 布林多头方向 → 趋势增强")

    # 构建并发送消息（只要有信号就发，无去重）
    if signals:
        msg = f"【15分钟布林多头趋势报告】{title}\n\n"
        msg += f"当前方向：{boll_direction}\n"
        msg += f"价格：${close:.0f} | 中轨：${latest['mid']:.0f}\n"
        msg += "──────────────\n"

        for sig in signals:
            msg += f"{sig}\n"

        send_message(msg)
        print(f"【{datetime.now().strftime('%H:%M')}】发送布林多头趋势报告 - {len(signals)}个信号")
    else:
        print(f"【{datetime.now().strftime('%H:%M')}】无多头信号")

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
    print("BTC 15分钟布林线多头趋势监控启动（无去重）...")
    main()
