# -*- coding: utf-8 -*-
#! /usr/bin/python

from numpy import *
import pandas as pd
import jieba
import codecs
import redis
import re
import os,sys
reload(sys)
sys.setdefaultencoding('utf8')

#贝叶斯分类
class BayesClass:

    #对文本完全分词
    def all_cat(self,sentence):
      # sentence：用户输入
      # spritall：列表，包含全分词的所有词
      spritall = []
      length = len(sentence)
      for i in range(length):
          for j in range(length, i + 1, -1):
              str = sentence[i: j]
              spritall.append(str)
      return spritall

    #读取数据
    def data_load(self,filename):
        #filename:文件名
        #data_dict：训练数据结巴
        # data_label：训练数据的标签
        data = pd.read_excel(filename, header=0)
        data['data'] = data['data'].apply(lambda s: jieba.lcut(s))  # 调用结巴分词
        data_dict = data['data']
        data_label = data['lable']
        return data_dict, data_label
    #构建字典
    def createVoctorList(self,dataSet):
        voctorSet = []
        for word_document in dataSet:
            for i in word_document:
                if i not in voctorSet:
                    voctorSet.append(i)
        return voctorSet
    #构建词向量
    def createVoctorList_1(self,vocabList, inputSet):
      retVocabList = [0] * len(vocabList)
      for word in inputSet:
          if word in vocabList:
              retVocabList[vocabList.index(word)] = 1
      return retVocabList
    #贝叶斯分类
    def Bayes_Class(self,s,filename):
        trainMat = []
        listOPosts, listClasses = self.data_load(filename)
        myVocabList = self.createVoctorList(listOPosts)
        for postinDoc in listOPosts:
            trainMat.append(self.createVoctorList_1(myVocabList, postinDoc))

        trainMatrix = array(trainMat)
        trainCatergory = array(listClasses)

        n1 = 0
        n2 = 0
        n3 = 0
        n4 = 0
        for number in trainCatergory:
            if number == 0:
                n1 = n1 + 1
            elif number == 1:
                n2 = n2 + 1
            elif number == 2:
                n3 = n3 + 1
            else:
                n4 = n4 + 1

        numTrainDoc = len(trainMatrix)
        numWords = len(trainMatrix[0])
        pA0sive = n1 / float(numTrainDoc)
        pA1sive = n2 / float(numTrainDoc)
        pA2sive = n3 / float(numTrainDoc)
        pA3sive = n4 / float(numTrainDoc)

        p0Num = ones(numWords)
        p1Num = ones(numWords)
        p2Num = ones(numWords)
        p3Num = ones(numWords)

        p0Denom = 2.0
        p1Denom = 2.0
        p2Denom = 2.0
        p3Denom = 2.0

        for i in range(numTrainDoc):
            if trainCatergory[i] == 1:
                p1Num += trainMatrix[i]
                p1Denom += sum(trainMatrix[i])
            elif trainCatergory[i] == 0:
                p0Num += trainMatrix[i]
                p0Denom += sum(trainMatrix[i])
            elif trainCatergory[i] == 2:
                p2Num += trainMatrix[i]
                p2Denom += sum(trainMatrix[i])
            else:
                p3Num += trainMatrix[i]
                p3Denom += sum(trainMatrix[i])

        p1Vect = log(p1Num / p1Denom)  # 处于精度的考虑
        p0Vect = log(p0Num / p0Denom)
        p2Vect = log(2 * p2Num / p2Denom)
        p3Vect = log(3 * p3Num / p3Denom)
        spritall = []
        spritall_1 = []
        for one_word in s.split(' ')[0]:
            spritall_1.append(one_word)
        flag = False
        length = len(s)
        for i in range(length):
            for j in range(length, i + 1, -1):
                str = s[i: j]
                spritall.append(str)
        thisDoc = array(self.createVoctorList_1(myVocabList, spritall))
        p1 = sum(thisDoc * p1Vect) + log(0.1)
        p2 = sum(thisDoc * p2Vect) + log(0.01)
        p0 = sum(thisDoc * p0Vect) + log(0.99)
        maxp = max(p1, p2, p0)
        if maxp == p1:
            label = 'video'
        elif maxp == p2:
            label = 'music'
        else:
            label = 'talking'
        return label

#前缀树
class TrieTree(object):

  def __init__(self):
    self.tree = {}
    self.origin=''
    self.tag = ''
    self.child=self.tree

#构建前缀树
  def add(self, word,tag):
    tree = self.tree
    for char in word:
      if char in tree:
        tree = tree[char]
      else:
        tree[char] = {}
        tree = tree[char]
    tree['exist'] = True
    tree['tag'] = tag
    tree['origin'] = word

#前缀树查询
  def search(self, word):
    #word:一个词
    tree = self.tree
    for char in word:
      if char in tree:
        tree = tree[char]
      else:
        return False
    if "exist" in tree and tree["exist"] == True:
      self.origin = tree['origin']
      self.tag = tree['tag']
      return True
    else:
      return False

# 获取文本中的最长电影名字，演员，角色字符串
# 自研电影名字库保存在 redis中
class GetFilmName:
    def __init__(self, host_, port_, redis_index_):
        self.redis_conn_pool = redis.ConnectionPool(host=host_, port=port_, db=redis_index_, decode_responses=True)
        self.r = redis.Redis(connection_pool=self.redis_conn_pool)

    def get_film_name(self, text_str_, redis_key_):
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
            return max_len_name_

        # 被提取的字符串替换为‘#’号
        replace_str = '#' * len(max_len_name_)
        temp_str_ = text_str_.replace(max_len_name_, replace_str)

        # 感官词判断
        sensory_words = [u'看', u'听']  # 感官词
        contain_sensory_word_before_flag = False  # 提取出的字符串之前包含感官词
        for sensory_word in sensory_words:
            if sensory_word in temp_str_[: temp_str_.rfind(replace_str)]:
                contain_sensory_word_before_flag = True

                # 不包含感官词的情况
        ss = [u'电视剧', u'电影', u'电视连续剧',u'集',u'季',u'部',u'期',u'版',u'导演',
              u'参演',u'主演',u'演']
        flag = False
        for i in ss:
            if i in text_str_ and (not contain_sensory_word_before_flag):
                if len(max_len_name_ + i) * 1.0 / len(text_str_) < 2./3:  # 没有感官词，但有明确类型
                    max_len_name_ = ''
                flag = True

        if (not flag) and (not contain_sensory_word_before_flag) and len(max_len_name_) * 1.0 / len(
                text_str_) < 2./3:
            max_len_name_ = ''

        return max_len_name_


def class_result(s, t, t_, cc, tt, t_1):
    flag_ = 0
    if len(s) == 1:
        flag_ = -1
    label = ''
    pattern = re.compile(r'.*(电视台|卫视|频道).*')
    if pattern.match(s):
        label = 'operation'

        # type
    else:
        ll_1 = tt.all_cat(s)
        for i in ll_1:
            if t_1.search(i.strip()) == False:

                label = 'no_1'
            else:
                label = str(t_1.tag)
                break

        # talking,opertation
        if label == 'no_1':

            ll_ = tt.all_cat(s)
            for i in ll_:
                if t_.search(i) == False:
                    label = 'no_'
                else:
                    label = str(t_.tag)
                    break
        # video,music
        if label == 'no_':

            ll = tt.all_cat(s)
            for i in ll:
                if t.search(i) == False:
                    label = 'no'
                else:
                    label = str(t.tag)
                    break

    if label == 'no' or flag_ == -1:
        redis_keys = ['film', 'figure', 'role']
        for redis_key in redis_keys:
            strinfo = re.compile(u'[第最后近更新的倒数]+[一二三四五六七八九十百千万0-9]+[集季部]')
            s = strinfo.sub('', s)

            max_len_name = cc.get_film_name(s, redis_key)
            if max_len_name != '':
                label = 'video'
                break
            else:
                label = 'nono'

    if label == 'nono':
        label = tt.Bayes_Class(s, 'true_data.xlsx')
    return label

from config_database import config
def classify(s):
    host = config.redis_ip
    port = config.redis_port
    redis_index = config.redis_db_c
    cc = GetFilmName(host, port, redis_index)

    #前缀树
    # rootdir = 'F:\\WORK_2017\\liyinglie_bys_\\trie_bayes_class_20180123\\triedata\\'
    # rootdir_ = 'F:\\WORK_2017\\liyinglie_bys_\\trie_bayes_class_20180123\\triedata_\\'
    # rootdir_1 ='F:\\WORK_2017\\liyinglie_bys_\\trie_bayes_class_20180123\\triedata_1\\'

    rootdir = 'triedata/'
    rootdir_ = 'triedata_/'
    rootdir_1 = 'triedata_1/'

    rootdir_1 = "%s%s%s" % (sys.path[0], '/', rootdir_1)
    t_1 = TrieTree()
    list_1 = os.listdir(rootdir_1)
    for fi in list_1:
        with codecs.open('%s%s' % (rootdir_1, fi), 'r', 'utf-8') as fn:
            for f in fn:
                line = f.rstrip()
                t_1.add(line, fi)

    t_ = TrieTree()
    rootdir_ = "%s%s%s" % (sys.path[0], '/', rootdir_)
    list_ = os.listdir(rootdir_)
    for fi in list_:
          with codecs.open('%s%s' % (rootdir_, fi), 'r', 'utf-8') as fn:
              for f in fn:
                  line = f.rstrip()
                  t_.add(line, fi)

    t = TrieTree()
    rootdir = "%s%s%s" % (sys.path[0], '/', rootdir)
    list = os.listdir(rootdir)
    for fi in list:
          with codecs.open('%s%s' % (rootdir, fi), 'r', 'utf-8') as fn:
              for f in fn:
                  line = f.rstrip()
                  t.add(line, fi)

    #贝叶斯
    tt = BayesClass()
    label = class_result(s, t, t_, cc, tt,t_1)
    return label



if __name__ == '__main__':
    label = classify(u'播放从容的电影')
    print (label)




