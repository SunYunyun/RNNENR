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
import datetime
import cProfile

conn=Connection(arangoURL = dict_data.arrangoPath,username='tester',password=123456)
db=conn[dict_data.arrangoName]
mongoClient=MongoClient(host=dict_data.mongo_path,port=dict_data.mongo_port)
db_mongo=mongoClient.MovieKnowledgeMap

tt = Buildtrie()
rootdir = dict_data.trie_dir['rootdir_00']
rootdir_11 = dict_data.trie_dir['rootdir_11']
rootdir_01 = dict_data.trie_dir['rootdir_01']
trie_01 = tt.Trie_oneword(rootdir_01)
trie_00 = tt.Trie_oneword(rootdir)
trie_11 = tt.Trie_oneword(rootdir_11)
# 分类
def class_result(x_content, trie_00,trie_11,trie_01,cc_redis, tt_bayes):

    all_cut = tt_bayes.all_cat(x_content)  # 全分词列表
    result_dict_category = {u'VIDEO': 0.0, u'MUSIC': 0.0, u'SPORTS': 0.0, 'POEM': 0.0}
    result_dict_name = {}
    redis_keys = {'film': 'VIDEO', 'figure': '', 'role': 'VIDEO', 'sports_competition': 'VIDEO',
                  'sports_event': 'VIDEO', 'sports_team': 'VIDEO', 'poetry': 'POEM', 'music_name': 'MUSIC'}
    dict_label = {u'VIDEO': 0.0, u'CINEMA': 0.0, u'WEATHER': 0.0, u'TRANSLATE': 0.0, u'TRAILER': 0.0,
                  u'TRAFFIC': 0.0, u'TIME': 0.0, u'STORY': 0.0, u'STOCK': 0.0, u'POEM': 0.0, u'NUMBER': 0.0,
                  u'NEWS': 0.0, u'JOKE': 0.0, u'IMAGE': 0.0,
                  u'IDIOM': 0.0, u'FINANCE': 0.0, u'EXPLORER': 0.0, u'CONTROL': 0.0, u'CONSTELLATION': 0.0,
                  u'CHINESE': 0.0, u'CALCULATE': 0.0, u'BAIKE': 0.0, u'TV': 0.0, u'APP': 0.0, u'MUSIC': 0.0,
                  u'SPORTS': 0.0}
    flag = 0#标志分类是否在前两棵树就可以判断出结果
    label = ''
    label_01=''
    video_flag = 0.0
    result_name = []
    special_label = {u'天气':u'APP',u'天气预报':u'APP',u'打开天气':u'APP'}
    if re.findall(ur'有.*的比赛吗',x_content) :
        label = u'VIDEO'
        flag = -1
    elif x_content in special_label:
        label = special_label[x_content]
        flag = -1

    else:
        for i in all_cut:
            k_01 = tt_bayes.split_data(i)
            if trie_01.get(k_01) != None:
                x_content = x_content.replace(i, '')
                label_01 = str(trie_01.get(k_01))

        if label_01 != '':
            label = label_01
            flag = -1
        else:
            txt_label = {}
            for j in all_cut:
                k_00 = tt_bayes.split_data(j)
                if trie_00.get(k_00) != None:
                    x_content = x_content.replace(j, '')
                    label_list = str(trie_00.get(k_00)).split(' ')

                    for lab in label_list:
                        if lab in txt_label:
                            txt_label[lab]=txt_label[lab]+len(j)
                        else:
                            txt_label[lab] =  len(j)
            if txt_label!={}:
                label_00 = sorted(txt_label, key=lambda x: txt_label[x])[-1]
                if label_00!='':
                    label = label_00
                    flag = -1
            else:
                if u'歌' in x_content:  # 因为全分词后没有单个的字，这里单独处理输入中包含歌
                    dict_label[u'MUSIC'] += 1.0
                    dict_label[u'TIME'] += 1.0
                if re.findall(ur'[加减乘除亩\+\-\*\=]', x_content) and re.findall(ur'[\d零一二三四五六七八九十百千]+',x_content):
                    dict_label[u'CALCULATE'] += 1.0
                if re.findall(ur'[诗]', x_content):
                    dict_label[u'POEM'] += 1.0
                if re.findall(ur'([\d零一二三四五六七八九十几]+[点小时号月日])|([周星期][123456一二三四五六日几])',x_content):
                    dict_label[u'TIME'] +=  1.0

                for k in all_cut:
                    k_11 = tt_bayes.split_data(k)
                    if trie_11.get(k_11) != None:
                        x_content = x_content.replace(k, '')
                        label_list = str(trie_11.get(k_11)).split(' ')
                        for lab_ in label_list:
                            if lab_ in dict_label:
                                dict_label[lab_] += 1.0
                video_flag = dict_label['VIDEO']
    if flag != -1:
        video_dict = {}
        for redis_key in redis_keys.keys():
            strinfo = re.compile(u'[第最后近更新的倒数]+[零一二三四五六七八九十百千万0-9]+[集季部期]')
            x_content_org = x_content
            x_content_ = strinfo.sub('', x_content)
            max_len_name, flag_v = cc_redis.get_film_name(x_content_, redis_key)
            if flag_v == True:  # 用户输入出现'看'则video
                result_dict_category['VIDEO'] += 1.0
                result_dict_name[redis_key] = max_len_name
            if redis_key == 'figure' or redis_key == 'role' or redis_key == 'film' and max_len_name != '':
                video_dict[redis_key] = max_len_name

            if max_len_name != '':
                if redis_key == 'figure':  # figure要根据职业判断领域
                    entityAql_error = 'For doc In entity Filter "%s" In doc.formatNames and doc.status == "active" RETURN doc' % (
                    max_len_name)
                    scoreDocs_error = db.AQLQuery(entityAql_error, rawResults=True, batchSize=1000)
                    if len(scoreDocs_error) != 0:
                        if 'profession' in scoreDocs_error[0]:
                            profession = scoreDocs_error[0]['profession']
                            result_dict_name[redis_key] = max_len_name
                            if u'actor' in profession or u'director' in profession:
                                result_dict_category[u'VIDEO'] = result_dict_category[u'VIDEO'] + 1.0
                            elif u'sportsman' in profession:
                                result_dict_category[u'VIDEO'] = result_dict_category[u'VIDEO'] + 1.0

                            elif u'singer' in profession:
                                result_dict_category[u'MUSIC'] = result_dict_category[u'MUSIC'] + 1.0
                        else:
                            result_dict_category[u'VIDEO'] = result_dict_category[u'VIDEO'] + 1.0  # 是人物但是没有找到职业，返回video
                else:
                    result_dict_category[redis_keys[redis_key]] = result_dict_category[redis_keys[redis_key]] + 1.0
                    result_dict_name[redis_key] = max_len_name

        if re.findall(u'[第倒数最后快进跳到]?[\d两一二三四五六七八九十百千零]+[期集季部行个页分钟秒]+', x_content_org):
            if dict_label['VIDEO']-video_flag>0.0:
                dict_label[u'VIDEO'] = dict_label[u'VIDEO']
            else:
                dict_label[u'VIDEO'] = 0.0
                dict_label[u'NEWS'] = 0.0
                dict_label[u'CONTROL'] = dict_label[u'CONTROL'] + 1.0

        ss = result_dict_category[sorted(result_dict_category, key=lambda x: result_dict_category[x])[-1]]
        if ss > 0.0:
            for key, value in result_dict_category.items():
                dict_label[key] = dict_label[key] + value
        #得到字典中value最大的key
        label_sort = sorted(dict_label, key=lambda x: dict_label[x])
        k = -2
        label_ep = ''
        label_value = 0.0
        if dict_label[label_sort[-1]]>0.0:
            label_ep = label_sort[-1]
            label_value = dict_label[label_sort[-1]]
        if label_value == dict_label[label_sort[k]]:
            label_ep = label_ep +'  '+ label_sort[k]
            k -=1
        else:
            pass
        if label_ep !='':
            label = label_ep
        else:
        #     label = 'BAIKE'
            myVocabList = dict_data.myVocabList
            p0Vect = dict_data.p0Vect
            p1Vect = dict_data.p1Vect
            p2Vect = dict_data.p2Vect
            label = tt_bayes.Bayes_Class(x_content, myVocabList, p0Vect, p1Vect, p2Vect)
        #返回两个及以上的类才需要加
        if label.strip() == u'#IMAGE':
            label =label+"#"+u'BAIKE'
    return label, dict_label,result_name

#输出分类结果
def classify(x_input):
    label_result=[]
    label, labels,result_name= class_result(x_input,trie_00,trie_11, trie_01, cc_redis,tt_bayes)
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
    return label_result,labels_,result_name


if __name__ == '__main__':
    # lines = codecs.open('2w_true_data.txt','r','utf-8')
    # result = codecs.open('2w_true_data_.txt','w','utf-8')
    # for line in lines:
    #     start = datetime.datetime.now()
    #     label,labels ,result_dict_name= classify(line.strip())
    #     time_ = datetime.datetime.now()-start
    #     result.write(line.strip()+'--->'+str(label)+'--->'+str(time_)+'\n')
    #     print line
    #     print label
    # # for i in range(100):
    start = datetime.datetime.now()
    label ,labels,result_name= classify(u'我想看刘德华的电影')
    end = datetime.datetime.now()
    print (end-start)
    print label ,labels,result_name
    # tt = Buildtrie()
    # rootdir = dict_data.trie_dir['rootdir_00']
    # rootdir_11 = dict_data.trie_dir['rootdir_11']
    # rootdir_01 = dict_data.trie_dir['rootdir_01']
    # trie_01 = tt.Trie_oneword(rootdir_01)
    # trie_00 = tt.Trie_oneword(rootdir)
    # trie_11 = tt.Trie_oneword(rootdir_11)
    # print cProfile.run("class_result(u'有维切利的比赛吗', trie_00,trie_11,trie_01, cc_redis, tt_bayes)", sort="cumulative")

    # import numpy as np
    # print type(np.arange(10))