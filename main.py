# -*- coding: utf-8 -*-
# Author： firejq
# Created on 2017-12-14
import time

from multiprocessing import Process
from threading import Thread
from InitialSeeds.InitialSeeds import InitialSeeds
from common.redis_tool.RedisTool import RedisTool
from url_handler.UrlHandler import UrlHandler


def url_handle(process_number=4, thread_number=16):
    """爬取启动
    :param process_number: 进程数
    :param thread_number: 线程数
    :return:
    """
    # 多进程运行
    for process_number_i in range(process_number):
        process = Process(target=url_handle_process, args=(thread_number,))
        process.start()

    while RedisTool().get_number('urls_to_visit') > 0:
        time.sleep(5)
        continue

    print('URL 全部爬取完毕')
    exit(0)


def url_handle_process(thread_number):
    """单个进程调用
    :param thread_number: 线程数
    :return:
    """
    # 多线程运行
    for thread_number_i in range(thread_number):
        thread = Thread(target=url_handle_thread)
        thread.start()
        thread.join()


def url_handle_thread():
    """单个线程调用
    从待访问队列中提取 URL 并进行一系列处理
    :return:
    """
    while RedisTool().get_number('urls_to_visit') > 0:
        begin_time = time.time()

        url = RedisTool().get_url('urls_to_visit')
        # 若获取 URL 出现错误，则重新获取
        if url == -1:
            continue
        # 将字节码格式转换为字符串格式
        url = str(url, encoding='utf-8')
        if url == '-1':
            continue

        # 对 URL 进行处理，成功返回1，其它情况返回-1
        res = UrlHandler(url=url).begin_handle()

        if res == 1:
            print('【' + url + '】处理成功,',
                  '耗时【' + str(time.time() - begin_time) + '】秒')


if __name__ == '__main__':
    # 执行种子初始化
    InitialSeeds()
    # 启动爬取
    url_handle(process_number=6, thread_number=16)
