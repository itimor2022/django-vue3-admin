# -*- coding: utf-8 -*-
# author: itimor

import CloudFlare
from godaddypy import Client, Account


class CloudFlareApi:
    def __init__(self, cf, record_type, record_content, proxied):
        self.cf = cf
        self.record_type = record_type
        self.record_content = record_content
        self.proxied = proxied

    def scan_zone(self):
        for line in lines:
            d = line.split()
            zone = d[0]
            print(zone)
            # 获取zone_id
            zone_info = self.cf.zones.get(params={'name': zone})
            print(zone_info)

    def add_record(self):
        for line in lines:
            d = line.split()
            zone = d[0]
            print(zone)
            # 添加域名, 获取zone_id
            zone_info = self.cf.zones.post(data={'jump_start': False, 'name': zone})
            print("打印nameserver")
            ns_data = {"nameServers": zone_info['name_servers']}
            print(ns_data)
            print("更新godaddy ns")
            gd.update_domain(zone, **ns_data)

            zone_id = zone_info['id']

            # zone_info = self.cf.zones.get(params={'name': zone})
            # zone_id = zone_info[0]['id']

            # 设置ssl加密模式为灵活  off|flexible|full|strict 关闭|灵活|完全|完全（严格）
            print("设置ssl加密模式为灵活")
            self.cf.zones.settings.ssl.patch(zone_id, data={'value': 'flexible'})
            print("始终使用 HTTPS")
            self.cf.zones.settings.always_use_https.patch(zone_id, data={'value': 'on'})
            for i in range(1, len(d)):
                record_name = d[i]
                print(record_name)
                print("添加dns解析")
                dns_record_data = {'name': record_name, 'type': self.record_type, 'content': self.record_content,
                                   'proxied': self.proxied}
                r = self.cf.zones.dns_records.post(zone_id, data=dns_record_data)
                print(r)

    def update_record(self):
        for line in lines:
            d = line.split()
            zone = d[0]
            print(zone)
            # 获取zone_id
            zone_info = self.cf.zones.get(params={'name': zone})
            zone_id = zone_info[0]['id']
            for i in range(1, len(d)):
                record_name = d[i]
                print(record_name)
                print("更新dns解析")
                dns_record_params = {'name': record_name, 'type': self.record_type}
                dns_record = self.cf.zones.dns_records.get(zone_id, params=dns_record_params)
                print(dns_record)
                dns_record_id = dns_record[0]['id']
                dns_record_data = {'name': record_name, 'type': self.record_type, 'content': self.record_content,
                                   'proxied': self.proxied}
                r = self.cf.zones.dns_records.put(zone_id, dns_record_id, data=dns_record_data)
                print(r)


if __name__ == '__main__':
    godadd_ac = Account(api_key='gHzap6zE4keX_2NaopMBRt4JRKcczEUbqDw', api_secret='VppHYw5ALkdtzW9XaPb6Ls')
    gd = Client(godadd_ac)
    # cf = CloudFlare.CloudFlare(email='leapkeji@gmail.com', key='c50dda35b1d4370a80610928b75eeeac6ded1')
    cf = CloudFlare.CloudFlare(email='mario755132@gmail.com', key='c68b7b980ea090fd803189d97152acd6618ff')
    record_type = 'A'
    record_content = '16.163.42.83'
    proxied = True
    with open("domains.txt", "r") as f:
        lines = f.readlines()
        c = CloudFlareApi(cf, record_type, record_content, proxied)
        # c.scan_zone()
        c.add_record()
        # c.update_record()
