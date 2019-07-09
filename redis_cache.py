# *===================================*
# -*- coding: utf-8 -*-
# * Time : 2019-07-09 12:08
# * Author : zhangsf
# *===================================*
# !/usr/bin/env python
# -*- coding:utf-8 -*-


import configparser
import sys
import mysql.connector
import redis

if __name__ == '__main__':
    pool = redis.ConnectionPool(host='127.0.0.1', port=6379, db=0)
    r = redis.Redis(connection_pool=pool)
    # r.expire('tb_signin_rank:id:signin_num', 20)

    config = configparser.ConfigParser()

    # 从配置文件中读取数据库服务器IP、域名，端口
    config.read('./dbconfig.conf')
    host = config['TESTDB']['host']
    port = config['TESTDB']['port']
    user = config['TESTDB']['user']
    passwd = config['TESTDB']['passwd']
    db_name = config['TESTDB']['db']
    charset = config['TESTDB']['charset']

    try:
        dbconn = mysql.connector.connect(host=host, port=port, user=user, password=passwd, database=db_name,
                                         charset=charset)
    except Exception as e:
        print('初始化数据连接失败：%s' % e)
        sys.exit()

    # 执行签到
    try:
        db_cursor = dbconn.cursor()
        for id in range(1, 6):
            db_cursor.execute(
                'UPDATE tb_signin_rank SET signin_num = signin_num + 1, signin_time = NOW(), gold_coin = gold_coin + (1 + RAND()*9) WHERE id = %s',
                (id,))
            db_cursor.execute('commit')
        # 更新缓存
        r.zincrby("tb_signin_rank:id:signin_num", id, 1)
    except Exception as e:
        print('执行数据库更新操作失败：%s' % e)
        db_cursor.execute('rollback')
        db_cursor.close()
        exit()

    # 展示用户签到次数
    for id in range(1, 6):
        result = r.zscore('tb_signin_rank:id:signin_num', id)
        if not result:  # 不存在缓存,从数据库读取
            print('----从数据库读取用户签到次数----')
            try:
                db_cursor = dbconn.cursor()
                db_cursor.execute('SELECT signin_num FROM tb_signin_rank WHERE id = %s', (id,))
                result = db_cursor.fetchone()[0]
                # 更新到缓存
                r.zadd('tb_signin_rank:id:signin_num', id, result)
            except Exception as e:
                print('执行数据库查询操作失败：%s' % e)
                db_cursor.close()
        else:  # 存在缓存，从缓存读取
            print('----从缓存读取用户签到次数----')
            result = int(result)

        print('sigin_num of user[id=%s]: %s' % (id, result))

    # 展示签到排行榜
    result = r.zrevrange('tb_signin_rank:id:signin_num', 0, 10)
    print('签到排行榜：', result)