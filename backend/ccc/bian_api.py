from binance.um_futures import UMFutures
from operator import itemgetter
import requests
import time

period = '5m'
typ = 'USDT'
print("*" * 100)
t = int(time.time())
timeArray = time.localtime(t)
otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
print(otherStyleTime)


def send_message(msg, chat_id="-4591709428"):
    token1 = "7114302"
    token2 = "389:AAHaFEzUwXj7QC1A20qwi_tJGlkRtP6FOlg"
    url = f"https://api.telegram.org/bot{token1}{token2}/sendMessage?chat_id={chat_id}&text={msg}"
    r = requests.get(url)
    print(r)


def get_pairs():
    exclude_pair_list = ['USDCUSDT', 'BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'PEPEUSDT', 'DOGEUSDT', 'TONUSDT', 'XRPUSDT',
                         'BCHUSDT', 'LTCUSDT', 'SHIBUSDT', 'TONUSDT']
    url = f"https://www.okx.com/priapi/v5/rubik/web/public/up-down-rank?countryFilter=1&rank=0&zone=utc8&period={period}&type={typ}&t={t}"
    r = requests.get(url)
    c = r.json()['data']['data']
    c_list = []
    for i in c:
        p = i['instId'].replace('-', '')
        if p not in exclude_pair_list:
            c_list.append(p)
    print(c_list)
    return c_list[:20]


def main():
    pair_list = ['CATIUSDT']
    # pair_list = get_pairs()

    s_list = list()
    for index, pair in enumerate(pair_list):
        print(index)
        p = pair.split('USDT')[0]
        r1 = futures_client.long_short_account_ratio(pair, period)
        d1 = sorted(r1, key=itemgetter('timestamp'), reverse=True)
        print(p)

        if len(d1) > 0:
            r2 = futures_client.taker_long_short_ratio(pair, period, limit=50)
            r3 = list()
            for r in r2:
                r['sellVol'] = float(r['sellVol'])
                r['buyVol'] = float(r['buyVol'])
                r3.append(r)
            d2 = sorted(r3, key=itemgetter('timestamp'), reverse=True)
            print(d2)


if __name__ == '__main__':
    futures_client = UMFutures(key='5gYKudrzlzetWpR3i6dcbXqBN74dZ6SQvOJjWDCKrp3CGsSesmL4OgBPqPyg2754',
                               secret='MbvXMsuAxsjIQ9ZJLGK2RRVtfLcuwXuezatK6sROthX9lbGyiv2AdenE6oqOsdOc')
    # get_pairs()
    main()
