from binance.um_futures import UMFutures
from operator import itemgetter
import requests
import time

period = '5m'
typ = 'USDT'


def get_pairs():
    exclude_pair_list = ['USDCUSDT', 'BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'PEPEUSDT', 'DOGEUSDT', 'TONUSDT', 'XRPUSDT',
                         'BCHUSDT', 'LTCUSDT', 'SHIBUSDT', 'TONUSDT']
    t = int(time.time())
    print(t)
    url = f"https://www.okx.com/priapi/v5/rubik/web/public/turn-over-rank?countryFilter=1&rank=0&period={period}&type={typ}&t={t}"
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
    # pair_list = ['PEPEUSDT']
    pair_list = get_pairs()
    type_b = '做多'
    type_s = '做空'

    s = {}
    t = {}
    for index, pair in enumerate(pair_list):
        m = 2
        n = 2
        print(index)
        p = pair.split('USDT')[0]
        print(p)
        r1 = futures_client.long_short_account_ratio(pair, period)
        d1 = sorted(r1, key=itemgetter('timestamp'), reverse=True)

        if len(d1) > 0:
            if float(d1[0]['longShortRatio']) > 1:
                t1 = float(d1[0]['longAccount']) / float(d1[1]['shortAccount'])
                t2 = float(d1[0]['longAccount']) / float(d1[2]['longAccount'])
                if t1 > m or t2 > m:
                    print(t1)
                    print(t2)
                    print(f'多倍{type_b}')
                t[p] = f'+{max(t1, t2)}'
            else:
                t1 = float(d1[0]['shortAccount']) / float(d1[1]['longAccount'])
                t2 = float(d1[0]['shortAccount']) / float(d1[2]['longAccount'])
                if t1 > m or t2 > m:
                    print(t1)
                    print(t2)
                    print(f'多倍{type_s}')
                t[p] = f'-{max(t1, t2)}'

            r2 = futures_client.taker_long_short_ratio(pair, period)
            d2 = sorted(r2, key=itemgetter('timestamp'), reverse=True)
            if float(d2[0]['buySellRatio']) > 1:
                s1 = float(d2[0]['buyVol']) / float(d2[1]['buyVol'])
                s2 = float(d2[0]['buyVol']) / float(d2[2]['buyVol'])
                if s1 > n or s2 > n:
                    print(s1)
                    print(s2)
                    print(f'多倍{type_b}')
                s[p] = f'+{max(s1, s2)}'
            else:
                s1 = float(d2[0]['sellVol']) / float(d2[1]['sellVol'])
                s2 = float(d2[0]['sellVol']) / float(d2[2]['sellVol'])
                if s1 > n or s2 > n:
                    print(s1)
                    print(s2)
                    print(f'多倍{type_s}')
                s[p] = f'-{max(s1, s2)}'

    print("***************** 多空持仓人数 *****************")
    print(t)
    tt = dict(sorted(t.items(), key=itemgetter(1), reverse=True))
    print(tt)

    print("***************** 主动买卖量比 *****************")
    print(s)
    ss = dict(sorted(s.items(), key=itemgetter(1), reverse=True))
    print(ss)


if __name__ == '__main__':
    futures_client = UMFutures(key='5gYKudrzlzetWpR3i6dcbXqBN74dZ6SQvOJjWDCKrp3CGsSesmL4OgBPqPyg2754',
                               secret='MbvXMsuAxsjIQ9ZJLGK2RRVtfLcuwXuezatK6sROthX9lbGyiv2AdenE6oqOsdOc')
    # get_pairs()
    main()
