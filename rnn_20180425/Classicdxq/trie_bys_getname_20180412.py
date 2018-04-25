# -*- coding: utf-8 -*-
#! /usr/bin/python

import re
from Classify_data import  *
import datetime
from dict_data import *
import os
import cProfile
import time

tt = Buildtrie()


rootdir = dict_data.trie_dir['rootdir_00']
rootdir_11 = dict_data.trie_dir['rootdir_11']
rootdir_01 = dict_data.trie_dir['rootdir_01']

trie_01 = tt.Trie_oneword(rootdir_01)
trie_00 = tt.Trie_oneword(rootdir)
trie_11 = tt.Trie_oneword(rootdir_11)
# 分类
def ClassResult(x_content, trie_00,trie_11,trie_01, tt_bayes,cc_redis):
    x_content_start = x_content
    all_cut = tt_bayes.all_cat(x_content)  # 全分词列表
    dict_label = {'VIDEO': 0.0, 'CINEMA': 0.0, 'WEATHER': 0.0, 'TRANSLATE': 0.0, 'TRAILER': 0.0,
                  'TRAFFIC': 0.0, 'TIME': 0.0, 'STORY': 0.0, 'STOCK': 0.0, 'POEM': 0.0, 'NUMBER': 0.0,
                  'NEWS': 0.0, 'JOKE': 0.0, 'IMAGE': 0.0,
                  'IDIOM': 0.0, 'FINANCE': 0.0, 'EXPLORER': 0.0, 'CONTROL': 0.0, 'CONSTELLATION': 0.0,
                  'CHINESE': 0.0, 'CALCULATE': 0.0, 'BAIKE': 0.0, 'TV': 0.0, 'APP': 0.0, 'MUSIC': 0.0,
                  'SPORTS': 0.0,'SCENICAREA':0.0,'TVSHOPPING':0.0,'TRAFFICINFO':0.0}
    flag = 0#标志分类是否在前两棵树就可以判断出结果
    label = ''
    label_01=''
    video_flag = 0.0
    result_name = []
    special_label = {u'我要玩游戏':'APP',u'我想玩游戏':'APP',u'天气':'APP',u'天气预报':'APP',u'我想听歌':'APP',u'我要听歌':'APP',u'我想唱歌':'APP',u'我要唱歌':'APP'
                     ,u'播放':'CONTROL'  }
    if re.findall(ur'有.*的比赛吗',x_content) :
        label = 'VIDEO'
        flag = -1
    elif re.findall(ur'(CCTV|央视|中央|cctv)[\d一二三四五六七八九十零]+[频道台套]?',x_content) and not re.findall(ur'节目单',x_content):
        label = 'TV'
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
                    dict_label['MUSIC'] += 1.0
                    # dict_label['TIME'] += 1.0
                if re.findall(ur'[加减乘除亩\+\-\*\=]', x_content) and re.findall(ur'[\d零一二三四五六七八九十百千]+',x_content):
                    dict_label['CALCULATE'] += 1.0
                if re.findall(ur'[诗]', x_content):
                    dict_label['POEM'] += 1.0
                if re.findall(ur'[\d零一二三四五六七八九十几]+[点小时号月日]+|周[123456一二三四五六日几]+|星期[123456一二三四五六日几]+', x_content):
                    dict_label['TIME'] +=  1.0

                for k in all_cut:
                    k_11 = tt_bayes.split_data(k)
                    if trie_11.get(k_11) != None:
                        x_content = x_content.replace(k, '')
                        label_list = str(trie_11.get(k_11)).split(' ')
                        for lab_ in label_list:
                            if lab_ in dict_label:
                                dict_label[lab_] += 1.0
                # video_flag = dict_label[u'VIDEO']#标记前面是否找到video特征
    if  flag !=-1:
        x_content_org = x_content
        for redis_key in redis_keys:
            strinfo = re.compile(u'[第最后近更新的倒数下]?[零两一二三四五六七八九十百千万0-9]+[集季部期]+')
            x_content_ = strinfo.sub('', x_content)
            max_len_name, flag_v =cc_redis.GetFilmName(x_content_, redis_key)
            # print max_len_name, flag_v
            if flag_v==True:#用户输入出现'看'则video
                dict_label['VIDEO']+=1.0
            if 'figure' == redis_key and max_len_name!='':
                profess = []
                ss = max_len_name.strip().split('/')
                max_len_name = ss[0]
                for i in  ss[1].split(':'):
                    if '}' in i  :
                        rr = i.split('}')[0]
                        profess.append(rr)
                for j in profess:
                    a =  j.replace('u','').replace("'",'').strip()
                    if  a in  rediskeys_to_label:
                        max_len_name = max_len_name+'/'+a
            else:
                max_len_name = max_len_name

            if max_len_name!='':
                redis_label_list = max_len_name.strip().split('/')[1:]
                result_name.append(max_len_name.strip().split('/')[0])
                for li in redis_label_list:
                    if li in rediskeys_to_label:
                        dict_label[rediskeys_to_label[li]]+=1.0

        # if re.findall(u'[第倒数最后快进跳到]?[\d两一二三四五六七八九十百千零]+[期集季部行个页分钟秒]+', x_content_org):
        #     if dict_label['VIDEO']-video_flag>0.0:
        #         dict_label['VIDEO'] = dict_label[u'VIDEO']
        #     else:
        #         dict_label['VIDEO'] = 0.0
        #         dict_label['NEWS'] = 0.0
        #         dict_label['CONTROL'] = dict_label['CONTROL'] + 1.0

        #根据去掉特征词和季数集数剩下些字符长度来判断video或control
        # print x_content_org

        if re.findall(u'[第倒数最后快进跳到下另]?[\d两一二三四五六七八九十百千零]+[期集季部行个页分钟秒]+',x_content_org) :
            strinfo_ =  re.compile(u'(第|倒数|快进到|最后|快进|跳到|下|另)?[\d两一二三四五六七八九十百千零]+[期集季部行个页分钟秒]+')

            x_content_end =  strinfo_.sub('', x_content_org )
            # print x_content_end
            if len(x_content_end) != 0:
                dict_label['VIDEO'] = dict_label['VIDEO'] + 1.0
            else:
                #直接把control的权重设置很大？？？？？
                dict_label['VIDEO'] = 0.0
                dict_label['NEWS'] = 0.0
                dict_label['CONTROL'] = dict_label['CONTROL'] + 1.0

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

            myVocabList = dict_data.myVocabList
            p0Vect = dict_data.p0Vect
            p1Vect = dict_data.p1Vect
            p2Vect = dict_data.p2Vect
            label = tt_bayes.BayesClass(x_content, myVocabList, p0Vect, p1Vect, p2Vect)
        #返回两个及以上的类才需要加
        # if label.strip() =='IMAGE':
        #     label =label+'  '+'BAIKE'
    return label, dict_label,result_name

#输出分类结果
def Classify(x_input):
    label_result=[]
    label, labels,result_name= ClassResult(x_input,trie_00,trie_11, trie_01, tt_bayes,cc_redis)
    if " " not in label:
        label_result.append(label)
    else:
        label_list = str(label).strip().split('  ')
        #返回1个类
        # label_result.append(label_list[1])
        #返回2,3个类
        if len(label_list)>2:#返回两个类，这里取2，返回三个类，这里取3；
            label_result.extend(label_list[0:2])
        else:
            label_result.extend(label_list[0:])
    labels_ = {}
    for key,value in labels.items():
        if value!=0.0:
            labels_[key] =labels[key]
    return label_result


if __name__ == '__main__':
    # lines = codecs.open('2w_true_data.txt','r','utf-8')
    # result = codecs.open('2w_true_data_.txt','w','utf-8')
    # for line in lines:
    #     start = datetime.datetime.now()
    #     label,_,_= Classify(line.strip())
    #     time_ = datetime.datetime.now()-start
    #     result.write(line.strip()+'--->'+str(label)+'--->'+str(time_)+'\n')
    #     print line
    #     print label

    start = datetime.datetime.now()
    label ,labels,result_name= Classify(u'我想看山海关')
    end = datetime.datetime.now()
    print (end-start)
    print label
