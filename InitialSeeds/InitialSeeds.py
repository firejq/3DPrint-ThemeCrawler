# -*- coding: utf-8 -*-
# Author： firejq
# Created on 2017-12-15
from common.redis_tool.RedisTool import RedisTool


class InitialSeeds:
    """初始种子:
    初始化四个 URL 队列：
        - 待过滤 URL 队列: urls_to_filter
        - 待访问 URL 队列: urls_to_visit
        - 已访问 URL 队列: urls_already_visited
        - 访问出错 URL 队列: urls_visited_error
    并将初始 URL 存入待访问 URL 队列
    """

    def __init__(self, initial_urls=None):
        """
        将初始 URL 存入待访问 URL 队列，若传入参数为空则使用默认初始 URLs
        :param initial_urls:
        """
        if RedisTool().get_number('urls_to_visit') == 0:
            initial_urls = initial_urls or [
                # 3D 打印案例
                'http://www.3ddayin.net/3ddayinanli/',

                # 3D 打印应用案例
                'http://cn.world3dassociation.com/anli/',

                # 3D 打印应用
                'http://www.i3dpworld.com/application',

                # 3D 打印技术文章
                'http://www.3dfocus.com/news/list-17.html',

                # 俄罗斯推出首个3D打印的卫星
                'http://3dprint.ofweek.com/2017-08'
                '/ART-132107-8200-30163283.html',

                # 东京大学3D打印人形机器人可以出汗，做俯卧撑和打羽毛球
                'http://www.nanjixiong.com/thread-125041-1-1.html',

                'http://www.china3dprint.com/'
                'news/27935.html',  # 华人团队研发3D打印不锈钢获突破
            ]
            for url in initial_urls:
                RedisTool().add_url('urls_to_visit', url)

            # RedisTool().get_url('urls_to_filter')
            # RedisTool().add_url('urls_already_visited', ' ')
            # RedisTool().add_url('urls_visited_error', ' ')
            print('首次运行...初始化完成')
        else:
            print('非首次运行，不再初始化')


if __name__ == '__main__':
    InitialSeeds()
