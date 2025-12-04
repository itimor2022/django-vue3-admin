import requests
import pandas as pd
import numpy as np
from datetime import datetime

# ==================== 配置区 ====================
chat_id = "-4966987679"
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
    except Exception as e:
        print("获取K线失败:", e)
        return pd.DataFrame()


def add_adx(df, period=14):
    df["tr"] = np.maximum(df["high"] - df["low"],
                          np.maximum(abs(df["high"] - df["close"].shift(1)),
                                     abs(df["low"] - df["close"].shift(1))))
    df["+dm"] = np.where(df["high"] - df["high"].shift(1) > df["low"].shift(1) - df["low"],
                         np.maximum(df["high"] - df["high"].shift(1), 0), 0)
    df["-dm"] = np.where(df["low"].shift(1) - df["low"] > df["high"] - df["high"].shift(1),
                         np.maximum(df["low"].shift(1) - df["low"], 0), 0)

    df["+di"] = 100 * (df["+dm"].rolling(period).sum() /
                       df["tr"].rolling(period).sum().replace(0, np.nan))
    df["-di"] = 100 * (df["-dm"].rolling(period).sum() /
                       df["tr"].rolling(period).sum().replace(0, np.nan))

    df["dx"] = 100 * abs(df["+di"] - df["-di"]) / \
               (df["+di"] + df["-di"]).replace(0, np.nan)
    df["adx"] = df["dx"].rolling(period).mean()
    return df


def add_indicators(df, period=20, fast=8, slow=21):
    df["ema_fast"] = df["close"].ewm(span=fast, adjust=False).mean()
    df["ema_slow"] = df["close"].ewm(span=slow, adjust=False).mean()
    df["trend"] = (df["ema_fast"] > df["ema_slow"]).astype(int)
    df["cross_up"] = (df["trend"] == 1) & (df["trend"].shift(1) == 0)
    df["cross_dn"] = (df["trend"] == 0) & (df["trend"].shift(1) == 1)

    df["sma"] = df["close"].rolling(period).mean()
    df["std"] = df["close"].rolling(period).std()
    df["upper"] = df["sma"] + 2 * df["std"]
    df["lower"] = df["sma"] - 2 * df["std"]
    df["band_width"] = df["upper"] - df["lower"]
    df["bw_expand"] = df["band_width"] > df["band_width"].shift(1) * 1.12  # 扩张12%以上才算

    df["vol_ma"] = df["vol"].rolling(20).mean()
    df["big_vol"] = df["vol"] > df["vol_ma"] * 1.9  # 放量阈值略降低，避免错过

    df = add_adx(df)
    return df


def main():
    df_15m = get_candles("BTC-USDT", "15m", 200)
    df_30m = get_candles("BTC-USDT", "30m", 200)

    if df_15m.empty or df_30m.empty or len(df_15m) < 60 or len(df_30m) < 60:
        return

    df_15m = add_indicators(df_15m.copy(), period=20, fast=8, slow=21)
    df_30m = add_indicators(df_30m.copy(), period=20, fast=9, slow=26)  # 30m用更稳的参数

    latest_15m = df_15m.iloc[-1]
    prev_15m = df_15m.iloc[-2]
    latest_30m = df_30m.iloc[-1]

    close = latest_15m["close"]
    ts = latest_15m["ts"].strftime("%m-%d %H:%M")
    vol_ratio = latest_15m["vol"] / latest_15m["vol_ma"]

    # ==================== 30m 大趋势判断 ====================
    trend_30m = "多头趋势" if latest_30m["trend"] == 1 else "空头趋势"
    strength_30m = "强势" if latest_30m["adx"] > 30 else "一般"  # 你可以加ADX，这里用EMA趋势代替

    # ==================== 核心信号：15m 启动 + 30m 共振 ====================
    if (latest_15m["cross_up"] and
            latest_15m["big_vol"] and
            latest_15m["bw_expand"] and
            latest_30m["trend"] == 1):  # 必须30m也在多头

        power = "极强共振" if latest_30m["ema_fast"] > latest_30m["ema_slow"] * 1.003 else "强共振"
        msg = f"""BTC 多头爆发 ‼️‼️
时间：{ts}
价格：${close:.1f}
15m：EMA8金叉 + 放量{vol_ratio:.1f}x + 布林张口
30m：{trend_30m}（{power}）
→ 15m+30m 双周期共振做多信号！
建议：现价或回踩EMA8附近进场多单"""
        send_message(msg)

    if (latest_15m["cross_dn"] and
            latest_15m["big_vol"] and
            latest_15m["bw_expand"] and
            latest_30m["trend"] == 0):
        power = "极强共振" if latest_30m["ema_fast"] < latest_30m["ema_slow"] * 0.997 else "强共振"
        msg = f"""BTC 空头启动 ‼️‼️
时间：{ts}
价格：${close:.1f}
15m：EMA8死叉 + 放量{vol_ratio:.1f}x + 布林张口
30m：{trend_30m}（{power}）
→ 15m+30m 双周期共振做空信号！
建议：现价或反弹EMA8附近进场空单"""
        send_message(msg)

    # ==================== 额外：15m极端拉升/杀跌（不看30m）===================
    if (prev_15m["close"] > prev_15m["upper"] and
            latest_15m["close"] > latest_15m["upper"] and
            latest_15m["big_vol"] and prev_15m["big_vol"]):
        msg = f"""BTC 15m 疯狂拉升！已连续突破布林上轨
时间：{ts} | 价格：${close:.1f}
30m趋势：{trend_30m}
追涨需谨慎！可能冲顶在见短顶"""
        send_message(msg)

    if (prev_15m["close"] < prev_15m["lower"] and
            latest_15m["close"] < latest_15m["lower"] and
            latest_15m["big_vol"] and prev_15m["big_vol"]):
        msg = f"""BTC 15m 恐慌杀跌！连续击穿下轨
时间：{ts} | 价格：${close:.1f}
30m趋势：{trend_30m}
极度超卖，或有暴力反弹！"""
        send_message(msg)

    # 调试信息
    print(f"[{datetime.now().strftime('%H:%M:%S')}] BTC 15m ${close:.0f} | "
          f"15m={'多' if latest_15m['trend'] == 1 else '空'} + 放量{latest_15m['big_vol']} | "
          f"30m={'多' if latest_30m['trend'] == 1 else '空'}")


if __name__ == '__main__':
    main()
