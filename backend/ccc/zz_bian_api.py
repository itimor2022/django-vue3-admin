from binance.um_futures import UMFutures
from operator import itemgetter
import requests
import time

period = '5m'
typ = 'USDT'
print("*"*140)
t = int(time.time())
timeArray = time.localtime(t)
otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
print(otherStyleTime)

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
    return c_list[:10]


def main():
    #pair_list = ['ICPUSDT']
    pair_list = get_pairs()
    type_b = '做多'
    type_s = '做空'

    h = list()
    for index, pair in enumerate(pair_list):
        k = dict()
        m = 2
        n = 5
        print(index)
        p = pair.split('USDT')[0]
        r1 = futures_client.long_short_account_ratio(pair, period)
        d1 = sorted(r1, key=itemgetter('timestamp'), reverse=True)

        print(p)
        k['pair'] = p
        k['t'] = 0.0
        k['s'] = 0.0
        if len(d1) > 0:

            if float(d1[0]['longShortRatio']) > 1:
                t1 = float(d1[0]['longAccount']) / float(d1[1]['shortAccount'])
                t2 = float(d1[0]['longAccount']) / float(d1[2]['longAccount'])
                if t1 > m or t2 > m:
                    print(t1)
                    print(t2)
                    print(f'多倍{type_b}')
            else:
                t1 = float(d1[0]['shortAccount']) / float(d1[1]['longAccount'])
                t2 = float(d1[0]['shortAccount']) / float(d1[2]['longAccount'])
                if t1 > m or t2 > m:
                    print(t1)
                    print(t2)
                    print(f'多倍{type_s}')
            k['t'] = max(t1, t2)

            r2 = futures_client.taker_long_short_ratio(pair, period, limit=50)
            r3 = list()
            for r in r2:
                r['sellVol'] = float(r['sellVol'])
                r['buyVol'] = float(r['buyVol'])
                r3.append(r)
            d2 = sorted(r3, key=itemgetter('timestamp'), reverse=True)
            if float(d2[0]['buySellRatio']) > 1:
                d1 = sorted(r3, key=itemgetter('buyVol'), reverse=True)
                s1 = d2[0]['buyVol'] / d2[1]['buyVol']
                s2 = d2[0]['buyVol'] / d2[2]['buyVol']
                if s1 > n or s2 > n and d1[0] is d2[0]:
                    print(s1)
                    print(s2)
                    print(f'多倍{type_b}')
            else:
                d1 = sorted(r3, key=itemgetter('sellVol'), reverse=True)
                s1 = d2[0]['sellVol'] / d2[1]['sellVol']
                s2 = d2[0]['sellVol'] / d2[2]['sellVol']
                if s1 > n or s2 > n and d1[0] is d2[0]:
                    print(s1)
                    print(s2)
                    print(f'多倍{type_s}')
            k['s'] = max(s1, s2)

        h.append(dict(k))
    print(h)
    print("***************** 主动买卖量比 *****************")
    ss = sorted(h, key=itemgetter('s'), reverse=True)
    print(ss)


if __name__ == '__main__':
    futures_client = UMFutures(key='5gYKudrzlzetWpR3i6dcbXqBN74dZ6SQvOJjWDCKrp3CGsSesmL4OgBPqPyg2754',
                               secret='MbvXMsuAxsjIQ9ZJLGK2RRVtfLcuwXuezatK6sROthX9lbGyiv2AdenE6oqOsdOc')
    # get_pairs()
    main()
