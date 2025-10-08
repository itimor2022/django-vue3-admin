import requests
import time
import pandas as pd

# 设置显示参数
pd.set_option('display.max_columns', 1000)
pd.set_option('display.max_rows', 1000)
pd.set_option('display.width', 1000)
pd.set_option('display.max_colwidth', 1000)

chat_id = "-4966987679"


def send_message(msg):
    token1 = "844434"
    token2 = "8700:AAGqkeUUuB_0rI_4qIaJxrTylpRGh020wU0"
    url = f"https://api.telegram.org/bot{token1}{token2}/sendMessage?chat_id={chat_id}&text={msg}&parse_mode=HTML"
    r = requests.get(url)
    print(r.json())


def get_tag(df):
    df['max_price'] = df['high'].rolling(10).max()
    df['is_max_price'] = df['high'] == df['max_price']
    df['min_price'] = df['low'].rolling(10).min()
    df['is_min_price'] = df['low'] == df['min_price']
    eps = 1e-8
    df['return_0'] = (df['close'] / (df['open'] + eps) - 1) * 100

    # 连续K线
    df['is_yang_two'] = (
            (df['close'].shift(1) >= df['open'].shift(1)) &
            (df['close'].shift(0) >= df['open'].shift(0))
    )
    df['is_yin_two'] = (
            (df['close'].shift(1) <= df['open'].shift(1)) &
            (df['close'].shift(0) <= df['open'].shift(0))
    )

    # BOLL
    window = 25
    num_of_std = 2
    df['SMA'] = df['close'].rolling(window=window).mean()
    df['STD'] = df['close'].rolling(window=window).std()
    df['upper'] = df['SMA'] + (df['STD'] * num_of_std)
    df['lower'] = df['SMA'] - (df['STD'] * num_of_std)
    df['yang_sma_x'] = (df['return_0'] > 0) & (df['open'] < df['SMA']) & (df['close'] > df['SMA'])
    df['yin_sma_x'] = (df['return_0'] < 0) & (df['close'] < df['SMA']) & (df['open'] > df['SMA'])
    df['is_high_boll'] = (df['return_0'] > 0) & (df['close'] > df['upper'])
    df['is_low_boll'] = (df['return_0'] < 0) & (df['low'] < df['lower'])

    # 下影线幅度（百分比）—— 适用于阳线和阴线
    df['shadow_lower'] = ((df[['open', 'close']].min(axis=1) / df['low']) - 1) * 100
    df['shadow_lower'] = df['shadow_lower'].clip(lower=0).round(2)

    df.drop(['min_price', 'max_price'], axis=1, inplace=True)
    df = df.round({'return_0': 2, 'close': 2, 'shadow_lower': 2})
    return df


def get_coin_data(coin="BTC-USDT"):
    title = f'⏰30分钟 {coin}⏰\n'
    api_url = "https://www.okx.com/api/v5/market/candles"
    params = {
        "instId": coin,
        "bar": "30m",  # 60分钟
        "limit": "100"
    }

    r = requests.get(api_url, params=params)
    result = r.json()

    if result.get("code") != "0":
        print("API错误:", result)
        return

    # OKX返回是 [ts, o, h, l, c, vol, volCcy, volCcyQuote, confirm]
    data = result['data']
    df = pd.DataFrame(data, columns=["timestamp", "open", "high", "low", "close", "-", "-", "-", "-"])
    df['timestamp'] = pd.to_datetime(df['timestamp'].astype(float), unit='ms').dt.tz_localize('UTC').dt.tz_convert(
        'Asia/Phnom_Penh')
    # 转换数据类型
    df[['open', 'high', 'low', 'close']] = df[['open', 'high', 'low', 'close']].astype(float)

    columns = ['timestamp', 'open', 'high', 'low', 'close']
    df = df[columns].sort_values(['timestamp'], ascending=True)

    df = get_tag(df)
    managed_df = df.sort_values(['timestamp'], ascending=False)
    latest = managed_df.iloc[0]

    return_0 = latest['return_0']
    close = latest['close']
    timestamp = latest['timestamp']

    # 触发boll信号,下跌趋势
    past_low_boll = df[df['is_low_boll']].iloc[-1:]
    if not past_low_boll.empty:
        last_close = past_low_boll['close'].values[0]
        prev_close = df['close'].iloc[-2]
        if (close < last_close) and (prev_close > last_close):
            msg = f'⚠️报警: {title} 当前收盘价 {close} 小于上次BOLL下轨触发时的收盘价 {last_close}'
            send_message(msg)

    # 触发boll信号,上涨趋势
    past_close_boll = df[df['is_high_boll']].iloc[-1:]
    if not past_close_boll.empty:
        last_close = past_close_boll['close'].values[0]
        prev_close = df['close'].iloc[-2]
        if (close > last_close) and (prev_close < last_close):
            msg = f'⚠️报警: {title} 当前收盘价 {close} 大于上次BOLL上轨触发时的收盘价 {last_close}'
            send_message(msg)

    # 如果这次最低价比上一次出现的最低价高，则报警
    past_min = df[df['is_min_price']].iloc[-2:-1]  # 上一次最低价信号
    if not past_min.empty:
        last_min_low = past_min['low'].values[0]
        current_low = latest['low']
        if current_low > last_min_low:
            msg = f'🚨提醒: {title} 当前最低价 {current_low} 高于上次最低价信号 {last_min_low}'
            send_message(msg)

    # 如果距离上次上穿中线后，后面连续7次都在中线上方，则报警
    last_cross = df[df['yang_sma_x']].iloc[-1:]  # 找到最后一次阳柱上穿中线的K线
    if not last_cross.empty:
        last_cross_index = last_cross.index[0]
        # 获取上穿之后的7根K线（不含上穿那根）
        after_cross = df.loc[last_cross_index + 1:].head(7)
        # 确保有足够的K线
        if len(after_cross) == 7:
            # 判断这7根K线是否全部在中线上方
            if (after_cross['close'] > after_cross['SMA']).all():
                msg = f'⚡️趋势确认: {title} 上次上穿中线后连续7根K线均在中线上方，强势趋势确认'
                send_message(msg)

    # 从上一次下穿中线后，连续7次都在中线下方则报警
    last_cross_down_index = df[df['yin_sma_x'] == True].index.max()
    if pd.notna(last_cross_down_index):
        after_df = df.loc[last_cross_down_index + 1:]
        if len(after_df) >= 7:
            below_count = (after_df['close'] < after_df['SMA']).head(7).sum()
            if below_count == 7:
                msg = f'⚠️趋势转弱: {title} 从上次下穿中线后，连续7根K线都收盘在中线下方'
                send_message(msg)

    # 触发信号
    if latest['is_yang_two']:
        msg = f'🥃2连阳 {title} 📈涨幅:{return_0}% 👁当前价:{close}'
        send_message(msg)

    if latest['is_yin_two']:
        msg = f'🍭2连阴 {title} 📉涨幅:{return_0}% 👁当前价:{close}'
        send_message(msg)

    if latest['yang_sma_x']:
        msg = f'🦷阳柱上穿中线 {title} 📊涨幅:{return_0}% 👁当前价:{close}'
        send_message(msg)

    if latest['yin_sma_x']:
        msg = f'🦷阴柱下穿中线 {title} 📊涨幅:{return_0}% 👁当前价:{close}'
        send_message(msg)

    if latest['shadow_lower'] >= 0.51:
        msg = f'🔥下影线太长: {title} 反弹上涨趋势'
        send_message(msg)

    print("*********************--------------*********************")
    print(timestamp)
    print(df)
    return df


if __name__ == '__main__':
    code = "ETH-USDT"  # OKX 交易对
    get_coin_data(code)
