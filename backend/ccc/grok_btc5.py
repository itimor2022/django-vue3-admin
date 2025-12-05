import requests
import pandas as pd
from datetime import datetime
import os

# ==================== 配置区 ====================
chat_id = "-5068436114"                                   # 你的群组/频道ID
TOKEN = "8444348700:AAGqkeUUuB_0rI_4qIaJxrTylpRGh020wU0"   # 你的Bot Token
BASE_URL = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

SIGNAL_FILE = "/tmp/btc_last_signal.txt"  # Linux/Mac用 /tmp，Windows改成 "last_signal.txt"

# ==================== 工具函数 ====================
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

def can_send(direction):  # "long" 或 "short"
    if not os.path.exists(SIGNAL_FILE):
        return True
    try:
        with open(SIGNAL_FILE, "r") as f:
            last_dir, last_time = f.read().strip().split("|")
            last_dt = datetime.fromisoformat(last_time)
            if (datetime.now() - last_dt).total_seconds() < 1800:  # 30分钟内
                return direction != last_dir                     # 不同方向可以发
            return True
    except:
        return True
    return True

def record_signal(direction):
    with open(SIGNAL_FILE, "w") as f:
        f.write(f"{direction}|{datetime.now().isoformat()}")

# ==================== 获取K线 ====================
def get_candles(instId="BTC-USDT", bar="5m", limit=300):
    url = "https://www.okx.com/api/v5/market/candles"
    params = {"instId": instId, "bar": bar, "limit": limit}
    try:
        resp = requests.get(url, params=params, timeout=10).json()
        data = resp["data"]
        df = pd.DataFrame(data, columns=["ts", "o", "h", "l", "c", "vol", "volCcy", "volCcyQuote", "confirm"])
        df["ts"] = pd.to_datetime(df["ts"].astype(int), unit='ms')
        df = df.astype({"o":float, "h":float, "l":float, "c":float, "vol":float})
        df = df[["ts", "o", "h", "l", "c", "vol"]].sort_values("ts").reset_index(drop=True)
        df.columns = ["ts", "open", "high", "low", "close", "vol"]
        return df
    except Exception as e:
        print("获取K线失败:", e)
        return pd.DataFrame()

# ==================== 指标计算 ====================
def add_indicators(df, fast=8, slow=21, bb_period=20):
    df["ema_fast"] = df["close"].ewm(span=fast, adjust=False).mean()
    df["ema_slow"] = df["close"].ewm(span=slow, adjust=False).mean()
    df["ema55"]    = df["close"].ewm(span=55, adjust=False).mean()

    # 趋势
    df["trend"] = (df["ema_fast"] > df["ema_slow"]).astype(int)
    df["bull"]  = df["trend"] == 1
    df["bear"]  = df["trend"] == 0

    # 金叉死叉
    df["cross_up"] = (df["trend"] == 1) & (df["trend"].shift(1) == 0)
    df["cross_dn"] = (df["trend"] == 0) & (df["trend"].shift(1) == 1)

    # 布林带
    df["sma"] = df["close"].rolling(bb_period).mean()
    df["std"] = df["close"].rolling(bb_period).std()
    df["upper"] = df["sma"] + 2 * df["std"]
    df["lower"] = df["sma"] - 2 * df["std"]
    df["band_width"] = df["upper"] - df["lower"]

    # 优化后的扩张 & 突破
    df["bw_expand"]    = df["band_width"] > df["band_width"].shift(1) * 1.09   # 9%以上扩张
    df["break_upper"]  = df["close"] > df["upper"]
    df["break_lower"]  = df["close"] < df["lower"]

    # 放量（1.85倍）
    df["vol_ma20"] = df["vol"].rolling(20).mean()
    df["vol_spike"] = df["vol"] > df["vol_ma20"] * 1.85

    return df

# ==================== 主逻辑 ====================
def main():
    df_5m  = get_candles("BTC-USDT", "5m",  300)
    df_15m = get_candles("BTC-USDT", "15m", 300)

    if df_5m.empty or df_15m.empty or len(df_5m) < 100 or len(df_15m) < 80:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 数据不足，跳过")
        return

    df_5m  = add_indicators(df_5m,  fast=7, slow=18, bb_period=20)   # 5m更灵敏
    df_15m = add_indicators(df_15m, fast=8, slow=21, bb_period=20)

    latest_5m  = df_5m.iloc[-1]
    prev_5m    = df_5m.iloc[-2]
    latest_15m = df_15m.iloc[-1]

    price = latest_5m["close"]
    ts    = latest_5m["ts"].strftime("%m-%d %H:%M")
    vol_ratio = latest_5m["vol"] / latest_5m["vol_ma20"]

    # 15m三线多头/空头排列（超级稳健）
    bull_15m  = latest_15m["ema_fast"] > latest_15m["ema_slow"] > latest_15m["ema55"]
    bear_15m  = latest_15m["ema_fast"] < latest_15m["ema_slow"] < latest_15m["ema55"]

    # 多头不创新低过滤
    no_new_low = latest_5m["low"] >= prev_5m["low"] if latest_5m["cross_up"] else True

    # ==================== 终极多头信号（2025核弹版）===================
    if (latest_5m["cross_up"] and
        latest_5m["vol_spike"] and
        latest_5m["bw_expand"] and
        latest_5m["break_upper"] and
        bull_15m and
        price > latest_15m["ema_slow"] and
        no_new_low and
        can_send("long")):

        strength = "核弹级" if vol_ratio >= 4 else ("超强" if vol_ratio >= 2.8 else "极强")
        msg = f"""🚀 BTC 核弹级多头发射 ‼️‼️‼️
时间：{ts}
价格：${price:.1f} （已强破5m布林上轨！）

【5m引爆四件套】
• EMA7金叉EMA18
• 瞬间放量 {vol_ratio:.2f}倍（{strength}）
• 布林带急速扩张 + 收盘突破上轨
• 金叉后未创新低（真突破）

【15m大趋势完美配合】
• 三线多头排列（EMA8>EMA21>EMA55）
• 价格站稳EMA21 ≈ {latest_15m['ema_slow']:.0f}

→ 2025年最强共振信号！胜率极高！

建议：立即追多 / 回踩 {latest_5m['ema_fast']:.0f} 加仓
目标：+6% → +18%+（牛市可持仓至新高）"""

        send_message(msg)
        record_signal("long")
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 多头核弹信号已发出！")

    # ==================== 终极空头信号 ====================
    if (latest_5m["cross_dn"] and
        latest_5m["vol_spike"] and
        latest_5m["bw_expand"] and
        latest_5m["break_lower"] and
        bear_15m and
        price < latest_15m["ema_slow"] and
        can_send("short")):

        strength = "核弹级" if vol_ratio >= 4 else ("超强" if vol_ratio >= 2.8 else "极强")
        msg = f"""💥 BTC 核弹级空头发射 ‼️‼️‼️
时间：{ts}
价格：${price:.1f} （已击穿5m布林下轨！）

【5m杀跌四件套】
• EMA7死叉EMA18
• 瞬间放量 {vol_ratio:.2f}倍（{strength}）
• 布林带急速扩张 + 收盘跌破下轨

【15m空头趋势确认】
• 三线空头排列
• 价格跌破EMA21 ≈ {latest_15m['ema_slow']:.0f}

→ 极品做空机会！

建议：立即追空 / 反弹至 {latest_5m['ema_fast']:.0f} 加仓
目标：-6% → -18%+"""

        send_message(msg)
        record_signal("short")
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 空头核弹信号已发出！")

    # ==================== 调试信息 ====================
    print(f"[{datetime.now().strftime('%H:%M:%S')}] BTC ${price:.0f} | "
          f"5m={'多' if latest_5m['bull'] else '空'} 放量{vol_ratio:.2f}x | "
          f"15m={'多' if bull_15m else '空'}")

if __name__ == '__main__':
    main()