# -*- coding: utf-8 -*-
# Author： firejq
# Created on 2017-12-15
import jieba.posseg as pseg
import codecs
import os
from gensim import corpora, models, similarities


class ThemeRelevance:
    """主题相关性计算器
    将传入的文本，根据预定义的query主题，使用Latent Semantic Indexing（LSI）模型计算页面的主题相关度并返回该相关度
    """

    def __init__(self, content_text=''):
        """初始化传入文本
        :param content_text:
        """
        self.__content_text = content_text

    def theme_relevance(self):
        """主题相关性计算
        使用Latent Semantic Indexing（LSI）模型计算页面的主题相关度：
        - 若结果小于阈值，则抛弃此链接；
        - 若结果大于阈值，则进入下一流程。
        :return:
        """
        # 项目根目录
        root_path = os.getcwd()

        def tokenization(article_text, argv_type):
            """
            对一篇文章分词、去停用词
            :param article_text:
            :param argv_type:
            :return:
            """
            # 构建停用词表
            stop_words = root_path \
                + '/common/theme_relevance/res/stop_words.txt'
            stopwords = codecs.open(stop_words, 'r',
                                    encoding='utf8').readlines()
            stopwords = [w.strip() for w in stopwords]
            # print(stopwords)
            # 停用词性 [标点符号、连词、助词、副词、介词、时语素、‘的’、数词、方位词、代词]
            stop_flag = ['x', 'c', 'u', 'd', 'p', 't', 'uj', 'm', 'f', 'r']
            result = []
            words = ''

            if argv_type == 'filename':
                with open(article_text, 'r', encoding='utf8') as f:
                    text = f.read()
                    words = pseg.cut(text)
            elif argv_type == 'text':
                words = pseg.cut(article_text)

            for word, flag in words:
                if flag not in stop_flag and word not in stopwords:
                    result.append(word)
            return result

        filenames = [
            root_path + '/common/theme_relevance/res/1.txt',
            root_path + '/common/theme_relevance/res/2.txt',
            root_path + '/common/theme_relevance/res/3.txt',
        ]
        corpus = []
        for each in filenames:
            corpus.append(tokenization(each, 'filename'))
        corpus.append(tokenization(self.__content_text, 'text'))
        # print(len(corpus))
        dictionary = corpora.Dictionary(corpus)
        # print(dictionary)
        doc_vectors = [dictionary.doc2bow(aricle_text)
                       for aricle_text in corpus]
        tfidf = models.TfidfModel(doc_vectors)
        tfidf_vectors = tfidf[doc_vectors]

        # 构建一个query文本
        query = tokenization(root_path +
                             '/common/theme_relevance/res/query.txt',
                             'filename')
        query_bow = dictionary.doc2bow(query)

        # 构建LSI模型，设置主题数为2
        lsi = models.LsiModel(tfidf_vectors, id2word=dictionary, num_topics=2)
        lsi_vector = lsi[tfidf_vectors]
        query_lsi = lsi[query_bow]
        # 用LSI模型计算相似度
        index = similarities.MatrixSimilarity(lsi_vector)
        sims = index[query_lsi]
        return list(enumerate(sims))[-1]
