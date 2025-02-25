# -*- coding: utf-8 -*-

import requests
import json
import time
import datetime
import hmac
import base64
import pytz

'''para
'''
t = int(time.time())
period = '5m'
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


def get_coin():
    period = '5m'
    # 热门榜
    url = f"https://www.okx.com/priapi/v5/rubik/web/public/hot-rank?countryFilter=1&rank=0&zone=utc8&period={period}&type=USDT&t={t}"
    # 成交额
    # url = f"https://www.okx.com/priapi/v5/rubik/web/public/turn-over-rank?countryFilter=1&rank=0&zone=utc8&period={period}&type=USDT&t={t}"
    # pair_list = ['CATI-USDT']
    r = requests.get(url)
    c = r.json()['data']['data'][:15]
    return c


def get_coin_data(coin):
    title = f'🏆{coin}🏆\n'
    result = marketAPI.get_history_candlesticks(coin, bar=period)['data']
    print(result)
    print("涨跌幅")
    close = result[0][4]
    time_stamp = int(result[0][0]) / 1000
    x = format_time(time_stamp, tz=7)
    y = format_time(time_stamp, tz=0)
    print('本地时间：', x)
    print('UTC时间：', y)
    # 成交量
    volume_list = [v[6] for v in result]
    v1 = volume_list[0]
    vmax = max(volume_list[:50])
    if v1 == vmax:
        msg = f'🈵🈯成交量史前巨大 {title}<strike>🚦🍄当前价:{close} \n本地时间:{x} UTC时间:{y}'
        send_message(msg, chat_id=chat_id)
    return_0 = (float(result[0][4]) / float(result[0][1]) - 1) * 100
    return_1 = (float(result[1][4]) / float(result[1][1]) - 1) * 100
    return_2 = (float(result[2][4]) / float(result[2][1]) - 1) * 100
    return_3 = (float(result[3][4]) / float(result[3][1]) - 1) * 100
    return_4 = (float(result[4][4]) / float(result[4][1]) - 1) * 100
    return_now = round(return_0, 2)
    return_list = [return_0, return_1, return_2, return_3, return_4]
    positive_count = len([num for num in return_list if num > 0])
    negative_count = len([num for num in return_list if num < 0])
    print(return_list)
    print(positive_count)
    print(negative_count)
    if negative_count >= 4:
        msg = f'📉5连续阴 {title} 🚦涨跌幅:{return_now} 🍄当前价:{close} \n本地时间:{x} UTC时间:{y}'
        send_message(msg, chat_id=chat_id)
    if positive_count >= 4:
        msg = f'📈5连阳 {title} 🚦涨跌幅:{return_now} 🍄当前价:{close} \n本地时间:{x} UTC时间:{y}'
        send_message(msg, chat_id=chat_id)

    if return_0 > 0:
        shang_line_0 = result[0][2] - result[0][4] + 0.000001
        shang_line_1 = result[1][2] - result[1][4] + 0.000001
    else:
        shang_line_0 = result[0][2] - result[0][1] + 0.000001
        shang_line_1 = result[1][2] - result[1][1] + 0.000001
    shang_line_x = shang_line_0 / shang_line_1

    if shang_line_x > 5:
        msg = f'👺上影线巨大 {title} 🚦涨跌幅:{return_now} 🍄当前价:{close} \n本地时间:{x} UTC时间:{y}'
        send_message(msg, chat_id=chat_id)

    s = 0
    b = 0
    for i in return_list:
        if i <= 0:
            s += i
        else:
            b += i
    if abs(s) / b > 5:
        if return_0 > 0:
            msg = f'✳️大阳柱 {title}<strike>🚦涨幅同比超倍</strike> <i>☘️涨跌幅:{return_now}</i> 🍄当前价:{close} \n本地时间:{x} UTC时间:{y}'
        else:
            msg = f'🚫大阴柱 {title}<strike>🚦跌幅同比超倍</strike> <i>☘️涨跌幅:{return_now}</i> 🍄当前价:{close} \n本地时间:{x} UTC时间:{y}'
        send_message(msg, chat_id=chat_id)

    # 对比成交量
    print("成交量")
    volume_0 = round(float(result[0][5]) / float(result[1][5]), 2)
    volume_1 = round(float(result[0][5]) / float(result[2][5]), 2)
    volume_x = max(volume_0, volume_1)
    print(volume_0)
    print(volume_1)
    if volume_x > 5:
        if return_0 > 0:
            msg = f'💹成交量 {title}<strike>🚦成交量超倍</strike> {volume_x} <i>☘️涨跌幅:{return_now}</i> 🍄当前价:{close} \n本地时间:{x} UTC时间:{y}'
        else:
            msg = f'💢成交量 {title}<strike>🚦成交量超倍</strike> {volume_x} <i>☘️涨跌幅:{return_now}</i> 🍄当前价:{close} \n本地时间:{x} UTC时间:{y}'
        send_message(msg, chat_id=chat_id)


if __name__ == '__main__':
    api_key = "ff633c9f-eeb1-4073-bfbc-de5a93af409c"
    secret_key = "B0C40F0CE489B41E13B05495110D978D"
    passphrase = "Jay@541430183"
    flag = '1'
    marketAPI = MarketAPI(api_key, secret_key, passphrase, False, flag)
    coin_list = get_coin()
    for i in coin_list:
        coin = i['instId']
        print(coin)
        get_coin_data(coin)
