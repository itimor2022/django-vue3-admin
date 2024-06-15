# -*- coding: utf-8 -*-
# author: itimor

import random
import string


def gen_web(site, m):
    print("h5")
    for i in range(m):
        num = string.ascii_lowercase + string.digits
        hou = "".join(random.sample(num, 2))
        full_site = f'{site}{hou}.shop\t\tweb.{site}{hou}.shop'
        print(full_site)


def gen_landing(site, m):
    n = 31
    print("落地页")
    for i in range(n, n + m):
        full_site = f'{site}store{i}.shop\tlanding.{site}store{i}.shop'
        print(full_site)


if __name__ == '__main__':
    site = 'xczx'
    m = 10
    gen_web(site, m)
    gen_landing(site, m)
