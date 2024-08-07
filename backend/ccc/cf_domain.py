# -*- coding: utf-8 -*-
# author: itimor

import CloudFlare
import random


class CloudFlareApi:
    def __init__(self, cf, record_type, record_content, proxied):
        self.cf = cf
        self.record_type = record_type
        self.record_content = record_content
        self.proxied = proxied

    def list_zone(self):
        name = 'ends_with:com'
        page = 1
        per_page = 20
        status = 'active'
        params = {'page': page, 'per_page': per_page, 'name': name, 'status': status}
        zones = cf.zones.get(params=params)
        for i in zones:
            print(i['name'])

    def add_zone_record(self):
        for line in lines:
            d = line.split()
            zone = d[0]
            print(zone)
            # 添加域名, 获取zone_id
            zone_info = self.cf.zones.post(data={'jump_start': False, 'name': zone})
            print("打印nameserver")
            ns_data = {"nameServers": zone_info['name_servers']}
            print(ns_data)
            # print("更新godaddy ns")
            # gd.update_domain(zone, **ns_data)

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

    def add_record(self):
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
                print("添加dns解析")
                dns_record_data = {'name': record_name, 'type': self.record_type, 'content': self.record_content,
                                   'proxied': self.proxied}
                print(zone_id)
                print(dns_record_data)
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
                                   'proxied': self.proxied, 'ttl': 600, }
                r = self.cf.zones.dns_records.put(zone_id, dns_record_id, data=dns_record_data)
                print(r)

    def delete_record(self):
        for line in lines:
            d = line.split()
            zone = d[0]
            print(zone)
            # 获取zone_id
            zone_info = self.cf.zones.get(params={'name': zone})
            zone_id = zone_info[0]['id']
            self.cf.zones.delete(zone_id)

    def add_random_record(self):
        e_list = ['z', 'y', 'x', 'w', 'v', 'u', 't', 's', 'r', 'q', 'p', 'o', 'n', 'm', 'l', 'k', 'j', 'i', 'h', 'g',
                  'f', 'e', 'd', 'c', 'b', 'a', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
        r_list = []
        for line in lines:
            d = line.split()
            zone = d[0]
            # 获取zone_id
            zone_info = self.cf.zones.get(params={'name': zone})
            zone_id = zone_info[0]['id']

            record_name = ''.join(random.sample(e_list, 5))
            r_list.append(f'{record_name}.{zone}')
            dns_record_data = {'name': record_name, 'type': self.record_type, 'content': self.record_content,
                                   'proxied': False}
            r = self.cf.zones.dns_records.post(zone_id, data=dns_record_data)
            print(f'{record_name}.{zone}')


if __name__ == '__main__':
    # godadd_ac = Account(api_key='h1UXtXE3kZb8_NmcVoHPRtygCfM8P9e27w1', api_secret='CyQACC2NyePptyLXT3asRc')
    # gd = Client(godadd_ac)
    # cf = CloudFlare.CloudFlare(email='leapkeji@gmail.com', key='c50dda35b1d4370a80610928b75eeeac6ded1')
    cf = CloudFlare.CloudFlare(email='mario755132@gmail.com', key='c68b7b980ea090fd803189d97152acd6618ff')
    record_type = 'A'
    record_content = '16.163.26.223'
    proxied = True
    with open("domains.txt", "r") as f:
        lines = f.readlines()
        c = CloudFlareApi(cf, record_type, record_content, proxied)
        # c.scan_zone()
        # c.add_zone_record()
        c.update_record()
        # c.delete_record()
        # c.list_zone()
        # c.add_record()
        # c.add_random_record()
