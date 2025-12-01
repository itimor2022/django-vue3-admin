import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import os
from typing import Optional, Dict, List
from dataclasses import dataclass
import json


# ==================== 配置类 ====================
@dataclass
class Config:
    """配置管理"""
    token: str
    chat_id: str
    inst_id: str = "BTC-USDT"
    timeframes: List[str] = None

    def __post_init__(self):
        if self.timeframes is None:
            self.timeframes = ["15m", "1h", "4h"]


class OKXClient:
    """OKX API客户端"""

    def __init__(self, base_url="https://www.okx.com/api/v5"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Trend Monitor Bot)",
            "Accept": "application/json"
        })

    def get_candles(self, inst_id: str, bar: str = "15m", limit: int = 300) -> pd.DataFrame:
        """获取K线数据"""
        url = f"{self.base_url}/market/candles"
        params = {
            "instId": inst_id,
            "bar": bar,
            "limit": limit
        }

        try:
            response = self.session.get(url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()

            if data.get("code") != "0":
                print(f"API Error: {data.get('msg')}")
                return pd.DataFrame()

            candles = data.get("data", [])
            if not candles:
                return pd.DataFrame()

            # 创建DataFrame
            df = pd.DataFrame(
                candles,
                columns=[
                    "ts", "open", "high", "low", "close",
                    "vol", "volCcy", "volCcyQuote", "confirm"
                ]
            )

            # 数据类型转换
            df["ts"] = pd.to_datetime(df["ts"].astype(int), unit='ms') + pd.Timedelta(hours=7)
            numeric_cols = ["open", "high", "low", "close", "vol"]
            df[numeric_cols] = df[numeric_cols].astype(float)

            # 排序和清理
            df = df[["ts", "open", "high", "low", "close", "vol"]]
            df = df.sort_values("ts").reset_index(drop=True)

            return df

        except Exception as e:
            print(f"获取K线失败 {inst_id}-{bar}: {e}")
            return pd.DataFrame()


class TechnicalIndicators:
    """技术指标计算"""

    @staticmethod
    def calculate_all_indicators(df: pd.DataFrame) -> pd.DataFrame:
        """计算所有技术指标"""
        if len(df) < 100:
            return df

        df = df.copy()

        # 基础价格指标
        df["return"] = df["close"].pct_change() * 100
        df["hl2"] = (df["high"] + df["low"]) / 2
        df["hlc3"] = (df["high"] + df["low"] + df["close"]) / 3

        # EMA系列
        for span in [12, 21, 50, 200]:
            df[f"ema{span}"] = df["close"].ewm(span=span, adjust=False).mean()

        # EMA交叉信号
        df["ema12_21_diff"] = df["ema12"] - df["ema21"]
        df["ema12_21_signal"] = np.sign(df["ema12_21_diff"])
        df["ema_cross_up"] = (df["ema12_21_signal"] == 1) & (df["ema12_21_signal"].shift(1) == -1)
        df["ema_cross_dn"] = (df["ema12_21_signal"] == -1) & (df["ema12_21_signal"].shift(1) == 1)

        # 布林带
        df["sma25"] = df["close"].rolling(window=25, min_periods=1).mean()
        df["std25"] = df["close"].rolling(window=25, min_periods=1).std()
        df["bb_upper"] = df["sma25"] + 2 * df["std25"]
        df["bb_middle"] = df["sma25"]
        df["bb_lower"] = df["sma25"] - 2 * df["std25"]
        df["bb_width"] = (df["bb_upper"] - df["bb_lower"]) / df["bb_middle"]
        df["bb_position"] = (df["close"] - df["bb_lower"]) / (df["bb_upper"] - df["bb_lower"] + 1e-8)

        # RSI
        delta = df["close"].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / (loss + 1e-8)
        df["rsi"] = 100 - (100 / (1 + rs))

        # 成交量指标
        df["vol_sma20"] = df["vol"].rolling(window=20).mean()
        df["vol_ratio"] = df["vol"] / (df["vol_sma20"] + 1e-8)

        # 价格位置
        df["high_20"] = df["high"].rolling(window=20).max()
        df["low_20"] = df["low"].rolling(window=20).min()
        df["price_position"] = (df["close"] - df["low_20"]) / (df["high_20"] - df["low_20"] + 1e-8)

        return df

    @staticmethod
    def calculate_trend_structure(df: pd.DataFrame, lookback: int = 11) -> pd.DataFrame:
        """计算趋势结构"""
        df = df.copy()

        # 寻找波段高低点
        df["swing_high"] = np.nan
        df["swing_low"] = np.nan

        # 使用局部极值点
        for i in range(lookback, len(df) - lookback):
            window = df.iloc[i - lookback:i + lookback + 1]
            if df.iloc[i]["high"] == window["high"].max():
                df.loc[df.index[i], "swing_high"] = df.iloc[i]["high"]
            if df.iloc[i]["low"] == window["low"].min():
                df.loc[df.index[i], "swing_low"] = df.iloc[i]["low"]

        # 趋势结构分析
        swing_highs = df["swing_high"].dropna()
        swing_lows = df["swing_low"].dropna()

        if len(swing_highs) >= 2 and len(swing_lows) >= 2:
            # 获取最近的波段点
            recent_highs = swing_highs.iloc[-2:]
            recent_lows = swing_lows.iloc[-2:]

            hh = recent_highs.iloc[-1] > recent_highs.iloc[-2]
            ll = recent_lows.iloc[-1] < recent_lows.iloc[-2]
            hl = recent_lows.iloc[-1] > recent_lows.iloc[-2]
            lh = recent_highs.iloc[-1] < recent_highs.iloc[-2]

            if hh and hl:
                structure = "上涨趋势 (HH+HL)"
            elif lh and ll:
                structure = "下跌趋势 (LH+LL)"
            elif lh and hl:
                structure = "收敛震荡 (LH+HL)"
            elif hh and ll:
                structure = "扩张震荡 (HH+LL)"
            else:
                structure = "区间震荡"
        else:
            structure = "结构未形成"

        df.loc[df.index[-1], "trend_structure"] = structure
        return df


class TrendAnalyzer:
    """趋势分析器"""

    def __init__(self, signal_cooldown: int = 3):
        self.signal_history = {}
        self.cooldown = signal_cooldown

    def analyze_multitimeframe(self,
                               df_15m: pd.DataFrame,
                               df_1h: pd.DataFrame,
                               df_4h: pd.DataFrame = None) -> Dict:
        """多时间框架分析"""
        analysis = {
            "timestamp": datetime.now(),
            "signals": [],
            "trend_score": 0,
            "volatility": 0,
            "recommendation": "HOLD"
        }

        if df_15m.empty:
            return analysis

        latest_15m = df_15m.iloc[-1]
        latest_1h = df_1h.iloc[-1] if not df_1h.empty else None

        # 趋势评分系统
        trend_score = 0

        # 1. EMA多空排列
        if latest_15m["ema12"] > latest_15m["ema21"]:
            trend_score += 1
        if latest_15m["ema12"] > latest_15m["ema50"]:
            trend_score += 1
        if latest_15m["ema21"] > latest_15m["ema50"]:
            trend_score += 1

        # 2. 多时间框架共振
        if latest_1h is not None:
            if latest_15m["ema12_21_signal"] == latest_1h["ema12_21_signal"]:
                trend_score += 2  # 共振加强

            # 价格位置共振
            if (latest_15m["price_position"] > 0.7 and latest_1h["price_position"] > 0.7):
                analysis["signals"].append("双时间框架高位共振")
            elif (latest_15m["price_position"] < 0.3 and latest_1h["price_position"] < 0.3):
                analysis["signals"].append("双时间框架低位共振")

        # 3. 成交量确认
        if latest_15m["vol_ratio"] > 1.5:
            trend_score += 1
            if latest_15m["return"] > 0:
                analysis["signals"].append("放量上涨")
            else:
                analysis["signals"].append("放量下跌")

        # 4. RSI超买超卖
        if latest_15m["rsi"] > 70:
            analysis["signals"].append("RSI超买")
        elif latest_15m["rsi"] < 30:
            analysis["signals"].append("RSI超卖")

        analysis["trend_score"] = trend_score

        # 生成交易建议
        if trend_score >= 4:
            analysis["recommendation"] = "STRONG_BUY" if latest_15m["ema12_21_signal"] == 1 else "STRONG_SELL"
        elif trend_score >= 2:
            analysis["recommendation"] = "BUY" if latest_15m["ema12_21_signal"] == 1 else "SELL"

        return analysis

    def generate_alert_message(self,
                               analysis: Dict,
                               df_15m: pd.DataFrame,
                               inst_id: str) -> Optional[str]:
        """生成警报消息"""
        if not analysis["signals"]:
            return None

        latest = df_15m.iloc[-1]
        timestamp = latest["ts"].strftime("%m-%d %H:%M")

        # 构建消息
        lines = []
        lines.append(f"📊 {inst_id} - {timestamp}")
        lines.append(f"价格: ${latest['close']:.2f}")
        lines.append(f"趋势评分: {analysis['trend_score']}/5")

        if analysis["signals"]:
            lines.append("📈 信号:")
            for signal in analysis["signals"][:3]:  # 最多显示3个信号
                lines.append(f"  • {signal}")

        lines.append(f"RSI: {latest['rsi']:.1f}")
        lines.append(f"成交量比: {latest['vol_ratio']:.1f}x")
        lines.append(f"建议: {analysis['recommendation']}")

        return "\n".join(lines)


class TelegramBot:
    """Telegram机器人"""

    def __init__(self, token: str, chat_id: str):
        self.token = token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{token}"
        self.session = requests.Session()

    def send_message(self,
                     message: str,
                     parse_mode: str = "HTML",
                     disable_preview: bool = True) -> bool:
        """发送消息"""
        url = f"{self.base_url}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": parse_mode,
            "disable_web_page_preview": disable_preview
        }

        try:
            response = self.session.post(url, json=payload, timeout=10)
            return response.json().get("ok", False)
        except Exception as e:
            print(f"发送消息失败: {e}")
            return False

    def send_signal(self,
                    signal_type: str,
                    message: str,
                    priority: str = "normal") -> bool:
        """发送信号消息（带优先级标记）"""
        priority_icons = {
            "high": "🚨",
            "normal": "📢",
            "low": "📝"
        }
        icon = priority_icons.get(priority, "📢")

        formatted_msg = f"{icon} {signal_type}\n{message}"
        return self.send_message(formatted_msg)


class CryptoTrendMonitor:
    """主监控类"""

    def __init__(self, config: Config):
        self.config = config
        self.okx_client = OKXClient()
        self.telegram_bot = TelegramBot(config.token, config.chat_id)
        self.analyzer = TrendAnalyzer()
        self.indicator_calc = TechnicalIndicators()

        # 状态跟踪
        self.last_analysis = {}
        self.alert_count = 0

    def run_analysis(self):
        """运行一次分析"""
        print(f"\n{'=' * 50}")
        print(f"开始分析 {self.config.inst_id} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print('=' * 50)

        try:
            # 获取多时间框架数据
            dataframes = {}
            for tf in self.config.timeframes:
                df = self.okx_client.get_candles(
                    inst_id=self.config.inst_id,
                    bar=tf,
                    limit=300 if tf == "15m" else 200
                )

                if not df.empty:
                    df = self.indicator_calc.calculate_all_indicators(df)
                    df = self.indicator_calc.calculate_trend_structure(df)
                    dataframes[tf] = df
                    print(f"{tf}: 获取 {len(df)} 根K线，最新时间 {df.iloc[-1]['ts']}")
                else:
                    print(f"{tf}: 数据获取失败")

            # 确保有15m和1h数据
            if "15m" not in dataframes or "1h" not in dataframes:
                print("关键时间框架数据缺失")
                return

            # 多时间框架分析
            analysis = self.analyzer.analyze_multitimeframe(
                dataframes["15m"],
                dataframes["1h"],
                dataframes.get("4h")
            )

            # 生成警报
            alert_message = self.analyzer.generate_alert_message(
                analysis,
                dataframes["15m"],
                self.config.inst_id
            )

            # 发送警报（如果有重要信号）
            if alert_message and analysis["trend_score"] >= 3:
                success = self.telegram_bot.send_signal(
                    signal_type="趋势警报",
                    message=alert_message,
                    priority="high" if analysis["trend_score"] >= 4 else "normal"
                )

                if success:
                    self.alert_count += 1
                    print(f"警报发送成功 (#{self.alert_count})")

            # 保存分析结果
            self.last_analysis = {
                "timestamp": datetime.now(),
                "analysis": analysis,
                "price": dataframes["15m"].iloc[-1]["close"]
            }

            # 控制台输出
            self.print_analysis_summary(dataframes["15m"], analysis)

        except Exception as e:
            print(f"分析过程中发生错误: {e}")
            import traceback
            traceback.print_exc()

    def print_analysis_summary(self, df_15m: pd.DataFrame, analysis: Dict):
        """打印分析摘要"""
        latest = df_15m.iloc[-1]

        print(f"\n📊 分析摘要:")
        print(f"  当前价格: ${latest['close']:.2f}")
        print(f"  24H变化: {df_15m['close'].pct_change().sum() * 100:.2f}%")
        print(f"  趋势强度: {analysis['trend_score']}/5")
        print(f"  趋势结构: {latest.get('trend_structure', 'N/A')}")
        print(f"  RSI: {latest.get('rsi', 0):.1f}")
        print(f"  布林位置: {latest.get('bb_position', 0):.2f}")
        print(f"  建议: {analysis['recommendation']}")

        if analysis["signals"]:
            print(f"  活跃信号: {', '.join(analysis['signals'][:2])}")


# ==================== 主程序 ====================
def main():
    """主函数"""

    # 从环境变量加载配置
    token = os.getenv("TELEGRAM_BOT_TOKEN", "8444348700:AAGqkeUUuB_0rI_4qIaJxrTylpRGh020wU0")
    chat_id = os.getenv("TELEGRAM_CHAT_ID", "-4850300375")
    inst_id = os.getenv("TRADING_PAIR", "BTC-USDT")

    # 创建配置
    config = Config(
        token=token,
        chat_id=chat_id,
        inst_id=inst_id,
        timeframes=["15m", "30m", "1h", "4h"]
    )

    # 创建监控器
    monitor = CryptoTrendMonitor(config)

    # 运行分析
    monitor.run_analysis()


if __name__ == "__main__":
    # 设置pandas显示选项
    pd.set_option('display.max_columns', 20)
    pd.set_option('display.width', 120)
    pd.set_option('display.float_format', '{:.2f}'.format)

    # 运行主程序
    main()

    # 定时运行示例（使用外部调度器如cron或systemd）
    print("\n✅ 分析完成")
    print("建议通过cron job每5-15分钟运行一次此脚本")
    print("示例cron配置: */10 * * * * cd /path/to/script && python trend_monitor.py")
