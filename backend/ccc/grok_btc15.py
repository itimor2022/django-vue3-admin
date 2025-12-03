import requests
import pandas as pd
from datetime import datetime

# ==================== 配置区 ====================
chat_id = "-4850300375"
TOKEN = "8444348700:AAGqkeUUuB_0rI_4qIaJxrTylpRGh020wU0"
BASE_URL = f"https://api.telegram.org/bot{TOKEN}/sendMessage"


def send_message(text):
    try:
        requests.get(BASE_URL, params={
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": True
        }, timeout=10)
    except:
        pass


def get_candles(instId="BTC-USDT", bar="15m", limit=200):
    url = "https://www.okx.com/api/v5/market/candles"
    params = {"instId": instId, "bar": bar, "limit": limit}
    try:
        data = requests.get(url, params=params, timeout=10).json()["data"]
        df = pd.DataFrame(data, columns=["ts", "o", "h", "l", "c", "vol", "volCcy", "volCcyQuote", "confirm"])
        df["ts"] = pd.to_datetime(df["ts"].astype(int), unit='ms')
        df = df.astype({"o": float, "h": float, "l": float, "c": float, "vol": float})
        df = df[["ts", "o", "h", "l", "c", "vol"]].sort_values("ts").reset_index(drop=True)
        df.columns = ["ts", "open", "high", "low", "close", "vol"]
        return df
    except:
        return pd.DataFrame()


def analyze_15m(df):
    if len(df) < 60:
        return

    # ============ 核心三指标（只保留最强信号） ============

    # 1. EMA8 vs EMA21（比12/21更灵敏，专为15m设计）
    df["ema8"] = df["close"].ewm(span=8, adjust=False).mean()
    df["ema21"] = df["close"].ewm(span=21, adjust=False).mean()
    df["trend"] = (df["ema8"] > df["ema21"]).astype(int)  # 1=多 0=空
    df["cross_up"] = (df["trend"] == 1) & (df["trend"].shift(1) == 0)
    df["cross_dn"] = (df["trend"] == 0) & (df["trend"].shift(1) == 1)

    # 2. 布林带中轨 + 带宽扩张（趋势启动标志）
    df["sma20"] = df["close"].rolling(20).mean()
    df["std20"] = df["close"].rolling(20).std()
    df["upper"] = df["sma20"] + 2 * df["std20"]
    df["lower"] = df["sma20"] - 2 * df["std20"]
    df["band_width"] = df["upper"] - df["lower"]
    df["bw_expand"] = df["band_width"] > df["band_width"].shift(1) * 1.1  # 带宽扩张10%以上

    # 3. 放量：当前成交量 > 近20根均量的2倍
    df["vol_ma"] = df["vol"].rolling(20).mean()
    df["big_vol"] = df["vol"] > df["vol_ma"] * 2

    latest = df.iloc[-1]
    prev = df.iloc[-2]
    close = latest["close"]
    ts = latest["ts"].strftime("%m-%d %H:%M")

    # ==================== 极简发信号逻辑 ====================

    alert_sent = False

    # 信号1：金叉 + 放量 + 布林带扩张（多头爆发
    if latest["cross_up"] and latest["big_vol"] and latest["bw_expand"]:
        msg = f"""🚀 BTC 15m 多头爆发信号 ‼️
时间：{ts}
价格：${close:.1f}
EMA8上穿EMA21金叉
放量 {latest['vol'] / latest['vol_ma']:.1f}倍
布林带张口扩张
→ 趋势启动，建议顺势做多"""
        send_message(msg)
        alert_sent = True

    # 信号2：死叉 + 放量 + 布林带扩张空头启动
    if latest["cross_dn"] and latest["big_vol"] and latest["bw_expand"]:
        msg = f"""💥 BTC 15m 空头启动信号 ‼️
时间：{ts}
价格：${close:.1f}
EMA8下穿EMA21死叉
放量 {latest['vol'] / latest['vol_ma']:.1f}倍
布林带张口扩张
→ 下跌趋势确立，建议顺势做空"""
        send_message(msg)
        alert_sent = True

    # 信号3：连续2根大阳线突破上轨 + 持续放量强势上涨中
    if (prev["close"] > prev["upper"] and
            latest["close"] > latest["upper"] and
            latest["close"] > prev["close"] and
            latest["big_vol"] and prev["big_vol"]):
        msg = f"""🔥 BTC 15m 疯狂拉升中！
时间：{ts}
价格：${close:.1f}（+{latest['close'] / prev['close'] - 1:.2%}）
连续突破布林上轨
持续巨量，追涨要小心冲顶！"""
        send_message(msg)

    # 信号4：连续2根大阴线击穿下轨恐慌杀跌
    if (prev["close"] < prev["lower"] and
            latest["close"] < latest["lower"] and
            latest["close"] < prev["close"] and
            latest["big_vol"] and prev["big_vol"]):
        msg = f"""⚠️ BTC 15m 恐慌杀跌！
时间：{ts}
价格：${close:.1f}（-{1 - latest['close'] / prev['close']:.2%}）
连续击穿布林下轨
放量下杀，或有极端超跌反弹机会"""
        send_message(msg)

    # 调试打印（可注释）
    status = "多头" if latest["trend"] else "空头"
    print(
        f"{datetime.now().strftime('%H:%M')} | BTC 15m | ${close:.0f} | {status} | 放量:{latest['big_vol']} 带宽扩:{latest['bw_expand']}")


if __name__ == '__main__':
    df = get_candles("BTC-USDT", "15m", 200)
    if not df.empty:
        analyze_15m(df)
