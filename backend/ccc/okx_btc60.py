import requests
import time
import pandas as pd

# 设置显示参数
pd.set_option('display.max_columns', 1000)
pd.set_option('display.max_rows', 1000)
pd.set_option('display.width', 1000)
pd.set_option('display.max_colwidth', 1000)

chat_id = "-1002086380388"

def send_message(msg, chat_id="-4591709428"):
    token1 = "7114302"
    token2 = "389:AAHaFEzUwXj7QC1A20qwi_tJGlkRtP6FOlg"
    url = f"https://api.telegram.org/bot{token1}{token2}/sendMessage?chat_id={chat_id}&text={msg}&parse_mode=HTML"
    r = requests.get(url)
    print(r.json())

def get_tag(df):
    df['max_volume'] = df['volume'].rolling(8).max()
    df['is_max_volume'] = df['volume'] == df['max_volume']
    df['max_price'] = df['high'].rolling(8).max()
    df['is_max_price'] = df['high'] == df['max_price']
    df['min_price'] = df['low'].rolling(8).min()
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
    df['is_yang_three'] = (
        (df['close'].shift(2) >= df['open'].shift(2)) &
        (df['close'].shift(1) >= df['open'].shift(1)) &
        (df['close'].shift(0) >= df['open'].shift(0))
    )
    df['is_yin_three'] = (
        (df['close'].shift(2) <= df['open'].shift(2)) &
        (df['close'].shift(1) <= df['open'].shift(1)) &
        (df['close'].shift(0) <= df['open'].shift(0))
    )

    # EMA
    for ma in [5, 10, 20]:
        df['ma' + str(ma)] = df["close"].ewm(span=ma, adjust=False).mean()
    df['ma5_ma20_x'] = abs(df['ma5'] / df['ma20'] - 1) * 10000

    # BOLL
    window = 20
    num_of_std = 2
    df['SMA'] = df['close'].rolling(window=window).mean()
    df['STD'] = df['close'].rolling(window=window).std()
    df['upper'] = df['SMA'] + (df['STD'] * num_of_std)
    df['lower'] = df['SMA'] - (df['STD'] * num_of_std)

    df.drop(['max_volume', 'min_price', 'max_price'], axis=1, inplace=True)
    df = df.round({'return_0': 2, 'ma5_ma20_x': 2, 'close': 2})
    return df

def get_coin_data(coin="BTC-USDT"):
    title = f'⏰60分钟 {coin}⏰\n'
    api_url = "https://www.okx.com/api/v5/market/candles"
    params = {
        "instId": coin,
        "bar": "1H",   # 60分钟
        "limit": "100"
    }

    r = requests.get(api_url, params=params)
    result = r.json()

    if result.get("code") != "0":
        print("API错误:", result)
        return

    # OKX返回是 [ts, o, h, l, c, vol, volCcy, volCcyQuote, confirm]
    data = result['data']
    df = pd.DataFrame(data, columns=["timestamp", "open", "high", "low", "close", "volume", "-", "-", "-"])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms').dt.tz_localize('UTC').dt.tz_convert('Asia/Phnom_Penh')

    # 转换数据类型
    df[['open','high','low','close','volume']] = df[['open','high','low','close','volume']].astype(float)

    columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
    df = df[columns].sort_values(['timestamp'], ascending=True)

    df = get_tag(df)
    managed_df = df.sort_values(['timestamp'], ascending=False)
    latest = managed_df.iloc[0]

    return_0 = latest['return_0']
    close = latest['close']

    # 触发信号
    if latest['is_yang_two']:
        msg = f'🥃2连阳 {title} 📈涨幅:{return_0}% 👁当前价:{close}'
        send_message(msg, chat_id=chat_id)

    if latest['is_yin_two']:
        msg = f'🍭2连阴 {title} 📉涨幅:{return_0}% 👁当前价:{close}'
        send_message(msg, chat_id=chat_id)

    if latest['is_yang_three']:
        msg = f'🥃3连阳 {title} 📈涨幅:{return_0}% 👁当前价:{close}'
        send_message(msg, chat_id=chat_id)

    if latest['is_yin_three']:
        msg = f'🍭3连阴 {title} 📉涨幅:{return_0}% 👁当前价:{close}'
        send_message(msg, chat_id=chat_id)

    if latest['is_max_price']:
        msg = f'☘️最高价 {title} 📈涨幅:{return_0}% 👁当前价:{close}'
        send_message(msg, chat_id=chat_id)

    if latest['is_min_price']:
        msg = f'🐥最低价 {title} 📉涨幅:{return_0}% 👁当前价:{close}'
        send_message(msg, chat_id=chat_id)

    if latest['is_max_volume']:
        msg = f'🦷最大量 {title} 📊涨幅:{return_0}% 👁当前价:{close}'
        send_message(msg, chat_id=chat_id)

    if return_0 >= 0.5:
        msg = f'🤡大阳柱 {title} 📈涨幅:{return_0}% 👁当前价:{close}'
        send_message(msg, chat_id=chat_id)

    if return_0 <= -0.5:
        msg = f'🥶大阴柱 {title} 📉涨幅:{return_0}% 👁当前价:{close}'
        send_message(msg, chat_id=chat_id)

    return df

if __name__ == '__main__':
    code = "BTC-USDT"  # OKX 交易对
    get_coin_data(code)
