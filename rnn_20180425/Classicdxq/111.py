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

# 分类
def class_result(x_content, trie_00,trie_11,trie_01, cc_redis, tt_bayes):
    # x_input:用户输入#t_1:前缀树，处理Type#t_:前缀树，处理闲聊和操作#t：前缀树，处理视频，音乐#cc：redis查找#tt：贝叶斯分类#label：标签
    all_cut = tt_bayes.all_cat(x_content)  # 全分词列表
    dict_label = {}
    result_dict_category = {u'VIDEO': 0.0, u'MUSIC': 0.0, u'SPORTS': 0.0,'POEM':0.0}
    result_dict_name = {}
    redis_keys = {'film': 'VIDEO', 'figure': '', 'role': 'VIDEO', 'sports_competition': 'VIDEO',
                  'sports_event': 'VIDEO', 'sports_team': 'VIDEO','poetry':'POEM','music_name':'MUSIC'}
    dict_label = {u'VIDEO': 0.0, u'CINEMA': 0.0, u'WEATHER': 0.0, u'TRANSLATE': 0.0, u'TRAILER': 0.0,
                  u'TRAFFIC': 0.0, u'TIME': 0.0, u'STORY': 0.0, u'STOCK': 0.0, u'POEM': 0.0, u'NUMBER': 0.0,
                  u'NEWS': 0.0, u'JOKE': 0.0, u'IMAGE': 0.0,
                  u'IDIOM': 0.0, u'FINANCE': 0.0, u'EXPLOER': 0.0, u'CONTROL': 0.0, u'CONSTELLATION': 0.0,
                  u'CHINESE': 0.0, u'CALCULATE': 0.0, u'BAIKE': 0.0, u'TV': 0.0, u'APP': 0.0, u'MUSIC': 0.0,
                  u'SPORTS': 0.0}


    pattern = re.compile(ur'.*(电视台|卫视|频道|CCTV|央视.*套|中央.*套|中央.*[台]?|cctv).*')
    pattern_ = re.compile(ur'[切换到四川]+.*[频道台套]|[0-9一二三四五六七八九十百]+[频道台]+')
    pattern_1 = re.compile(ur'我想唱歌|我想听歌|打开天气')


    flag = 0
    label = ''
    label_=''
    for i in all_cut:
        k = tt_bayes.split_data(i)
        if trie_01.get(k) != None:
            x_content = x_content.replace(i, '')
            label_ = str(trie_01.get(k))
    if label_ != '':
        label = label_
        flag = -1
    else:
        txt_label = {}
        for i in all_cut:
            kk = tt_bayes.split_data(i)
            if trie_00.get(kk) != None:
                x_content = x_content.replace(i, '')
                label_list = str(trie_00.get(kk)).split(' ')
                counter_label = collections.Counter(label_list)
                for key, value in counter_label.iteritems():
                    if key in txt_label:
                        txt_label[key]=txt_label[key]+len(i)
                    else:
                        txt_label[key] =  len(i)
        if txt_label!={}:
            label_ = sorted(txt_label, key=lambda x: txt_label[x])[-1]
            if label_!='':
                label = label_
                flag = -1
        else:
            if pattern_1.match(x_content):
                label = 'APP'
                flag = -1
            elif pattern_.match(x_content) or pattern.match(x_content):
                label = 'TV'
                flag = -1
            else:
                if u'歌' in x_content:  # 因为全分词后没有单个的字，这里单独处理输入中包含歌
                    dict_label[u'MUSIC'] += 1.0
                    dict_label[u'TIME'] += 1.0
                if re.findall(ur'[加减乘除亩\+\-\*\=]', x_content):
                    dict_label[u'CALCULATE'] += 1.0
                if re.findall(ur'[诗]', x_content):
                    dict_label[u'POEM'] += 1.0
                # if re.findall(u'[第倒数最后][\d一二三四五六七八九十零]+[行个页]',x_content):
                #     dict_label[u'control'] = dict_label[u'control'] + 1.0
                if re.findall(ur'([\d零一二三四五六七八九十几]+[点小时号月日])|([周星期][123456一二三四五六日几])',x_content):
                    dict_label[u'TIME'] +=  1.0
                    # dict_label[u'traffic'] = dict_label[u'traffic'] + 1.0
                # if re.findall(ur'第?[\d一二三四五六七八九十]+[集季部期]',x_content):
                #     dict_label[u'video'] = dict_label[u'video'] + 1.0
                #应用前缀树以字为节点
                for j in all_cut:
                    kkk = tt_bayes.split_data(j)
                    if trie_11.get(kkk) != None:
                        x_content = x_content.replace(j, '')
                        label_list = str(trie_11.get(kkk)).split(' ')
                        counter_label = collections.Counter(label_list)
                        for key, value in counter_label.iteritems():
                            if key in dict_label:
                                dict_label[key] += 1.0

    if  flag !=-1:
        video_dict = {}
        for redis_key in redis_keys.keys():
            strinfo = re.compile(u'[第最后近更新的倒数]+[零一二三四五六七八九十百千万0-9]+[集季部期]')
            x_content_org = x_content
            x_content_ = strinfo.sub('', x_content)
            max_len_name, flag_v = cc_redis.get_film_name(x_content_, redis_key)
            if flag_v==True:#用户输入出现'看'则video
                result_dict_category['VIDEO'] += 1.0
                result_dict_name[redis_key] = max_len_name
            if redis_key == 'figure' or redis_key == 'role' or redis_key == 'film' and max_len_name != '':
                video_dict[redis_key] = max_len_name


            if max_len_name != '':
                if redis_key == 'figure':#figure要根据职业判断领域
                    entityAql_error = 'For doc In entity Filter "%s" In doc.formatNames and doc.status == "active" RETURN doc' % (max_len_name)
                    scoreDocs_error = db.AQLQuery(entityAql_error, rawResults=True, batchSize=1000)
                    if len(scoreDocs_error)!=0:
                        if 'profession' in scoreDocs_error[0]:
                            profession = scoreDocs_error[0]['profession']
                            result_dict_name[redis_key] = max_len_name
                            if u'actor' in profession or u'director' in profession:
                                result_dict_category[u'VIDEO'] = result_dict_category[u'VIDEO']+1.0
                            elif u'sportsman' in profession:
                                result_dict_category[u'VIDEO'] = result_dict_category[u'VIDEO']+1.0

                            elif u'singer' in profession:
                                result_dict_category[u'MUSIC'] = result_dict_category[u'MUSIC']+1.0
                        else:
                            result_dict_category[u'VIDEO'] = result_dict_category[u'VIDEO']+1.0# 是人物但是没有找到职业，返回video
                else:
                        result_dict_category[redis_keys[redis_key]] = result_dict_category[redis_keys[redis_key]]+1.0
                        result_dict_name[redis_key] = max_len_name

        if re.findall(u'[第倒数最后跳到]?[\d一二三四五六七八九十百千零]+[期集季部行个页分钟秒]', x_content_org):
            if video_dict != {}:
                dict_label[u'VIDEO'] = dict_label[u'VIDEO'] + len(video_dict)
            else:
                dict_label[u'VIDEO'] = 0.0
                dict_label[u'NEWS'] = 0.0
                dict_label[u'CONTROL'] = dict_label[u'CONTROL'] + 1.0

        ss = result_dict_category[sorted(result_dict_category, key=lambda x: result_dict_category[x])[-1]]
        if ss>0.0:
            for key, value in result_dict_category.items():
                dict_label[key] = dict_label[key] + value


        #得到字典中value最大的key
        max_value = dict_label[sorted(dict_label, key=lambda x: dict_label[x])[-1]]
        max_value_key = {}

        ###########
        for key, value in dict_label.items():
            if value == max_value:
                max_value_key[key] = value

        if max_value>0.0:
            for key ,value in max_value_key.items():
                label = label+'#'+key
        else:
            # label = 'BAIKE'
            myVocabList = dict_data.myVocabList
            p0Vect = dict_data.p0Vect
            p1Vect = dict_data.p1Vect
            p2Vect = dict_data.p2Vect
            label = tt_bayes.Bayes_Class(x_content, myVocabList, p0Vect, p1Vect, p2Vect)
        #返回两个及以上的类才需要加
        if label.strip() == u'#IMAGE':
            label =label+"#"+u'BAIKE'
    return label, dict_label,result_dict_name

#输出分类结果
def classify(x_input):
    label_result=[]
    tt = Buildtrie()
    rootdir = dict_data.trie_dir['rootdir_00']
    rootdir_11 = dict_data.trie_dir['rootdir_11']
    rootdir_01 = dict_data.trie_dir['rootdir_01']
    trie_01 = tt.Trie_oneword(rootdir_01)
    trie_00 = tt.Trie_oneword(rootdir)
    trie_11 = tt.Trie_oneword(rootdir_11)

    label, labels,result_dict_name = class_result(x_input,trie_00,trie_11, trie_01,cc_redis, tt_bayes)
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
    # lines = codecs.open('2w_true_data.txt','r','utf-8')
    # result = codecs.open('2w_true_data_.txt','w','utf-8')
    # for line in lines:
    #     label,labels ,result_dict_name= classify(line.strip())
    #     result.write(line.strip()+'--->'+str(label)+'\n')
    #     print line
    #     print label
    # start = datetime.datetime.now()
    # label,labels,result_dict_name = classify(u'我想看芈月传第一百一十一集')
    # print label,labels,result_dict_name
    # print datetime.datetime.now()-start
    # #tt = Buildtrie()
    # tt = Buildtrie()
    # rootdir = dict_data.trie_dir['rootdir_00']
    # rootdir_11 = dict_data.trie_dir['rootdir_11']
    # rootdir_01 = dict_data.trie_dir['rootdir_01']
    # trie_01 = tt.Trie_oneword(rootdir_01)
    # trie_00 = tt.Trie_oneword(rootdir)
    # trie_11 = tt.Trie_oneword(rootdir_11)
    # print cProfile.run("class_result(u'我想看芈月传第一百一十一集', trie_00,trie_11,trie_01, cc_redis, tt_bayes)", sort="cumulative")

    # import numpy as np
    # print type(np.arange(10))
    x_content = u'厨星25集'
    ss = re.findall(ur'[\d零一二三四五六七八九十几]+[点小时号月日]+|周[123456一二三四五六日几]+|星期[123456一二三四五六日几]+', x_content)
    print ss[0]