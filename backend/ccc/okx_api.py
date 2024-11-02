# -*- coding: utf-8 -*-
"""
Created on Wen May 24 02:47:46 2023

@author: 35003
"""
import requests
import json
import time
import datetime
import hmac
import base64
from sys import argv

'''para
'''
typ = argv[1]
t = int(time.time())
API_URL = 'https://www.okx.com'
GET = "GET"
VOLUMNE = '/api/v5/market/platform-24-volume'
TICKER_INFO = '/api/v5/market/ticker'
ORDER_BOOKS = '/api/v5/market/books'
SERVER_TIMESTAMP_URL = '/api/v5/public/time'
POST = "POST"
# header
APPLICATION_JSON = 'application/json'
CONTENT_TYPE = 'Content-Type'
OK_ACCESS_KEY = 'OK-ACCESS-KEY'
OK_ACCESS_SIGN = 'OK-ACCESS-SIGN'
OK_ACCESS_TIMESTAMP = 'OK-ACCESS-TIMESTAMP'
OK_ACCESS_PASSPHRASE = 'OK-ACCESS-PASSPHRASE'


def stamp2time(timeStamp):  # 时间戳转日期函数
    """
    功能：将时间戳转换成日期函数 例如：1606708276268 ==》2020-11-30 11:51:16
    参数：timeStamp 时间戳，类型 double 例如：1606708276268
    返回值：日期， 类型：字符串 2020-11-30 11:51:16
    """
    time_local = time.localtime(int(timeStamp) / 1000)
    dt = time.strftime("%Y-%m-%d %H:%M:%S", time_local)
    return dt


def send_message(msg, chat_id="-4591709428"):
    token1 = "7114302"
    token2 = "389:AAHaFEzUwXj7QC1A20qwi_tJGlkRtP6FOlg"
    url = f"https://api.telegram.org/bot{token1}{token2}/sendMessage?chat_id={chat_id}&text={msg}"
    r = requests.get(url)
    print(r)


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

    def get_history_candlesticks(self, instId, after=None, before=None, bar='3m', limit=None):
        url = '/api/v5/market/history-candles'
        para = {'instId': instId, 'after': after, 'before': before, 'bar': bar, 'limit': limit}
        return self.request_with_para(GET, url, para)


def get_pairs(typ):
    period = '1H'
    exclude_pair_list = ['USDC-USDT', 'BTC-USDT', 'ETH-USDT', 'XRP-USDT', 'BCH-USDT', 'LTC-USDT', 'TON-USDT']
    if typ == 'hot':
        # 热门榜
        url = f"https://www.okx.com/priapi/v5/rubik/web/public/hot-rank?countryFilter=1&rank=0&zone=utc8&period={period}&type=USDT&t={t}"
    else:
        # 成交额
        url = f"https://www.okx.com/priapi/v5/rubik/web/public/turn-over-rank?countryFilter=1&rank=0&zone=utc8&period={period}&type=USDT&t={t}"
    r = requests.get(url)
    c = r.json()['data']['data']
    c_list = []
    for i in c:
        p = i['instId']
        if p not in exclude_pair_list:
            c_list.append(p)
    return c_list[:100]


def get_btc():
    result = marketAPI.get_history_candlesticks('BTC-USDT')['data']
    print(result)
    m = (float(result[0][4]) / float(result[0][1]) - 1) * 100
    n = abs(m)
    if n > 0.09:
        if m > 0:
            send_message(f'-*-3分钟btc涨跌幅-*- | +{n}%')
        else:
            send_message(f'-*-3分钟btc涨跌幅-*- | -{n}%')


def main():
    n = 5
    # pair_list = ['CATI-USDT']
    pair_list = get_pairs(typ)
    s_list = list()
    for index, pair in enumerate(pair_list):
        print(index)
        print(pair)
        result = marketAPI.get_history_candlesticks(pair)['data']
        m = float(result[1][5]) / float(result[0][5])
        if m > n:
            print(m)
            print(result)
            s = f"{pair} {m}"
            s_list.append(s)
            send_message(f'-*-3分钟成交量{n}倍-*-\n' + result, chat_id="-1002086380388")
    if len(s_list) > 0:
        print("发送消息")
        all_msg = '\n'.join(s_list)
        print(all_msg)
        send_message(f'-*-3分钟成交量{n}倍-*-\n' + all_msg)


if __name__ == '__main__':
    api_key = "ff633c9f-eeb1-4073-bfbc-de5a93af409c"
    secret_key = "B0C40F0CE489B41E13B05495110D978D"
    passphrase = "Jay@541430183"
    flag = '1'
    marketAPI = MarketAPI(api_key, secret_key, passphrase, False, flag)
    get_btc()
    main()
