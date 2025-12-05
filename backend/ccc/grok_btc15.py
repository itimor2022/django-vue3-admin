import requests
import pandas as pd
from datetime import datetime
import os

# ==================== 配置区 ====================
chat_id = "-4850300375"
TOKEN = "8444348700:AAGqkeUUuB_0rI_4qIaJxrTylpRGh020wU0"
BASE_URL = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

SIGNAL_FILE = "15m_signal_lock.txt"   # 防刷屏文件

# ==================== 工具函数 ====================
def send_message(text):
    try:
        requests.post(BASE_URL, json={                 # 改用POST更稳定
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": True
        }, timeout=10)
    except:
        pass

def can_send(direction):  # direction: "long" 或 "short"
    if not os.path.exists(SIGNAL_FILE):
        return True
    try:
        with open(SIGNAL_FILE, "r", encoding="utf-8") as f:
            last_dir, last_time = f.read().strip().split("|")
            last_dt = datetime.fromisoformat(last_time)
            if (datetime.now() - last_dt).total_seconds() < 1800:  # 30分钟锁
                return direction != last_dir
            return True
    except:
        return True

def record_signal(direction):
    with open(SIGNAL_FILE, "w", encoding="utf-8") as f:
        f.write(f"{direction}|{datetime.now().isoformat()}")

# ==================== 主逻辑 ====================
def get_candles():
    url = "https://www.okx.com/api/v5/market/candles"
    params = {"instId": "BTC-USDT", "bar": "15m", "limit": 200}
    try:
        data = requests.get(url, params=params, timeout=10).json()["data"]
        df = pd.DataFrame(data, columns=["ts", "o", "h", "l", "c", "vol", "volCcy", "volCcyQuote", "confirm"])
        df["ts"] = pd.to_datetime(df["ts"].astype(int), unit='ms')
        df = df.astype({"o":float, "h":float, "l":float, "c":float, "vol":float})
        df = df[["ts", "o", "h", "l", "c", "vol"]].sort_values("ts").reset_index(drop=True)
        df.columns = ["ts", "open", "high", "low", "close", "vol"]
        return df
    except:
        return pd.DataFrame()

def analyze():
    df = get_candles()
    if df.empty or len(df) < 80:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 数据不足")
        return

    # ============ 指标计算 ============
    df["ema8"]  = df["close"].ewm(span=8,  adjust=False).mean()
    df["ema21"] = df["close"].ewm(span=21, adjust=False).mean()
    df["sma20"] = df["close"].rolling(20).mean()
    df["std20"] = df["close"].rolling(20).std()
    df["upper"] = df["sma20"] + 2 * df["std20"]
    df["lower"] = df["sma20"] - 2 * df["std20"]
    df["bw"]    = df["upper"] - df["lower"]
    df["bw_expand"] = df["bw"] > df["bw"].shift(1) * 1.08   # 8%扩张

    df["vol_ma20"] = df["vol"].rolling(20).mean()
    df["vol_spike"] = df["vol"] > df["vol_ma20"] * 1.82    # 关键：1.82倍

    df["bull"] = df["ema8"] > df["ema21"]
    df["cross_up"]   = df["bull"] & (~df["bull"].shift(1).fillna(False))
    df["cross_dn"]   = (~df["bull"]) & (df["bull"].shift(1).fillna(False))

    df["break_upper"] = df["close"] > df["upper"]
    df["break_lower"] = df["close"] < df["lower"]

    latest = df.iloc[-1]
    prev   = df.iloc[-2]
    price  = latest["close"]
    ts     = latest["ts"].strftime("%m-%d %H:%M")
    vol_ratio = latest["vol"] / latest["vol_ma20"]

    # ============ 终极多头信号（极少但极准） ============
    if (latest["cross_up"] and
        latest["vol_spike"] and
        latest["bw_expand"] and
        latest["break_upper"] and
        latest["low"] >= prev["low"] and   # 金叉后不创新低
        price > latest["sma20"] and        # 在中轨之上
        can_send("long")):

        strength = "核弹级" if vol_ratio >= 3.5 else "超强"
        msg = f"""BTC 15m 核弹多头发射

时间：{ts}
价格：${price:.1f}

【核心确认】
• EMA8 金叉 EMA21
• 放量 {vol_ratio:.2f}倍（{strength}）
• 布林带张口 + 收盘强破上轨
• 金叉后未创新低（真突破！）

趋势已启动，大概率开启主升浪
建议：立即追多 或 回踩 EMA8 加仓
目标：+8% ~ +25%+"""

        send_message(msg)
        record_signal("long")
        print(f"多头核弹信号已发出")

    # ============ 终极空头信号（谨慎追空） ============
    if (latest["cross_dn"] and
        latest["vol_spike"] and
        latest["bw_expand"] and
        latest["break_lower"] and
        price < latest["sma20"] and        # 跌破中轨
        can_send("short")):

        msg = f"""BTC 15m 空头趋势启动

时间：{ts}
价格：${price:.1f}

【核心确认】
• EMA8 死叉 EMA21
• 放量 {vol_ratio:.2f}倍
• 收盘击穿布林下轨 + 带宽扩张

下跌趋势确立，可短线顺势做空
建议：现价轻仓空 / 反弹 EMA8 再入
目标：-7% ~ -15%"""

        send_message(msg)
        record_signal("short")

    # ============ 疯狂追涨/恐慌提示（可选） ============
    if (prev["break_upper"] and latest["break_upper"] and latest["vol_spike"]):
        msg = f"""BTC 15m 极度亢奋！

{ts} | ${price:.1f}
连续两根收在上轨之上 + 放量
冲顶风险极高！谨慎追涨"""
        send_message(msg)

    if (prev["break_lower"] and latest["break_lower"] and latest["vol_spike"]):
        msg = f"""BTC 15m 极端恐慌！

{ts} | ${price:.1f}
连续击穿下轨，极度超卖
注意：可能V型反转，空单减仓！"""
        send_message(msg)

    # ============ 调试信息 ============
    print(f"[{datetime.now().strftime('%H:%M:%S')}] BTC 15m ${price:.0f} | "
          f"趋势={'多' if latest['bull'] else '空'} | 放量{vol_ratio:.2f}x | 带宽扩:{latest['bw_expand']}")

if __name__ == '__main__':
    analyze()