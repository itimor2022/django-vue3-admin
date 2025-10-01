import requests
import time
import pandas as pd

# 设置 pandas 显示选项
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
    df['max_price'] = df['high'].rolling(8).max()
    df['is_max_price'] = df['high'] == df['max_price']
    df['min_price'] = df['low'].rolling(8).min()
    df['is_min_price'] = df['low'] == df['min_price']
    eps = 1e-8
    df['return_0'] = (df['close'] / (df['open'] + eps) - 1) * 100

    # 连阳 / 连阴
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

    # 均线
    for ma in [5, 10, 20]:
        df['ma' + str(ma)] = df["close"].ewm(span=ma, adjust=False).mean()
    df['ma5_ma20_x'] = abs(df['ma5'] / df['ma20'] - 1) * 10000

    # 布林带
    window = 20
    num_of_std = 2
    df['SMA'] = df['close'].rolling(window=window).mean()
    df['STD'] = df['close'].rolling(window=window).std()
    df['upper'] = df['SMA'] + (df['STD'] * num_of_std)
    df['lower'] = df['SMA'] - (df['STD'] * num_of_std)

    round_dict = {'return_0': 2, 'ma5_ma20_x': 2, 'close': 2}
    df = df.round(round_dict)
    return df


def get_coin_data(coin="BTC-USDT"):
    title = f'🏆30分钟 {coin}🏆\n'
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
    df = pd.DataFrame(data, columns=["ts", "open", "high", "low", "close", "volume", "volCcy"])
    df = df.astype({"open": float, "high": float, "low": float, "close": float, "volume": float})
    df["timestamp"] = pd.to_datetime(df["ts"], unit="ms").dt.tz_localize("UTC").dt.tz_convert("Asia/Phnom_Penh")
    df = df.sort_values("timestamp", ascending=True).reset_index(drop=True)

    df = get_tag(df)
    managed_df = df.sort_values(['timestamp'], ascending=False)
    latest = managed_df.iloc[0]

    return_0 = latest['return_0']
    close = latest['close']
    print(managed_df.head())

    if latest['is_yang_two']:
        msg = f'🥃2连阳 {title} 🍄涨幅:{return_0}% 👁当前价:{close}'
        send_message(msg, chat_id=chat_id)

    if latest['is_yin_two']:
        msg = f'🍭2连阴 {title} 🍄涨幅:{return_0}% 👁当前价:{close}'
        send_message(msg, chat_id=chat_id)

    if latest['is_yang_three']:
        msg = f'🥃3连阳 {title} 🍄涨幅:{return_0}% 👁当前价:{close}'
        send_message(msg, chat_id=chat_id)

    if latest['is_yin_three']:
        msg = f'🍭3连阴 {title} 🍄涨幅:{return_0}% 👁当前价:{close}'
        send_message(msg, chat_id=chat_id)

    if latest['is_max_price']:
        msg = f'☘️最高价 {title} 🍄涨幅:{return_0}% 👁当前价:{close}'
        send_message(msg, chat_id=chat_id)

    if latest['is_min_price']:
        msg = f'🐥最低价 {title} 🍄涨幅:{return_0}% 👁当前价:{close}'
        send_message(msg, chat_id=chat_id)

    if return_0 >= 0.5:
        msg = f'🤡大阳柱 {title} 🍄涨幅:{return_0}% 👁当前价:{close}'
        send_message(msg, chat_id=chat_id)

    if return_0 <= -0.5:
        msg = f'🥶大阴柱 {title} 🍄涨幅:{return_0}% 👁当前价:{close}'
        send_message(msg, chat_id=chat_id)

    return df


if __name__ == "__main__":
    get_coin_data("BTC-USDT")
