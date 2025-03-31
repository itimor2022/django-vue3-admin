# -*- coding: utf-8 -*-

import requests
import json
import time
import datetime
import hmac
import base64
import pandas as pd
from lxml import etree

# 设置最大列数，避免只显示部分列
pd.set_option('display.max_columns', 1000)
# 设置最大行数，避免只显示部分行数据
pd.set_option('display.max_rows', 1000)
# 设置显示宽度
pd.set_option('display.width', 1000)
# 设置每列最大宽度，避免属性值或列名显示不全
pd.set_option('display.max_colwidth', 1000)

'''para
'''
t = int(time.time())
period = '15m'
chat_id = "-1002086380388"
GET = "GET"
POST = "POST"
API_URL = 'https://www.okx.com'
SERVER_TIMESTAMP_URL = '/api/v5/public/time'
# header
APPLICATION_JSON = 'application/json'
CONTENT_TYPE = 'Content-Type'
OK_ACCESS_KEY = 'OK-ACCESS-KEY'
OK_ACCESS_SIGN = 'OK-ACCESS-SIGN'
OK_ACCESS_TIMESTAMP = 'OK-ACCESS-TIMESTAMP'
OK_ACCESS_PASSPHRASE = 'OK-ACCESS-PASSPHRASE'


def send_message(msg, chat_id="-4591709428"):
    token1 = "7114302"
    token2 = "389:AAHaFEzUwXj7QC1A20qwi_tJGlkRtP6FOlg"
    url = f"https://api.telegram.org/bot{token1}{token2}/sendMessage?chat_id={chat_id}&text={msg}&parse_mode=HTML"
    r = requests.get(url)
    print(r.json())


##############################################################
##############################################################
'''
mod
'''


class base():
    def clean_dict_none(d: dict) -> dict:
        return {k: d[k] for k in d.keys() if d[k] != None}

    def get_timestamp():
        now = datetime.datetime.utcnow()
        t = now.isoformat("T", "milliseconds")
        return t + "Z"

    def sign(message, secretKey):
        mac = hmac.new(bytes(secretKey, encoding='utf8'), bytes(message, encoding='utf-8'), digestmod='sha256')
        d = mac.digest()
        return base64.b64encode(d)

    def pre_hash(timestamp, method, request_path, body):
        return str(timestamp) + str.upper(method) + request_path + body

    def get_header(api_key, sign, timestamp, passphrase, flag):
        header = dict()
        header[CONTENT_TYPE] = APPLICATION_JSON
        header[OK_ACCESS_KEY] = api_key
        header[OK_ACCESS_SIGN] = sign
        header[OK_ACCESS_TIMESTAMP] = str(timestamp)
        header[OK_ACCESS_PASSPHRASE] = passphrase
        header['FLAG'] = flag
        return header

    def parse_para_to_str(para):
        para = base.clean_dict_none(para)
        url = '?'
        for key, value in para.items():
            url = url + str(key) + '=' + str(value) + '&'
        return url[0:-1]


class Client(object):

    def __init__(self, api_key, api_secret_key, passphrase, use_server_time=False, flag='1'):

        self.API_KEY = api_key
        self.API_SECRET_KEY = api_secret_key
        self.PASSPHRASE = passphrase
        self.use_server_time = use_server_time
        self.flag = flag

    def _request(self, method, request_path, para):

        if method == GET:
            request_path = request_path + base.parse_para_to_str(para)
        # url
        url = API_URL + request_path
        print(url)

        timestamp = base.get_timestamp()

        # sign & header
        if self.use_server_time:
            timestamp = self.get_timestamp()

        body = json.dumps(para) if method == POST else ""

        sign = base.sign(base.pre_hash(timestamp, method, request_path, str(body)), self.API_SECRET_KEY)
        header = base.get_header(self.API_KEY, sign, timestamp, self.PASSPHRASE, self.flag)
        response = None
        if method == GET:
            response = requests.get(url, headers=header)
        elif method == POST:
            response = requests.post(url, data=body, headers=header)

        return response.json()

    def request_with_para(self, method, request_path, para):
        return self._request(method, request_path, para)

    def get_timestamp(self):
        url = API_URL + SERVER_TIMESTAMP_URL
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()['ts']
        else:
            return ""


class MarketAPI(Client):

    def __init__(self, api_key, api_secret_key, passphrase, use_server_time=False, flag='1'):
        Client.__init__(self, api_key, api_secret_key, passphrase, use_server_time, flag)

    def get_history_candlesticks(self, instId, after=None, before=None, bar=None, limit=None):
        url = '/api/v5/market/history-candles'
        para = {'instId': instId, 'after': after, 'before': before, 'bar': bar, 'limit': limit}
        return self.request_with_para(GET, url, para)


def format_time(time_stamp, tz=0):
    dt = datetime.datetime.fromtimestamp(time_stamp)
    # 设置时区
    x = dt.astimezone(datetime.timezone(datetime.timedelta(hours=tz)))
    # 格式化日期
    dd = x.strftime("%Y-%m-%d %H:%M:%S %Z%z")
    return dd

def get_coin1():
    # 放到服务器上执行， 通过api获取数据, 数据就不对
    # 热门榜
    # url = f"https://www.okx.com/priapi/v5/rubik/web/public/hot-rank?countryFilter=1&rank=0&zone=utc8&type=USD&t={t}"
    # 成交额
    # url = f"https://www.okx.com/priapi/v5/rubik/web/public/turn-over-rank?countryFilter=1&rank=0&zone=utc8&period={period}&type=USD&t={t}"
    # 1小时涨幅榜 1H
    url = f"https://aws.okx.com/priapi/v5/rubik/web/public/up-down-rank?period=1H&zone=utc8&type=USDT&countryFilter=1&rank=0"
    # 当天涨幅榜 1D
    # url = f"https://aws.okx.com/priapi/v5/rubik/web/public/up-down-rank?period=1D&zone=utc8&type=USDT&countryFilter=1&rank=0&t={t}"
    # 新币榜
    # url = f"https://aws.okx.com/priapi/v5/rubik/web/public/new-coin-rank?zone=utc8&type=USDT&countryFilter=1&rank=0"
    r = requests.get(url)
    print(r.url)
    c = r.json()['data']['data']
    return c[:20]

def get_coin2():
    # 爬虫爬取页面，不通过api获取数据
    url = "https://www.okx.com/zh-hans/markets/explore/notable-change/5min-up"
    headers = {
        'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1"}
    html = requests.get(url,headers=headers)
    print(html.text)
    selector=etree.HTML(html.text)
    a=selector.xpath('//table/tbody/tr[*]/td[1]/a/text()')
    b = list(dict.fromkeys(a))[:10]
    msg = f'🏆5分钟异动币🏆'
    for i in b:
        msg += f"\n`{i}`\n"
    send_message(msg, chat_id=chat_id)
    return b

def get_tag(df):
    df['max_volume'] = df['volume'].rolling(50).max()
    df['is_max_volume'] = df['volume'] == df['max_volume']
    df['max_price'] = df['high'].rolling(50).max()
    df['is_max_price'] = df['high'] == df['max_price']
    df['min_price'] = df['low'].rolling(50).min()
    df['is_min_price'] = df['low'] == df['min_price']
    df['return_0'] = (df['close'] / df['open'] - 1) * 100 + 0.0000001
    df['is_san_yang'] = False
    df['is_san_yin'] = False
    df['is_san_yang'] = (
            (df['close'].shift(0) >= df['open'].shift(0)) &
            (df['close'].shift(1) >= df['open'].shift(1)) &
            (df['close'].shift(2) >= df['open'].shift(2)) &
            (df['close'].shift(3) >= df['open'].shift(3))
    )
    df['is_san_yin'] = (
            (df['close'].shift(0) <= df['open'].shift(0)) &
            (df['close'].shift(1) <= df['open'].shift(1)) &
            (df['close'].shift(2) <= df['open'].shift(2)) &
            (df['close'].shift(3) <= df['open'].shift(3))
    )
    # ema
    ma_list = [5, 10, 20]
    for ma in ma_list:
        df['ma' + str(ma)] = df["close"].ewm(span=ma, adjust=False).mean()
    df['ma5_ma20_x'] = abs(df['ma5'] / df['ma20'] - 1) * 10000

    df.drop(['max_volume', 'min_price', 'max_price'], axis=1, inplace=True)
    round_dict = {'return_0': 2, 'ma5_ma20_x': 2}
    df = df.round(round_dict)
    return df


def get_coin_data(coin):
    title = f'🏆{period} {coin}🏆\n'
    print(coin)
    print(period)
    result = marketAPI.get_history_candlesticks(coin, bar=period)['data']
    print(result)
    df = pd.DataFrame(result)
    col = ['timestamp', 'open', 'high', 'low', 'close', 'volume', 'amount', '-', '-']
    df.columns = col
    df['datetime'] = pd.to_datetime(df['timestamp'], unit='ms').dt.tz_localize('UTC').dt.tz_convert('Asia/Phnom_Penh')
    columns = ['datetime', 'open', 'high', 'low', 'close', 'volume', 'amount', 'timestamp']
    df = df[columns].sort_values(['timestamp'], ascending=True)
    df[columns[1:]] = df[columns[1:]].apply(pd.to_numeric, errors='coerce').fillna(0.0)
    df = get_tag(df)
    df['max_ma5_ma20_x'] = df['ma5_ma20_x'].rolling(10).max()
    managed_df = df.sort_values(['timestamp'], ascending=False)
    return_0 = managed_df['return_0'].iloc[0]
    dt = str(managed_df['datetime'].iloc[0]).split('07:00')[0]
    print(managed_df)

    if managed_df['is_san_yang'].iloc[0] == 1:
        print("3连阳")
        msg = f'🥃3连阳 {title} 🍄涨幅:{return_0}% \n本地时间:{dt}'
        send_message(msg, chat_id=chat_id)

    if managed_df['is_san_yin'].iloc[0] == 1:
        print("3连阴")
        msg = f'🍭3连阴 {title} 🍄涨幅:{return_0}% \n本地时间:{dt}'
        send_message(msg, chat_id=chat_id)

    if managed_df['is_max_price'].iloc[0] == 1:
        print("最高价")
        msg = f'☘️最高价 {title} 🍄涨幅:{return_0}% \n本地时间:{dt}'
        send_message(msg, chat_id=chat_id)

    if managed_df['is_min_price'].iloc[0] == 1:
        print("最低价")
        msg = f'🐥最低价 {title} 🍄涨幅:{return_0}% \n本地时间:{dt}'
        send_message(msg, chat_id=chat_id)

    if managed_df['is_max_volume'].iloc[0] == 1:
        print("最大量")
        msg = f'🦷最大量 {title} 🍄涨幅:{return_0}% \n本地时间:{dt}'
        send_message(msg, chat_id=chat_id)

    if managed_df['return_0'].iloc[0] >= 0.5:
        print("大阳柱")
        msg = f'🤡大阳柱 {title} 🍄涨幅:{return_0}% \n本地时间:{dt}'
        send_message(msg, chat_id=chat_id)

    if managed_df['return_0'].iloc[0] <= -0.5:
        print("大阴柱")
        msg = f'🥶大阴柱 {title} 🍄涨幅:{return_0}% \n本地时间:{dt}'
        send_message(msg, chat_id=chat_id)

    if managed_df['ma5_ma20_x'].iloc[1] > 20 and managed_df['ma5_ma20_x'].iloc[1] == \
            managed_df['max_ma5_ma20_x'].iloc[0]:
        print("均线趋势")
        msg = f'🔱🔱🔱均线趋势 {title} 🍄涨幅:{return_0}% \n本地时间:{dt} \n趋势值：{managed_df["ma5_ma20_x"].iloc[0]}'
        send_message(msg, chat_id=chat_id)

    df = managed_df[:9]
    if len(df.loc[df.return_0 > 0]) >= 7:
        print("7小阳")
        msg = f'💒7小阳 {title} 🍄涨幅:{return_0}% \n本地时间:{dt}'
        send_message(msg, chat_id=chat_id)
    if len(df.loc[df.return_0 < 0]) >= 7:
        print("7小阴")
        msg = f'🎁7小阴 {title} 🍄涨幅:{return_0}% \n本地时间:{dt}'
        send_message(msg, chat_id=chat_id)
    print(df)

    return df


if __name__ == '__main__':
    api_key = "ff633c9f-eeb1-4073-bfbc-de5a93af409c"
    secret_key = "B0C40F0CE489B41E13B05495110D978D"
    passphrase = "Jay@541430183"
    flag = '1'
    marketAPI = MarketAPI(api_key, secret_key, passphrase, False, flag)
    coins = ['ETH-USDT']
    for coin in coins:
        get_coin_data(coin)
