# coding=utf-8
import requests
import json

file = open('2', 'r')
lines = file.readlines()
file.close()

headers = {
    "Content-type": "application/json"
}
url = 'http://172.31.17.145:5001/channel/subscriber_add'
for line in lines:
    print(line)
    data = {
        "channel_id": "0b3612d488264b27b953ec8506ef06df",
        "channel_type": 2,
        "reset": 0,
        "subscribers": [eval(line.strip()), ],
        "temp_subscriber": 0
    }
    d = json.dumps(data)
    print(d)
    r = requests.post(url, data=d, headers=headers)
    print(r.json())
