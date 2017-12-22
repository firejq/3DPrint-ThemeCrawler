# -*- coding: utf-8 -*-
# Author： firejq
# Created on 2017-12-15
import hashlib
import os
from configparser import ConfigParser

import requests
import time
from bs4 import BeautifulSoup
from textrank4zh import TextRank4Keyword, TextRank4Sentence

from common.redis_tool.RedisTool import RedisTool
from common.theme_relevance.ThemeRelevance import ThemeRelevance
from common.url2io3.Url2io3Tool import Url2io3Tool


class UrlHandler:
    """URL 处理类
    """

    def __init__(self, url):
        self.cur_url = url

    def begin_handle(self):
        """对传入的 url 进行一系列操作
        :return:
        """
        print('【' + self.cur_url + '】开始处理')

        if self.__url_duplicate_judgment() != 1:
            print('【' + self.cur_url + '】已访问过，不再访问')
            return -1
        if self.__url_open() == -1:
            print('【' + self.cur_url + '】访问出错，已加入出错队列')
            return -1
        if self.__main_content_get() == -1:
            print('【' + self.cur_url + '】获取正文出错，舍弃')
            return -1
        if self.__theme_relevance() == -1:
            print('【' + self.cur_url + '】的主题相关度小于阈值，舍弃')
            return -1

        self.__url_crawler()
        self.__main_content_duplicate_judgment()
        self.__data_save()
        # 按照预定流程处理完成，返回1
        return 1

    def __url_duplicate_judgment(self):
        """检测 url 是否在已访问队列中存在：
        - 若已存在：返回非 1 值。
        - 若不存在：将 URL 存入 Redis 的已访问队列，返回 1
        :return:
        """
        return RedisTool().add_url('urls_already_visited',
                                   self.cur_url)

    def __url_open(self):
        """访问链接：
        - 若访问出错：将 URL 放入出错队列。
        - 若访问正常：进入下一流程。
        :return:
        """
        try:
            self.__request = requests.get(self.cur_url)
        except Exception as e:
            print(e)
            return -1
        if self.__request.status_code != 200:
            RedisTool().add_url('urls_visited_error', self.cur_url)
            return -1
        else:
            self.__soup = BeautifulSoup(self.__request.text,
                                        'lxml')
            return 1

    def __url_crawler(self):
        """提取链接：使用正则表达式提取其中的所有链接
        （包括外链和内链，其中内链若是相对地址，需要在当前网页的 URL 上添加相对链接的字段从而组成完整的 URL），
        存放至 urls_to_visit 队列，然后进行下一流程
        :return:
        """
        links = [a.get('href') for a in self.__soup.find_all('a')]

        domain = self.cur_url.split('?')[0]
        # 补充相对地址的链接
        for link in links:
            if isinstance(link, str) \
                    and len(link) > 7 \
                    and link[0:4] == 'http':
                continue
            if isinstance(link, str) \
                    and len(link) > 0 \
                    and link[0] == '/' \
                    and '.' not in link:
                links[links.index(link)] = domain + link[1:]
                continue
            links[links.index(link)] = ''
        while '' in links:
            links.remove('')

        # print(links)
        RedisTool().add_url('urls_to_visit', links)

    def __main_content_get(self):
        """网页正文内容提取：使用 url2io 进行正文提取
        :return:
        """
        # print(self.cur_url)
        self.__main_content = Url2io3Tool(self.cur_url).get_main_text()
        # print(self.__main_content)
        if self.__main_content.get('error') is not None:
            return -1
        else:
            return 1

    def __theme_relevance(self):
        """计算主题相关度，小于阈值则抛弃此URL
        :return:
        """
        # print(self.__main_content.get('text'))
        theme_relevance = \
            ThemeRelevance(self.__main_content.get('text')).theme_relevance()
        # print(theme_relevance)

        # 定义主题相关度阈值，默认值为 0.3
        threshold = 0.3
        # 从配置文件读取阈值
        cf = ConfigParser()
        try:
            cf.read(os.getcwd() + os.path.sep + 'config.ini')
            threshold = float(cf.get('theme-relevance', 'threshold'))
        except BaseException as e:
            print(e)
            pass

        if ('3D打印' in self.__main_content.get('title')
            or '3D 打印' in self.__main_content.get('title')) \
                and theme_relevance[1] > threshold:
            return 1
        else:
            return -1

    def __main_content_duplicate_judgment(self):
        """正文文本内容判重：使用 SimHash 进行文本内容判重：
        - 若重复：退出 handler。
        - 若不重复：进入下一流程。
        :return:
        """
        # TODO
        # print(self.__main_content.content)
        pass

    def __data_save(self):
        """文本摘要、关键词提取：
        使用 TextRank 对正文进行文本摘要，并提取关键词，在本地磁盘以 txt 文件存储
        :return:
        """
        # print(self.__main_content)
        data_content = ''
        data_content += '============= URL：=============\n' \
                        + self.__main_content.get('url') + '\n'
        data_content += '\n============= Date：=============\n' \
                        + str(self.__main_content.get('date')) + '\n'
        data_content += '\n============= Title：=============\n' \
                        + self.__main_content.get('title') + '\n'

        tr4w = TextRank4Keyword()
        tr4w.analyze(text=self.__main_content.get('text'),
                     lower=True,
                     window=2)

        data_content += '\n============= 关键词：=============\n'
        for item in tr4w.get_keywords(20, word_min_len=1):
            data_content += item.word + ' ' + str(item.weight) + '\n'

        data_content += '\n============= 关键短语：=============\n'
        for phrase in tr4w.get_keyphrases(keywords_num=20,
                                          min_occur_num=2):
            data_content += phrase + '\n'

        tr4s = TextRank4Sentence()
        tr4s.analyze(text=self.__main_content.get('text'),
                     lower=True,
                     source='all_filters')
        data_content += '\n============= 摘要：=============\n'
        for item in tr4s.get_key_sentences(num=3):
            data_content += '【index】：' + str(item.index) \
                + '\n' \
                + '【weight】：' + str(item.weight) \
                + '\n' \
                + '【sentence】：' + item.sentence \
                + '\n\n'

        data_content += '\n============= 正文：=============\n' \
                        + self.__main_content.get('text')

        path = os.getcwd() + os.path.sep + 'data' + os.path.sep
        data_filename = time.strftime(
            '%Y%m%d%H%M%S_',
            time.localtime(time.time())
        ) + hashlib.sha1(bytes(self.cur_url,
                               encoding='utf8')
                         ).hexdigest()[0:7] + '.txt'
        if not os.path.exists(path):
            os.mkdir(path)
        with open(path + data_filename,
                  'w',
                  encoding='utf8') as f:
            f.write(data_content)
