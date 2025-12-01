import requests
import pandas as pd
import numpy as np
from datetime import datetime

# ==================== 配置区 ====================
chat_id = "-4850300375"
TOKEN = "8444348700:AAGqkeUUuB_0rI_4qIaJxrTylpRGh020wU0"   # 直接写完整，安全点
BASE_URL = f"https://api.telegram.org/bot{TOKEN}"

pd.set_option('display.max_columns', 20)
pd.set_option('display.width', 1000)


def send_message(msg):
    url = f"{BASE_URL}/sendMessage"
    payload = {
        "chat_id": chat_id,
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
        df["ts"] = pd.to_datetime(df["ts"].astype(int), unit='ms') + pd.Timedelta(hours=7)  # 转为亚洲时间
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

    # 快慢线趋势
    df["trend_ema"] = np.where(df["ema12"] > df["ema21"], 1, -1)  # 1=多头排列，-1=空头排列
    df["trend_ema_prev"] = df["trend_ema"].shift(1)
    df["ema_cross_up"] = (df["trend_ema"] == 1) & (df["trend_ema_prev"] == -1)
    df["ema_cross_dn"] = (df["trend_ema"] == -1) & (df["trend_ema_prev"] == 1)

    # BOLL（25,2）
    df["sma25"] = df["close"].rolling(25).mean()
    df["std25"] = df["close"].rolling(25).std()
    df["upper"] = df["sma25"] + 2 * df["std25"]
    df["lower"] = df["sma25"] - 2 * df["std25"]

    # ADX 趋势强度（14期）
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

    # 波段高低点（使用5根K线确认）
    df["swing_high"] = df["high"][(df["high"] == df["high"].rolling(11, center=True).max())]
    df["swing_low"] = df["low"][(df["low"] == df["low"].rolling(11, center=True).min())]

    # 趋势结构：Higher High / Lower Low
    df["hh"] = df["swing_high"].notna() & (df["swing_high"] > df["swing_high"].shift(1).where(df["swing_high"].shift(1).notna()))
    df["ll"] = df["swing_low"].notna() & (df["swing_low"] < df["swing_low"].shift(1).where(df["swing_low"].shift(1).notna()))
    df["lh"] = df["swing_high"].notna() & (df["swing_high"] < df["swing_high"].shift(1).where(df["swing_high"].shift(1).notna()))
    df["hl"] = df["swing_low"].notna() & (df["swing_low"] > df["swing_low"].shift(1).where(df["swing_low"].shift(1).notna()))

    # 当前趋势结构判断（最近两个有效波段点）
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

    # 下影线比例（阳线更强）
    df["lower_shadow"] = (df[["open", "close"]].min(axis=1) - df["low"]) / (df["high"] - df["low"] + 1e-8)
    df["is_hammer"] = (df["lower_shadow"] > 0.6) & (df["close"] > df["open"])

    return df


def trend_alert(df_15m, df_1h=None):
    if df_15m.empty:
        return
    latest = df_15m.iloc[-1]
    prev = df_15m.iloc[-2]
    close = latest["close"]
    ts = latest["ts"].strftime("%m-%d %H:%M")
    coin = "BTC-USDT"

    title = f"15m {coin} - {ts}"

    # ==================== 核心趋势信号 ====================

    # 1. EMA12/21 金叉死叉 + ADX > 20 过滤弱势
    if latest["ema_cross_up"] and latest["adx"] > 20:
        strength = "强" if latest["adx"] > 35 else "中"
        msg = f"🚀15m多头趋势启动\n{title}\nEMA12上穿EMA21 + ADX={latest['adx']:.1f} ({strength})\n价格: ${close:.0f}"
        if df_1h is not None and df_1h.iloc[-1]["ema12"] > df_1h.iloc[-1]["ema21"]:
            msg = "‼️" + msg.replace("启动", "1h共振确认，多头极强！")
        send_message(msg)

    if latest["ema_cross_dn"] and latest["adx"] > 20:
        strength = "强" if latest["adx"] > 35 else "中"
        msg = f"15m空头趋势启动\n{title}\nEMA12下穿EMA21 + ADX={latest['adx']:.1f} ({strength})\n价格: ${close:.0f}"
        if df_1h is not None and df_1h.iloc[-1]["ema12"] < df_1h.iloc[-1]["ema21"]:
            msg = "‼️" + msg.replace("启动", "1h共振确认，空头极强！")
        send_message(msg)

    # 2. 趋势结构突破（配合成交量放大）
    structure = latest["current_structure"]
    vol_up = latest["vol"] > df_15m["vol"].rolling(20).mean().iloc[-1] * 1.5

    if "强势上涨" in structure and vol_up:
        send_message(f"上涨结构确认\n{title}\nHigher High + Higher Low 成立\n放量突破，趋势转强！\n价格: ${close:.0f}")

    if "强势下跌" in structure and vol_up:
        send_message(f"下跌结构确认\n{title}\nLower High + Lower Low 成立\n放量下破，趋势转空！\n价格: ${close:.0f}")

    # 3. 连续2根破布林 + 趋势一致
    if (prev["close"] < prev["lower"]) and (latest["close"] < latest["lower"]) and latest["trend_ema"] == -1:
        send_message(f"连续破下轨 + 空头排列\n{title}\n极度恐慌，可考虑超短反弹\n价格: ${close:.0f}")

    if (prev["close"] > prev["upper"]) and (latest["close"] > latest["upper"]) and latest["trend_ema"] == 1:
        send_message(f"连续破上轨 + 多头排列\n{title}\n疯狂追涨，注意冲顶风险\n价格: ${close:.0f}")

    # 4. 锤头线 + 处于支撑
    if latest["is_hammer"] and latest["lower_shadow"] > 0.7 and latest["close"] > latest["ema21"]:
        send_message(f"锤头线探底回升\n{title}\n下影占比 {latest['lower_shadow']:.1%}\n多头反击信号\n价格: ${close:.0f}")


def main(coin="BTC-USDT"):
    df_15m = get_candles(coin, "15m", 300)
    df_1h = get_candles(coin, "1H", 200)   # 用于多级别共振

    if df_15m.empty:
        return

    df_15m = add_technical_indicators(df_15m)
    if not df_1h.empty:
        df_1h = add_technical_indicators(df_1h)

    trend_alert(df_15m, df_1h)

    # 打印最新结构（调试用）
    print(f"{datetime.now().strftime('%m-%d %H:%M')} | {coin} 15m结构:", df_15m.iloc[-1]["current_structure"])
    print(f"价格: ${df_15m.iloc[-1]['close']:.0f} | ADX: {df_15m.iloc[-1]['adx']:.1f} | 趋势: {'多' if df_15m.iloc[-1]['trend_ema']==1 else '空'}")


if __name__ == '__main__':
    # 建议配合定时任务，每5~10分钟运行一次
    main("BTC-USDT")