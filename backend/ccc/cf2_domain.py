# -*- coding: utf-8 -*-
# author: itimor

import CloudFlare
from godaddypy import Client, Account
from hashlib import md5


def encrypt_md5(s):
    # 创建md5对象
    new_md5 = md5()
    # 这里必须用encode()函数对字符串进行编码，不然会报 TypeError: Unicode-objects must be encoded before hashing
    new_md5.update(s.encode(encoding='utf-8'))
    # 加密
    return new_md5.hexdigest()


class CloudFlareApi:
    def __init__(self, cf):
        self.cf = cf

    def add_zone_ssl_record(self, record_type, record_content, proxied):
        for line in lines:
            d = line.split()
            zone = d[0]
            print(zone)
            # 添加域名, 获取zone_id
            zone_info = self.cf.zones.post(data={'jump_start': False, 'name': zone})
            print("打印nameserver")
            ns_data = {"nameServers": zone_info['name_servers']}
            print(ns_data)
            zone_id = zone_info['id']

            # 设置ssl加密模式为灵活  off|flexible|full|strict 关闭|灵活|完全|完全（严格）
            print("设置ssl加密模式为灵活")
            self.cf.zones.settings.ssl.patch(zone_id, data={'value': 'flexible'})
            print("始终使用 HTTPS")
            self.cf.zones.settings.always_use_https.patch(zone_id, data={'value': 'on'})
            for i in range(1, len(d)):
                record_name = d[i]
                print(record_name)
                print("添加dns解析")
                dns_record_data = {'name': record_name, 'type': record_type, 'content': record_content,
                                   'proxied': proxied}
                r = self.cf.zones.dns_records.post(zone_id, data=dns_record_data)
                print(r)

    def add_zone(self):
        for line in lines:
            d = line.split()
            zone = d[0]
            print(zone)
            # 添加域名, 获取zone_id
            zone_info = self.cf.zones.post(data={'jump_start': False, 'name': zone})
            print("打印nameserver")
            ns_data = {"nameServers": zone_info['name_servers']}
            print(ns_data)

    def update_zone_ssl(self, ssl='flexible', always_use_https='on'):
        for line in lines:
            d = line.split()
            zone = d[0]
            print(zone)
            zone_info = self.cf.zones.get(params={'name': zone})
            zone_id = zone_info[0]['id']

            # 设置ssl加密模式为灵活  off|flexible|full|strict 关闭|灵活|完全|完全（严格）
            print("设置ssl加密模式为灵活")
            self.cf.zones.settings.ssl.patch(zone_id, data={'value': ssl})
            print("始终使用 HTTPS")
            self.cf.zones.settings.always_use_https.patch(zone_id, data={'value': always_use_https})

    def add_record(self, record_type, record_name, record_content, proxied):
        print(record_name)
        for line in lines:
            d = line.split()
            zone = d[0]
            print(zone)
            # 获取zone_id
            zone_info = self.cf.zones.get(params={'name': zone})
            zone_id = zone_info[0]['id']
            print(zone_id)
            print("添加dns解析")
            dns_record_data = {'name': record_name, 'type': record_type, 'content': record_content,
                               'proxied': proxied}
            print(zone_id)
            print(dns_record_data)
            r = self.cf.zones.dns_records.post(zone_id, data=dns_record_data)
            print(r)

    def update_record(self, record_type='A', record_name="web", record_content="127.0.0.1", proxied=True):
        for line in lines:
            d = line.split()
            zone = d[0]
            print(zone)
            # 获取zone_id
            zone_info = self.cf.zones.get(params={'name': zone})
            zone_id = zone_info[0]['id']
            print(zone_id)
            print("更新dns解析")
            dns_record_params = {'name': f'{record_name}.{zone}', 'type': record_type}
            dns_record = self.cf.zones.dns_records.get(zone_id, params=dns_record_params)
            dns_record_id = dns_record[0]['id']
            dns_record_data = {'name': record_name, 'type': record_type, 'content': record_content,
                               'proxied': proxied, 'ttl': 600, }
            r = self.cf.zones.dns_records.put(zone_id, dns_record_id, data=dns_record_data)
            print(r)

    def get_records(self, zone):
        # 获取zone_id
        zone_info = self.cf.zones.get(params={'name': zone})
        zone_id = zone_info[0]['id']
        print(zone_id)
        print("更新dns解析")
        dns_record_params = {'name': f'{record_name}.{zone}', 'type': record_type}
        dns_record = self.cf.zones.dns_records.get(zone_id, params=dns_record_params)
        print(dns_record)

    def delete_record(self):
        for line in lines:
            d = line.split()
            zone = d[0]
            print(zone)
            # 获取zone_id
            zone_info = self.cf.zones.get(params={'name': zone})
            zone_id = zone_info[0]['id']
            self.cf.zones.delete(zone_id)


if __name__ == '__main__':
    godadd_ac = Account(api_key='h1UXtXE3kZb8_NmcVoHPRtygCfM8P9e27w1', api_secret='CyQACC2NyePptyLXT3asRc')
    gd = Client(godadd_ac)
    # cf = CloudFlare.CloudFlare(email='leapkeji@gmail.com', key='c50dda35b1d4370a80610928b75eeeac6ded1')
    # cf = CloudFlare.CloudFlare(email='mario755132@gmail.com', key='c68b7b980ea090fd803189d97152acd6618ff')
    cf = CloudFlare.CloudFlare(email='itimor2022@gmail.com', key='3863b58adc38744c3fc07a0444e85378811f3')
    record_type = 'A'
    record_name = 'zy'
    record_content = '18.166.41.3'
    proxied = True
    with open("domains.txt", "r") as f:
        lines = f.readlines()
        c = CloudFlareApi(cf)
        # c.add_zone_ssl_record(record_type, record_content, proxied)
        c.update_record(record_type=record_type, record_name=record_name, record_content=record_content, proxied=proxied)
        # c.get_records('eohpto.cyou')
        # c.delete_record()
        # c.add_record(record_type=record_type, record_name=record_name, record_content=record_content, proxied=proxied)
        # 设置ssl加密模式为灵活  off|flexible|full|strict 关闭|灵活|完全|完全（严格）
        # c.update_zone_ssl()
