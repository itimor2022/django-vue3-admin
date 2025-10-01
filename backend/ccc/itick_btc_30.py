import requests
import time
import pandas as pd

# 设置最大列数，避免只显示部分列
pd.set_option('display.max_columns', 1000)
# 设置最大行数，避免只显示部分行数据
pd.set_option('display.max_rows', 1000)
# 设置显示宽度
pd.set_option('display.width', 1000)
# 设置每列最大宽度，避免属性值或列名显示不全
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
    df['is_yang_two'] = False
    df['is_yin_two'] = False
    df['is_yang_two'] = (
            (df['close'].shift(1) >= df['open'].shift(1)) &
            (df['close'].shift(0) >= df['open'].shift(0))
    )
    df['is_yin_two'] = (
            (df['close'].shift(1) <= df['open'].shift(1)) &
            (df['close'].shift(0) <= df['open'].shift(0))
    )
    df['is_yang_three'] = False
    df['is_yin_three'] = False
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

    # ema
    ma_list = [5, 10, 20]
    for ma in ma_list:
        df['ma' + str(ma)] = df["close"].ewm(span=ma, adjust=False).mean()
    df['ma5_ma20_x'] = abs(df['ma5'] / df['ma20'] - 1) * 10000

    # bool
    """
       计算布林线指标。
        参数:
        data: pandas.DataFrame，包含日期和收盘价两列数据。
        window: 移动平均线窗口大小，默认为20。
        num_of_std: 标准差倍数，用于计算上下轨，默认为2。
        返回:
        pandas.DataFrame，包含原始数据和布林线指标（中轨，上轨，下轨）。
    """
    window = 20
    num_of_std = 2
    # 计算简单移动平均线
    df['SMA'] = df['close'].rolling(window=window).mean()
    # 计算标准差
    df['STD'] = df['close'].rolling(window=window).std()
    # 计算上轨和下轨
    df['upper'] = df['SMA'] + (df['STD'] * num_of_std)
    df['lower'] = df['SMA'] - (df['STD'] * num_of_std)

    df.drop(['max_volume', 'min_price', 'max_price'], axis=1, inplace=True)
    round_dict = {'return_0': 2, 'ma5_ma20_x': 2, 'close': 2}
    df = df.round(round_dict)
    return df


def get_coin_data(coin):
    title = f'🏆30分钟 {coin}🏆\n'
    api_url = 'https://api.itick.org/crypto/kline'
    params = {
        'region': 'ba',
        'code': coin,
        'kType': 4,  # 周期 1分钟、2五分钟、3十分钟、4三十分钟、5一小时、6两小时、7四小时、8一天、9一周、10一月
        'et': int(time.time() * 1000),  # 查询截止时间
        'limit': 100
    }
    headers = {
        'Content-Type': 'application/json',
        'accept': 'application/json',
        'token': '966110b446bb43a5b409a89ebc502ada18ae4fa6df804ee688e5c9efe9d97d58'
    }
    r = requests.get(url=api_url, params=params, headers=headers)
    result = r.json()['data']
    # result = q['data']
    print(result)
    df = pd.DataFrame(result)
    col = ['-', 'close', 'timestamp', 'volume', 'high', 'low', 'open']
    df.columns = col
    df['datetime'] = pd.to_datetime(df['timestamp'], unit='ms').dt.tz_localize('UTC').dt.tz_convert('Asia/Phnom_Penh')
    columns = ['datetime', 'open', 'high', 'low', 'close', 'volume', 'timestamp']
    df = df[columns].sort_values(['timestamp'], ascending=True)
    df[columns[1:]] = df[columns[1:]].apply(pd.to_numeric, errors='coerce').fillna(0.0)
    df = get_tag(df)
    managed_df = df.sort_values(['timestamp'], ascending=False)
    latest = managed_df.iloc[0]
    return_0 = latest['return_0']
    close = latest['close']
    print(managed_df)

    if latest['is_yang_two']:
        print("2连阳")
        msg = f'🥃2连阳 {title} 🍄涨幅:{return_0}% 👁当前价:{close}'
        send_message(msg, chat_id=chat_id)

    if latest['is_yin_two']:
        print("2连阴")
        msg = f'🍭2连阴 {title} 🍄涨幅:{return_0}% 👁当前价:{close}'
        send_message(msg, chat_id=chat_id)

    if latest['is_yang_three']:
        print("3连阳")
        msg = f'🥃3连阳 {title} 🍄涨幅:{return_0}% 👁当前价:{close}'
        send_message(msg, chat_id=chat_id)

    if latest['is_yang_three']:
        print("3连阴")
        msg = f'🍭3连阴 {title} 🍄涨幅:{return_0}% 👁当前价:{close}'
        send_message(msg, chat_id=chat_id)

    if managed_df['is_max_price'].iloc[0] == 1:
        print("最高价")
        msg = f'☘️最高价 {title} 🍄涨幅:{return_0}% 👁当前价:{close}'
        send_message(msg, chat_id=chat_id)

    if managed_df['is_min_price'].iloc[0] == 1:
        print("最低价")
        msg = f'🐥最低价 {title} 🍄涨幅:{return_0}% 👁当前价:{close}'
        send_message(msg, chat_id=chat_id)

    if managed_df['is_max_volume'].iloc[0] == 1:
        print("最大量")
        msg = f'🦷最大量 {title} 🍄涨幅:{return_0}% 👁当前价:{close}'
        send_message(msg, chat_id=chat_id)

    if return_0 >= 0.5:
        print("大阳柱")
        msg = f'🤡大阳柱 {title} 🍄涨幅:{return_0}% 👁当前价:{close}'
        send_message(msg, chat_id=chat_id)

    if return_0 <= -0.5:
        print("大阴柱")
        msg = f'🥶大阴柱 {title} 🍄涨幅:{return_0}% 👁当前价:{close}'
        send_message(msg, chat_id=chat_id)

    return df


if __name__ == '__main__':
    code = 'BTCUSDT'
    get_coin_data(code)
