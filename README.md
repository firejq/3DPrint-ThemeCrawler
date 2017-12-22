- [3DPrint Theme Crawler](#3dprint-theme-crawler)
  - [Requirement](#requirement)
  - [URLs Queue](#urls-queue)
  - [Initial Seeds](#initial-seeds)
  - [URL Handler](#url-handler)
  - [TODO](#todo)
  - [Refer Links](#refer-links)
  - [Lisence](#lisence)

# 3DPrint Theme Crawler

面向 3D 打印的主题爬虫。

## Requirement

- [Python 3.6.2](https://docs.python.org/3/)
- [letiantian / TextRank4ZH](https://github.com/letiantian/TextRank4ZH)
- [leonsim / simhash](https://github.com/leonsim/simhash)
- [gensim](https://github.com/RaRe-Technologies/gensim)
- [fxsjy / jieba](https://github.com/fxsjy/jieba)

<!-- ## Work Flow

![image](http://otaivnlxc.bkt.clouddn.com/image/2017/12/image-1513270767647-d29yay1mbG93LnBuZw==.png) -->

## URLs Queue

Redis 中以 set 结构存储着一系列 URL 队列：

- 待访问 URL 队列
- 已访问 URL 队列
- 访问出错 URL 队列

## Initial Seeds

根据选定的关键词，得到初始种子。// TODO

## URL Handler

URL Handler 用于处理一个从待访问队列中获取的 url，处理流程如下：

<!-- 1. URL 判重：使用 Bloom Filter 根据 Redis 中的已访问队列和访问出错队列进行 URL 判重：
    - 若重复：退出 handler。
    - 若不重复：将 URL 与其 md5 签名组成键值对存入 Redis 的已访问队列，然后访问该 URL。 -->

1. URL 判重：将 URL 加入 Redis 中的 urls_already_visited 队列，利用 SET 结构进行判重：
    - 若重复：退出 handler。
    - 若不重复：进入下一流程。   

1. 访问链接：
    - 若访问出错：将 URL 放入出错队列。
    - 若访问正常：进入下一流程。 

1. 网页正文内容提取：使用 url2io 进行正文提取，以
    ```
    {
        url: '...',
        date: '...',
        text: '...', 
        title: '...'
    }
    ```
    格式进入下一流程。

1. 正文文本内容判重：使用 SimHash 进行文本内容判重：TODO
   - 若重复：退出 handler。
   - 若不重复：进入下一流程。

1. 计算主题相关性：根据预定义的主题，使用 Latent Semantic Indexing（LSI）模型计算正文文本内容的主题相关度，并与预设阈值进行比较：
    - 若小于阈值：说明主题相关性较小，舍弃此 URL，退出 handler。
    - 若大于阈值：说明主题相关性较大，进入下一流程。

1. 提取链接：获取网页的 HTML，使用正则表达式提取其中的所有链接（包括外链和内链，其中内链若是相对地址，需要在当前网页的 URL 上添加相对链接的字段从而组成完整的 URL），并依次添加到 urls_to_visit 队列中，然后进行下一流程。

1. 文本摘要、关键词提取：使用 TextRank 对正文进行文本摘要，并提取关键词，将所有提取的信息以
    ```
    title:...
    url:...
    date:...
    关键词：...
    摘要：...
    正文：...
    ```
    格式，在 data 目录下以 txt 文件存储。

1. 退出 handler。

Handler 默认以多进程 & 多线程运行。

<!-- ## Data Analyzer

Data Analyzer 用于从保存的 TXT 文件中分析数据，统计词频，得到结果，以柱状图呈现。 -->

## config.ini

- `[redis]`: 定义 redis 连接的相关配置。 
    
    默认值：
    ```
    host=localhost
    port=6379
    db=0
    ```
 
- `[theme-relevance]`: 定义主题相关性的阈值（0 < threshold < 1）。默认值为 0.3。

## TODO

- 在待访问 URL 队列中，使用 PageRank 进行优先级排序，并且在 Redis 中用 zset 存储而不是 set
- 爬取页面的 URLs 时，要先进行去噪，如：对广告链接进行过滤

## Refer Links

http://www.jianshu.com/p/edf666d3995f

http://www.ruanyifeng.com/blog/2013/03/cosine_similarity.html

## Lisence

The 3DPrint Theme Crawler is under the [MIT](https://github.com/firejq/3DPrint-ThemeCrawler/blob/master/LICENSE) Lisence.