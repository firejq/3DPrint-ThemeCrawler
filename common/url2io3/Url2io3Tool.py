# -*- coding: utf-8 -*-
# Author： firejq
# Created on 2017-12-15
from common.url2io3 import url2io3


class Url2io3Tool:
    """
    url2io3 sdk 操作工具类
    """

    __token = '_d4qT6VDQcK7P9aKSQIGng'
    __api = url2io3.API(__token)

    def __init__(self, url):
        self.url = url

    def get_main_text(self):
        return Url2io3Tool.__api.article(url=self.url, fields=['text'])

    def get_main_html(self):
        return Url2io3Tool.__api.article(url=self.url)


if __name__ == '__main__':
    Url2io3Tool()
