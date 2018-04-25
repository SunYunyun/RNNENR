# -*- coding: utf-8 -*-
#! /usr/bin/python

import redis
import dict_data


# 获取文本中的最长电影名字，演员，角色字符串
# 自研电影名字库保存在 redis中
class GetFilmName:
    # 初始化redis连接参数
    # host_为ip，port_为端口，redis_index_为redis库号
    def __init__(self, host_, port_, redis_index_):
        self.redis_conn_pool = redis.ConnectionPool(host=host_, port=port_, db=redis_index_, decode_responses=True)
        self.r = redis.Redis(connection_pool=self.redis_conn_pool)

    # redis相应的库中提取文本中的字符串
    # text_str_为输入的文本， redis_key_为hashset中的键值
    def GetFilmName(self, text_str_, redis_key_):
        text_str_ = text_str_.strip()
        length = len(text_str_)
        # count = 1
        film_names = []

        for i in range(length):
            for j in range(length, i + 1, -1):
                temp_str = text_str_[i: j]
                # count += 1
                if self.r.hexists(redis_key_, temp_str)\
                        and not self.r.hexists("del_" + redis_key_, temp_str)\
                        and not self.r.hexists("common_words", temp_str):  # 该字符串不在删除列表中
                    film_names.append(temp_str)
        max_len_name_ = ''
        if len(film_names) > 0:
            max_len_name_ = sorted(film_names, key=lambda x: len(x))[-1]

        # 未获取到结果直接返回
        if '' == max_len_name_:
            return max_len_name_,False

        # 被提取的字符串替换为‘#’号
        replace_str = '#' * len(max_len_name_)
        temp_str_ = text_str_.replace(max_len_name_, replace_str)

        # 感官词判断
        sensory_words = dict_data.sensory_words
        contain_sensory_word_before_flag = False  # 提取出的字符串之前包含感官词
        for sensory_word in sensory_words:
            if sensory_word in temp_str_[: temp_str_.rfind(replace_str)]:
                contain_sensory_word_before_flag = True

        # 不包含感官词的情况
        ss = dict_data.video_tag
        flag = False
        for i in ss:
            if i in text_str_ and (not contain_sensory_word_before_flag):
                if len(max_len_name_ + i) * 1.0 / len(text_str_) < 0.6:  # 没有感官词，但有明确类型
                    max_len_name_ = ''
                flag = True

        if (not flag) and (not contain_sensory_word_before_flag) and len(max_len_name_) * 1.0 / len(
                text_str_) < 0.6:
            max_len_name_ = ''

        return max_len_name_ ,contain_sensory_word_before_flag