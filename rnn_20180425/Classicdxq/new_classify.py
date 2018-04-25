# -*- coding: utf-8 -*-
#! /usr/bin/python
#
import codecs
import re
import collections
from Classify_data import  *
from pymongo import MongoClient
from pyArango.connection import *
import  time
conn=Connection(arangoURL = dict_data.arrangoPath,username='tester',password=123456)
db=conn[dict_data.arrangoName]
mongoClient=MongoClient(host=dict_data.mongo_path,port=dict_data.mongo_port)
db_mongo=mongoClient.MovieKnowledgeMap

# 分类
def class_result(x_content, trie_01,trie_02,trie_03, cc_redis, tt_bayes):
    # x_input:用户输入#t_1:前缀树，处理Type#t_:前缀树，处理闲聊和操作#t：前缀树，处理视频，音乐#cc：redis查找#tt：贝叶斯分类#label：标签
    all_cut = tt_bayes.all_cat(x_content)  # 全分词列表
    dict_label = {}
    result_dict_category = {u'video': 0.0, u'music': 0.0, 'poem':0.0}
    result_dict_name = {}
    redis_keys = {'film': 'video', 'figure': '', 'role': 'video', 'sports_competition': 'video',
                  'sports_event': 'video', 'sports_team': 'video','poetry':'poem','music_name':'music'}
    flag = 0  # for i in all_cut:
    #     i = tt_bayes.split_data(i)
    #     if trie_00.get(i) != None:
    #         x_content = x_content.replace(i.replace(' ', ''), '')
    #         label_list = str(trie_00.get(i)).split(' ')
    #         counter_label = collections.Counter(label_list)
    #         for key, value in counter_label.iteritems():
    #             label = key
    # if label!='':
    #     label = label
    #     flag = -1
    label = ''
    # for i in all_cut:
    #     i = tt_bayes.split_data(i)
    #     if trie_00.get(i) != None:
    #         x_content = x_content.replace(i.replace(' ', ''), '')
    #         label_list = str(trie_00.get(i)).split(' ')
    #         counter_label = collections.Counter(label_list)
    #         for key, value in counter_label.iteritems():
    #             label = key
    # if label!='':
    #     label = label
    #     flag = -1
    # else:
    # pattern = re.compile(ur'.*(电视台|卫视|频道|CCTV|央视.*套|中央.*套|中央.*[台]?|cctv).*')
    # pattern_ = re.compile(ur'[切换到四川]+.*[频道台套]|[0-9一二三四五六七八九十百]+[频道台]+')
    pattern_1 = re.compile(ur'我想唱歌|我想听歌|天气|打开天气')
    pattern_2 = re.compile(u'[第倒数最后][\d一二三四五六七八九十零]+[行个]|第?[\d一二三四五六七八九十]+[集季部期]')
    if pattern_1.match(x_content):
        label = 'APP'
        flag = -1
    elif pattern_2.match(x_content):
        label = 'control'
        flag = -1
    elif re.findall(ur'[加减乘除亩\+\-\*\=]', x_content):
        label = 'calculate'
        flag = -1
    else:
        for i in all_cut:
            i = tt_bayes.split_data(i)
            if trie_01.get(i) != None:
                x_content = x_content.replace(i.replace(' ', ''), '')
                label = str(trie_01.get(i))
        if label!='':
            label = label
            flag = -1
        else:
            for i in all_cut:
                i = tt_bayes.split_data(i)
                if trie_02.get(i) != None:
                    x_content = x_content.replace(i.replace(' ', ''), '')
                    label_list = str(trie_02.get(i)).split(' ')
                    counter_label = collections.Counter(label_list)
                    for key, value in counter_label.iteritems():
                        label = key
                if label!='':
                    label = label
                    flag = -1
                else:
                    dict_label = {u'time':0.0,u'video':0.0,u'poem':0.0,u'news':0.0,u'control':0.0,u'baike':0.0,u'music':0.0}
                    if re.findall(ur'[诗]', x_content):
                        dict_label[u'poem'] = dict_label[u'poem'] + 1.0
                    if re.findall(ur'([\d零一二三四五六七八九十几]+[点小时号月日])|([周星期][123456一二三四五六日几])',x_content):
                        dict_label[u'time'] = dict_label[u'time'] + 1.0
                        # dict_label[u'traffic'] = dict_label[u'traffic'] + 1.0
                    #应用前缀树以字为节点
                    for j in all_cut:
                        label = ''
                        j = tt_bayes.split_data(j)
                        if trie_03.get(j) != None:
                            x_content = x_content.replace(j.replace(' ', ''), '')
                            label_list = str(trie_03.get(j)).split(' ')
                            counter_label = collections.Counter(label_list)
                            for key, value in counter_label.iteritems():
                                if key in dict_label:
                                    dict_label[key] = dict_label[key]+1.0

    if  flag !=-1:
        for redis_key in redis_keys.keys():
            strinfo = re.compile(u'[第最后近更新的倒数]+[一二三四五六七八九十百千万0-9]+[集季部]')
            x_content = strinfo.sub('', x_content)
            max_len_name, flag_v = cc_redis.get_film_name(x_content, redis_key)
            if flag_v==True:#用户输入出现'看'则video
                result_dict_category['video'] = result_dict_category['video']+1.0
                result_dict_name[redis_key] = max_len_name
            if max_len_name != '':
                if redis_key == 'figure':#figure要根据职业判断领域
                    entityAql_error = 'For doc In entity Filter "%s" In doc.formatNames and doc.status == "active" RETURN doc' % (
                    max_len_name)
                    scoreDocs_error = db.AQLQuery(entityAql_error, rawResults=True, batchSize=1000)
                    if len(scoreDocs_error)!=0:
                        if 'profession' in scoreDocs_error[0]:
                            profession = scoreDocs_error[0]['profession']
                            result_dict_name[redis_key] = max_len_name
                            if u'actor' in profession or u'director' in profession:
                                result_dict_category[u'video'] = result_dict_category[u'video']+1.0
                            elif u'sportsman' in profession:
                                result_dict_category[u'video'] = result_dict_category[u'video']+1.0

                            elif u'singer' in profession:
                                result_dict_category[u'music'] = result_dict_category[u'music']+1.0
                        else:
                            result_dict_category[u'video'] = result_dict_category[u'video']+1.0# 是人物但是没有找到职业，返回video
                else:
                        result_dict_category[redis_keys[redis_key]] = result_dict_category[redis_keys[redis_key]]+1.0
                        result_dict_name[redis_key] = max_len_name

        ss = result_dict_category[sorted(result_dict_category, key=lambda x: result_dict_category[x])[-1]]
        if ss!=0.0:
            for key, value in result_dict_category.items():
                dict_label[key] = dict_label[key] + value

        #得到字典中value最大的key
        max_value = dict_label[sorted(dict_label, key=lambda x: dict_label[x])[-1]]
        max_value_key = {}
        for key, value in dict_label.items():
            if value == max_value:
                max_value_key[key] = value
        if max_value!=0.0:
            for key ,value in max_value_key.items():
                label = label+'#'+key
        else:
            myVocabList = dict_data.myVocabList
            p0Vect = dict_data.p0Vect
            p1Vect = dict_data.p1Vect
            p2Vect = dict_data.p2Vect
            label = tt_bayes.Bayes_Class(x_content, myVocabList, p0Vect, p1Vect, p2Vect)
        #返回两个及以上的类才需要加
        if label.strip() == u'#image':
            label =label+"#"+u'baike'
    return label, dict_label,result_dict_name

#输出分类结果
def classify(x_input):
    label_result=[]
    tt = Buildtrie()
    rootdir_01 = dict_data.trie_dir['rootdir_01']
    rootdir_02 = dict_data.trie_dir['rootdir_02']
    rootdir_03 = dict_data.trie_dir['rootdir_03']
    trie_01 = tt.Trie_oneword(rootdir_01)
    trie_02 = tt.Trie_oneword(rootdir_02)
    trie_03= tt.Trie_oneword(rootdir_03)
    label, labels,result_dict_name = class_result(x_input,trie_01,trie_02, trie_03,cc_redis, tt_bayes)
    if "#" not in label:
        label_result.append(label)
    else:
        label_list = str(label).strip().split('#')
        #返回1个类
        # label_result.append(label_list[1])
        #返回2,3个类
        if len(label_list)>2:#返回两个类，这里取2，返回三个类，这里取3；
            label_result.extend(label_list[1:3])
        else:
            label_result.extend(label_list[1:])
    labels_ = {}
    for key,value in labels.items():
        if value!=0.0:
            labels_[key] =labels[key]
    return label_result,labels_,result_dict_name


if __name__ == '__main__':
    lines = codecs.open('2w_true_data.txt','r','utf-8')
    result = codecs.open('2w_true_data_.txt','w','utf-8')
    for line in lines:
        label,labels ,result_dict_name= classify(line.strip())
        result.write(line.strip()+'--->'+str(label)+'\n')
    #     print line
        print label

    #
    # label,labels,result_dict_name = classify(u'芈月传几时播')
    # print label,labels,result_dict_name
