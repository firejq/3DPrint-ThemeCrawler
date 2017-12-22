# -*- coding: utf-8 -*-
# Author： firejq
# Created on 2017-12-15
from configparser import ConfigParser

import os
import redis


class RedisTool:
    """
    Redis 操作工具类

    Redis 中存储着四个 URL 队列，均以 SET 结构存储
    - 待过滤 URL 队列: urls_to_filter
    - 待访问 URL 队列: urls_to_visit
    - 已访问 URL 队列: urls_already_visited
    - 访问出错 URL 队列: urls_visited_error
    """
    cf = ConfigParser()
    host = 'localhost'
    port = 6379
    db = 0
    try:
        cf.read(os.getcwd() + os.path.sep + 'config.ini')
        host = cf.get('redis', 'host')
        port = cf.get('redis', 'port')
        db = cf.get('redis', 'db')
    except BaseException as e:
        print(e)
        exit(1)
    finally:
        __pool = redis.ConnectionPool(host=host, port=port, db=db)
        # __redis = redis.StrictRedis(connection_pool=__pool)

    def __init__(self):
        self.__redis = redis.StrictRedis(connection_pool=RedisTool.__pool)
        pass

    def add_url(self, name, value):
        """
        向指定 URLs 中添加一个新值，若存在则不添加
        :param name:
        :param value:
        :return:
        """
        if name:
            if isinstance(value, str) and value:
                return self.__redis.sadd(name, value)
            elif isinstance(value, list) and len(value):
                res = 1
                for url in value:
                    if self.__redis.sadd(name, url) == -1:
                        res = -1
                return res
        else:
            return -1

    def get_url(self, name):
        """
        在指定 URLs 中取出并删除一个值
        :param name:
        :return:
        """
        if name:
            return self.__redis.spop(name=name) or -1
        else:
            return -1

    def get_number(self, name):
        """
        获取指定 URLs 中的元素数量
        :param name:
        :return:
        """
        return self.__redis.scard(name=name)


if __name__ == '__main__':
    # RedisTool().add_url('urls_to_filter', '')
    # print(RedisTool.get_url('urls_to_visit'))
    # print(RedisTool.get_number('urls_to_visit'))
    pass
