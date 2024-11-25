# coding: utf-8
import pymysql
import random

try:
    # db = pymysql.connect(host="127.0.0.1", user="rtx", password="32w52YjCfTBBSRhS", database="rtx", port=23306)
    db = pymysql.connect(host="16.163.200.186", user="root", password="123456", database="rtx", port=23306)
    c = db.cursor()
    cancel_top_sql = 'update yat_user_media set is_topping=0;'
    c.execute(cancel_top_sql)
    list_id_sql = 'select id from yat_user_media order by id desc limit 50;'
    lst = c.execute(list_id_sql)
    video_id_list = random.sample(lst, 10)
    set_top_sql = 'update yat_user_media set is_topping=1 where in in %s;' % video_id_list
    c.execute(list_id_sql)
finally:
    # 关闭mysql连接
    c.close()
    db.commit()
    db.close()