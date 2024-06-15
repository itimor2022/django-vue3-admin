# -*- coding: utf-8 -*-
# author: itimor

from requests_toolbelt import MultipartEncoder
import requests

domain_file = "domain.txt"

"""
websiteId 15 live.yangguangxueyuan01.shop
websiteId 16 live.yangguangxueyuan02.shop
websiteId 17 live.yangguangxueyuan03.shop
websiteId 18 live.yangguangxueyuan04.shop
websiteId 19 live.yangguangxueyuan05.shop
websiteId 20 live.yangguangxueyuan06.shop
websiteId 21 live.yangguangxueyuan07.shop
websiteId 22 live.yangguangxueyuan08.shop
websiteId 23 live.yangguangxueyuan09.shop
websiteId 24 live.yangguangxueyuan10.shop
"""

# room_list = ['1002', '1003', '1005', '1008']
# websiteId_list = [
#     {"SiteName": "live.yangguangxueyuan06.shop", "websiteId": "20"},
#     {"SiteName": "live.yangguangxueyuan07.shop", "websiteId": "21"},
#     {"SiteName": "live.yangguangxueyuan08.shop", "websiteId": "22"},
#     {"SiteName": "live.yangguangxueyuan09.shop", "websiteId": "23"},
#     {"SiteName": "live.yangguangxueyuan10.shop", "websiteId": "24"},
# ]
room_list = ['1004', '1006', '1007', '1009', '1010', '1011']
websiteId_list = [
    {"SiteName": "live.yangguangxueyuan01.shop", "websiteId": "15"},
    {"SiteName": "live.yangguangxueyuan02.shop", "websiteId": "16"},
    {"SiteName": "live.yangguangxueyuan03.shop", "websiteId": "17"},
    {"SiteName": "live.yangguangxueyuan04.shop", "websiteId": "18"},
    {"SiteName": "live.yangguangxueyuan05.shop", "websiteId": "19"},
]

url = "http://api.7x7by.cfd:55520/api/getShortLink?DomainId=22"

with open(domain_file, 'w') as fn:
    n = 10
    for room in room_list:
        print(f"{room}房间:")
        fn.write(f"{room}房间:")
        fn.write("\n")
        for i in websiteId_list:
            data = MultipartEncoder(
                fields={
                    "oldLink": f":55520/?room={room}",
                    "SiteName": i["SiteName"],
                    "short_id": "5",
                    "websiteId": i["websiteId"],
                    "pc": "1",
                    "wechat": "2"
                }
            )
            headers = {
                'Content-Type': data.content_type
            }
            r = requests.post(url, data=data, headers=headers)
            f_data = f'{r.text}'
            print(f_data)
            fn.write(f_data)
            fn.write("\n")

print(f"域名文件已生成，请打开{domain_file}查看")
