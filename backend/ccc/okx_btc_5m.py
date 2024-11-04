# -*- coding: utf-8 -*-

import requests
import json
import time
import datetime
import hmac
import base64

'''para
'''
t = int(time.time())
period = '5m'
title = f'-*- {period} btc -*-\n'
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


def stamp2time(timeStamp):  # 时间戳转日期函数
    """
    功能：将时间戳转换成日期函数 例如：1606708276268 ==》2020-11-30 11:51:16
    参数：timeStamp 时间戳，类型 double 例如：1606708276268
    返回值：日期， 类型：字符串 2020-11-30 11:51:16
    """
    time_local = time.localtime(int(timeStamp) / 1000)
    dt = time.strftime("%Y-%m-%d %H:%M:%S", time_local)
    return dt


emoji_dict = {
    "laugh": "%f0%9f%98%82",
    "angry": "%f0%9f%98%a1",
    "evil": "%f0%9f%98%88",
    "kiss_laugh": "%f0%9f%98%8d",
    "han": "%f0%9f%98%93",
    "kiss": "%f0%9f%98%98",
    "fail": "%f0%9f%98%a8",
}


def send_message(msg, chat_id="-4591709428"):
    token1 = "7114302"
    token2 = "389:AAHaFEzUwXj7QC1A20qwi_tJGlkRtP6FOlg"
    url = f"https://api.telegram.org/bot{token1}{token2}/sendMessage?chat_id={chat_id}&text={msg}&parse_modwarninge=Markdown"
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

    def get_history_candlesticks(self, instId, after=None, before=None, bar=None, limit=None):
        url = '/api/v5/market/history-candles'
        para = {'instId': instId, 'after': after, 'before': before, 'bar': bar, 'limit': limit}
        return self.request_with_para(GET, url, para)


def get_btc():
    result = marketAPI.get_history_candlesticks('BTC-USDT', bar=period)['data']
    print(result)
    print("涨跌幅")
    close = result[0][4]
    return_0 = (float(result[0][4]) / float(result[0][1]) - 1) * 100
    return_1 = (float(result[1][4]) / float(result[2][1]) - 1) * 100
    return_x = round(abs(return_0) / abs(return_1), 2)
    return_now = round(return_0, 2)
    print(return_0)
    print(return_1)
    print(return_x)
    n = round(abs(return_0), 2)
    if n > 0.11:
        if return_0 > 0:
            msg = f'{emoji_dict["laugh"]} {title}单线涨幅超一个点 涨跌幅:{return_now} 当前价:{close}'
        else:
            msg = f'{emoji_dict["angry"]} {title}单线跌幅超一个点 涨跌幅:{return_now} 当前价:{close}'
        send_message(msg, chat_id=chat_id)

    if return_x > 4.86:
        if return_0 > 0:
            msg = f'{emoji_dict["kiss"]} {title}涨幅同比超5倍 涨跌幅:{return_now} 当前价:{close}'
        else:
            msg = f'{emoji_dict["fail"]} {title}跌幅同比超5倍 涨跌幅:{return_now} 当前价:{close}'
        send_message(msg, chat_id=chat_id)

    # 对比成交量
    print("成交量")
    volume_0 = round(float(result[0][5]) / float(result[1][5]), 2)
    volume_1 = round(float(result[0][5]) / float(result[2][5]), 2)
    volume_x = max(volume_0, volume_1)
    print(volume_0)
    print(volume_1)
    print(volume_x)
    if volume_x > 4.86:
        if return_0 > 0:
            msg = f'{emoji_dict["kiss_laugh"]} {title}此时成交量超7倍 +{volume_x} 涨跌幅:{return_now} 当前价:{close}'
        else:
            msg = f'{emoji_dict["han"]} {title}此时成交量超7倍 +{volume_x} 涨跌幅:{return_now} 当前价:{close}'
        send_message(msg, chat_id=chat_id)


if __name__ == '__main__':
    api_key = "ff633c9f-eeb1-4073-bfbc-de5a93af409c"
    secret_key = "B0C40F0CE489B41E13B05495110D978D"
    passphrase = "Jay@541430183"
    flag = '1'
    marketAPI = MarketAPI(api_key, secret_key, passphrase, False, flag)
    get_btc()
