import requests
import pandas as pd
from datetime import datetime

# ==================== 配置区 ====================
chat_id = "-5068436114"
TOKEN = "8444348700:AAGqkeUUuB_0rI_4qIaJxrTylpRGh020wU0"
BASE_URL = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

def send_message(text):
    try:
        requests.post(BASE_URL, data={
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": True
        }, timeout=10)
    except:
        pass


def get_candles(instId="BTC-USDT", bar="5m", limit=300):
    url = "https://www.okx.com/api/v5/market/candles"
    params = {"instId": instId, "bar": bar, "limit": limit}
    try:
        data = requests.get(url, params=params, timeout=10).json()["data"]
        df = pd.DataFrame(data, columns=["ts", "o", "h", "l", "c", "vol", "volCcy", "volCcyQuote", "confirm"])
        df["ts"] = pd.to_datetime(df["ts"].astype(int), unit='ms')
        df = df.astype({"o":float, "h":float, "l":float, "c":float, "vol":float})
        df = df[["ts", "o", "h", "l", "c", "vol"]].sort_values("ts").reset_index(drop=True)
        df.columns = ["ts", "open", "high", "low", "close", "vol"]
        return df
    except Exception as e:
        print("获取K线失败:", e)
        return pd.DataFrame()


def add_indicators(df, fast=8, slow=21, bb_period=20):
    # EMA趋势
    df["ema_fast"] = df["close"].ewm(span=fast, adjust=False).mean()
    df["ema_slow"] = df["close"].ewm(span=slow, adjust=False).mean()
    df["trend"] = (df["ema_fast"] > df["ema_slow"]).astype(int)
    df["bull"] = df["trend"] == 1
    df["bear"] = df["trend"] == 0

    # 金叉死叉
    df["cross_up"] = (df["trend"] == 1) & (df["trend"].shift(1) == 0)
    df["cross_dn"] = (df["trend"] == 0) & (df["trend"].shift(1) == 1)

    # 布林带
    df["sma"] = df["close"].rolling(bb_period).mean()
    df["std"] = df["close"].rolling(bb_period).std()
    df["upper"] = df["sma"] + 2 * df["std"]
    df["lower"] = df["sma"] - 2 * df["std"]
    df["band_width"] = df["upper"] - df["lower"]
    df["bw_expand"] = df["band_width"] > df["band_width"].shift(1) * 1.15  # 扩张15%以上

    # 放量
    df["vol_ma20"] = df["vol"].rolling(20).mean()
    df["vol_spike"] = df["vol"] > df["vol_ma20"] * 2.2  # 极强放量

    return df


def main():
    df_5m = get_candles("BTC-USDT", "5m", 300)
    df_15m = get_candles("BTC-USDT", "15m", 300)

    if df_5m.empty or df_15m.empty or len(df_5m) < 80 or len(df_15m) < 60:
        return

    df_5m = add_indicators(df_5m, fast=7, slow=18, bb_period=20)   # 5m用更灵敏参数
    df_15m = add_indicators(df_15m, fast=8, slow=21, bb_period=20)

    latest_5m = df_5m.iloc[-1]
    prev_5m = df_5m.iloc[-2]
    latest_15m = df_15m.iloc[-1]

    price = latest_5m["close"]
    ts = latest_5m["ts"].strftime("%m-%d %H:%M")
    vol_ratio = latest_5m["vol"] / latest_5m["vol_ma20"]

    # ==================== 终极多头信号：5m点火 + 15m大趋势支持 ====================
    if (latest_5m["cross_up"] and
        latest_5m["vol_spike"] and
        latest_5m["bw_expand"] and
        latest_15m["bull"] and
        price > latest_15m["ema_slow"]):  # 价格站在15m慢线上方

        strength = "超强" if vol_ratio > 4 else "极强"
        msg = f"""BTC 即将暴力拉升 ‼️‼️‼️
时间：{ts}
价格：${price:.1f}
【5m级引爆信号】
・EMA7金叉EMA18
・放量 {vol_ratio:.1f}倍（{strength}）
・布林带大幅张口
【15m大趋势确认】
・多头排列进行中
・价格站稳EMA21 = {latest_15m['ema_slow']:.0f}
→ 5m+15m 双周期顶级共振！
建议：立即或回踩5m EMA7（{latest_5m['ema_fast']:.0f}）进场多单
目标：+5% ~ +15%"""
        send_message(msg)

    # ==================== 终极空头信号 ====================
    if (latest_5m["cross_dn"] and
        latest_5m["vol_spike"] and
        latest_5m["bw_expand"] and
        latest_15m["bear"] and
        price < latest_15m["ema_slow"]):

        strength = "超强" if vol_ratio > 4 else "极强"
        msg = f"""BTC 即将暴跌预警 ‼️‼️‼️
时间：{ts}
价格：${price:.1f}
【5m级杀跌信号】
・EMA7死叉EMA18
・放量 {vol_ratio:.1f}倍（{strength}）
・布林带大幅张口
【15m大趋势确认】
・空头排列进行中
・价格跌破EMA21 = {latest_15m['ema_slow']:.0f}
→ 5m+15m 双周期顶级做空信号！
建议：立即或反弹5m EMA7（{latest_5m['ema_fast']:.0f}）进场空单
目标：-5% ~ -15%"""
        send_message(msg)

    # ==================== 附加：5m极端追涨/恐慌（不看15m）===================
    if (prev_5m["close"] > prev_5m["upper"] and
        latest_5m["close"] > latest_5m["upper"] and
        latest_5m["vol_spike"]):
        msg = f"""BTC 5m 疯狂追涨中！
{ts} | ${price:.1f}
连续两根爆拉破上轨
15m趋势：{'多' if latest_15m['bull'] else '空'}
注意：极度亢奋，冲顶风险极高！"""
        send_message(msg)

    if (prev_5m["close"] < prev_5m["lower"] and
        latest_5m["close"] < latest_5m["lower"] and
        latest_5m["vol_spike"]):
        msg = f"""BTC 5m 恐慌砸盘！
{ts} | ${price:.1f}连续击穿下轨
15m趋势：{'多' if latest_15m['bull'] else '空'}
极度超卖，或有V型反转可能！"""
        send_message(msg)

    # 调试打印
    print(f"[{datetime.now().strftime('%H:%M:%S')}] BTC ${price:.0f} | "
          f"5m={'多' if latest_5m['bull'] else '空'} 放量{latest_5m['vol_spike']} | "
          f"15m={'多' if latest_15m['bull'] else '空'}")


if __name__ == '__main__':
    main()
