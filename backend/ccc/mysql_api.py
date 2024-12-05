# -*- coding: utf-8 -*-
# author: itimor
# pip3 install PyMySQL

import random
import pymysql as MySQLdb


class MYSQL:
    def __init__(self, db):
        self.conn = MySQLdb.connect(
            host=db["host"],
            port=db["port"],
            user=db["user"],
            passwd=db["passwd"],
            db=db["db"],
            charset='utf8')
        self.cursor = self.conn.cursor()

    def insert(self, sql):
        self.cursor.execute(sql)
        self.conn.commit()
        return True

    def select(self, sql):
        self.cursor.execute(sql)
        alldata = self.cursor.fetchall()
        return alldata

    def update(self, sql):
        self.cursor.execute(sql)
        self.conn.commit()
        return True

    def close(self):
        self.cursor.close()
        self.conn.close()


def main():
    # 去除所以置顶视频
    cancel_top_sql = 'update yat_user_media set is_topping=0 where type=1;'
    myapi.update(cancel_top_sql)
    # 查询前50，随机取12条
    list_id_sql = 'select id from yat_user_media where type=1 order by id desc limit 50;'
    lst = myapi.select(list_id_sql)
    id_list = [i for (i,) in lst]
    video_id_list = random.sample(id_list, 10)
    # 查询20662
    s_id_sql = 'select id from yat_user_media where uid=20662;'
    s_lst = myapi.select(s_id_sql)
    s_id_list = [i for (i,) in s_lst]
    s_video_id_list = random.sample(s_id_list, 1) + video_id_list
    # 组合数据
    z_list = ', '.join(str(i) for i in s_video_id_list)
    print(z_list)
    # 把上面数据置顶
    set_top_sql = 'update yat_user_media set is_topping=1 where type=1 and id in (%s);' % z_list
    myapi.update(set_top_sql)


if __name__ == '__main__':
    # my_info = {
    #     "host": "16.163.200.186",
    #     "port": 23306,
    #     "user": "root",
    #     "passwd": "123456",
    #     "db": "rtx",
    # }
    my_info = {
        "host": "127.0.0.1",
        "port": 23306,
        "user": "rtx",
        "passwd": "32w52YjCfTBBSRhS",
        "db": "rtx",
    }
    myapi = MYSQL(my_info)
    main()
    myapi.close()
