from binance.um_futures import UMFutures
from operator import itemgetter
import requests
import time

period = '5m'
typ = 'USDT'


def get_pairs():
    t = int(time.time())
    url = f"https://www.okx.com/priapi/v5/rubik/web/public/turn-over-rank?countryFilter=1&rank=0&period={period}&type={typ}&t={t}"
    r = requests.get(url)
    c = r.json()['data']['data']
    c_list = []
    for i in c:
        p = i['instId'].replace('-', '')
        c_list.append(p)
    print(c_list)
    return c_list[:30]


def main():
    # pair_list = ['PEPEUSDT']
    pair_list = get_pairs()
    type_b = '做多'
    type_s = '做空'

    d = {}

    for index, pair in enumerate(pair_list):
        print(index)
        print(pair)
        r1 = futures_client.long_short_account_ratio(pair, period)
        d1 = sorted(r1, key=itemgetter('timestamp'), reverse=True)
        print(d1)
        if len(d1) > 0:
            if float(d1[0]['longShortRatio']) > 1:
                print(type_b)
            else:
                print(type_s)


            r2 = futures_client.taker_long_short_ratio(pair, period)
            d2 = sorted(r2, key=itemgetter('timestamp'), reverse=True)
            print(d2)
            n = 2
            if float(d2[0]['buySellRatio']) > 1:
                s2 = float(d2[0]['buyVol']) / float(d2[2]['buyVol'])
                s3 = float(d2[0]['buyVol']) / float(d2[3]['buyVol'])
                if s2 > n or s3 > n:
                    print(s2)
                    print(s3)
                    print(f'多倍{type_b}')
            else:
                s2 = float(d2[0]['sellVol']) / float(d2[2]['sellVol'])
                s3 = float(d2[0]['sellVol']) / float(d2[3]['sellVol'])
                if s2 > n or s3 > n:
                    print(s2)
                    print(s3)
                    print(f'多倍{type_s}')
            d[pair] = max(s2, s3)

    print(d)
    dd = sorted(d.items(), key=itemgetter(1), reverse=True)
    print(dd)



if __name__ == '__main__':
    futures_client = UMFutures(key='5gYKudrzlzetWpR3i6dcbXqBN74dZ6SQvOJjWDCKrp3CGsSesmL4OgBPqPyg2754',
                               secret='MbvXMsuAxsjIQ9ZJLGK2RRVtfLcuwXuezatK6sROthX9lbGyiv2AdenE6oqOsdOc')
    # get_pairs()
    main()
