#encoding:utf-8
# encoding: utf-8
from fuzzywuzzy import fuzz
from xpinyin import Pinyin
from pymongo import MongoClient
from datetime import datetime
from pyArango.connection import Connection
from collections import OrderedDict
import redis
from ConfigError import config,clients

config.dev_address=102

pinyin=Pinyin()
conR=redis.Redis(host=config.redis_ip,port=config.redis_port,db=config.redis_db_error)
conn=Connection(config.arrangoPath,username='tester',password=123456)
db_arango=conn[config.arrangoName]

conMongo=MongoClient(host=config.mongo_path,port=config.mongo_port)
db_mongo=conMongo[config.mongoDB]

correct_db=db_mongo.error_logging
wrong_db=db_mongo.error_fail

class ProofCheck:
    # def __init__(self,thresholds,confusingRedis,stopWord):
    #     self.thresholds=thresholds
    #     self.confusingRedis=confusingRedis
    #     self.stopWord=stopWord

    def ErrorSuggestMUVIDEO(self, txt,clientDomian,stopWord,confusingRedis,domain):
        mongodic = {};mongodic2 = {}
        mongodic['error_input'] = txt
        sInput_py, categorys, flag_er, input_list = self.PreprocessMuVi(txt, clientDomian)
        twoGrams=[txt[i] + txt[i + 1] for i in range(0, len(txt) - 1)]
        suggests = self.get_Suggests(twoGrams, stopWord, confusingRedis)
        mongodic['striped_py'] = sInput_py

        if input_list == []:
            if flag_er > 0 or (flag_er==0 and len(txt)>=4):
                mongodic2 = self.singular_match(txt, sInput_py,suggests)

                if mongodic2:
                    temp_result=self.MaximumResult(mongodic2)
                    str1=domain+':'+str(temp_result[1])

                    final_result=self.result_form(str1,categorys)
                    self.writeToMongo(str1, mongodic2)
                    return final_result
                else:return None
            else:
                return None
        else:
            mongodic1 = self.singular_match(txt, input_list[0],suggests)
            mongodic2 = self.singular_match(txt, input_list[1],suggests)

            temp=self.MaximumResult(mongodic1)
            temp2=self.MaximumResult(mongodic2)
            str_re=domain+':'+temp[1]
            str_re2=domain+':'+temp2[1]
            merge_dic1 = dict(mongodic, **mongodic1)
            merge_dic2 = dict(mongodic, **mongodic2)
            final_result1 = dict(self.result_form(str_re, categorys))
            final_result2 = dict(self.result_form(str_re2, categorys))

            for label_e, value_e in final_result1.items():
                if label_e in final_result2.keys():
                    final_result2[label_e] = value_e + ',' + final_result2[label_e]
                else:
                    final_result2[label_e] = value_e
            print 'final result2:',final_result2
            monResult=temp[1]+temp2[1]
            findic=dict(merge_dic1,**merge_dic2)
            self.writeToMongo(monResult, findic)
            # self.writeToMongo(result2, merge_dic2)
            return final_result2

    def ErrorSuggestTV(self, txt):
        sInput_station = self.PreSuffixStation(txt)
        # print 'sinputStation:',sInput_station
        sInput_TV, number, tvset_op = self.PreprocessAppTV(txt,clients.prefixAPPTV())
        # print 'sInputTV:',sInput_TV, number, tvset_op
        suggestTV=self.get_Suggests(txt,'semantic:error_correct:stopWordAPPTv','semantic:error_correct:ConfusingTV')
        suggeststation=self.get_Suggests(txt,'semantic:error_correct:stopWordAPPTv','semantic:error_correct:ConfusingAPP')

        dicResultTV=self.singular_match(txt,sInput_TV,suggestTV,'MinThresholdsTV')
        dicstation=self.singular_match(txt,sInput_station,suggeststation,'MinThresholdsStation')

        temp=self.MaximumResult(dicResultTV)
        temp2 = self.MaximumResult(dicstation)

        TVResult, TVScore=temp[1],temp[0]
         # print StationResult,StationScore
        StationResult, StationScore=temp2[1],temp[0]

        if TVScore>StationScore:
            if tvset_op != 'None' and number != None:
                finalresult = TVResult + tvset_op + str(number)
            elif tvset_op == 'None' and number != None :
                finalresult = TVResult + str(number)
            elif tvset_op != 'None' and number == None:
                finalresult = TVResult + tvset_op
            else:finalresult=TVResult
        elif StationScore>=TVScore and len(txt)>3:
            finalresult=StationResult
        else:finalresult='fail'
        return finalresult

    def MaximumResult(self,reDic):

        return max(zip(reDic.values(),reDic.keys()))


    def transNumTV(self, txt):
# this is to change chinese characters to numbers
        chiNum = {"1": "一 十", "2": "二", "3": "三", "4": "四", "5": "五 伍", "6": "六", "7": "七 柒 期", "8": "八", "9": "九",
                  "0": "零", "00": "百", "100": "最大"}
        txtLength = len(txt)
        if txt.endswith(u'一点') is False:
            for num, chi in chiNum.items():
                for chinese in chi.split(' '):
                    replacePosit = txt.find(chinese.decode('utf-8'), txtLength / 2 - 1)
                    if txt.find(chinese.decode('utf-8'), txtLength / 2 - 1) != -1:
                        if len(chinese) == 1:
                            txt = txt[:replacePosit] + num + txt[(replacePosit + 1):]
                        else:
                            txt = txt.replace(chinese.decode('utf-8'), num)
                    if txt.find(chinese.decode('utf-8'), 0, txtLength / 2 - 1) != -1:
                        txt = txt.replace(chinese.decode('utf-8'), '')
        return txt

    def PreSuffixStation(self,txt):
        txt = txt.strip('恩')
        txt = txt.strip('嗯')
        sInput_py=pinyin.get_pinyin(txt,'')
        prefix_station = {u"我想看": "woxiangkan xiangkan woxiangwan xiangwan woxiangdakai woxiang woyaokan "
                             "changhongxiaobai congxiaobai biede woyao qiehuandao liuan tangxiaobai "
                             "bangwoxiaobai xiaobai chuangexiaobai xiaobai",
                     u"打开": "dakai qiehuandao kaidao tiaojiedao tiaodao tiaojiezhi tiaozhi tiaojie shangge shangshangge",
                     u"切换": "tiaozhuan tiao zhuan kuaitui kuaijin bofang dianbo kan sousuo fangying",
                     u"语气词": "qing ba tiao"}


        for pre_key, pre_value in prefix_station.items():
            for confusion_word in pre_value.split(' '):
                if sInput_py.strip().startswith(''.join(confusion_word)) == True:
                    sInput_py = sInput_py.replace(''.join(confusion_word), '')
        return sInput_py

    def PreprocessMuVi(self,txt,clientDomian):
        txt = txt.strip('集')
        txt = txt.strip('季')
        txt = txt.strip('恩')
        txt = txt.strip('嗯')
        flag_pre = 0;flag_su = 0
        sInput_py = pinyin.get_pinyin(txt, '')
        sInput_py = ''.join(sInput_py)
        category=''
        categorys,prefix_music,suffix_music,middle_music=clientDomian
        for pre_key, pre_value in categorys.items():
            for confusion_word in pre_value.split(' '):
                if sInput_py.find(''.join(confusion_word))!=-1:
                    category='category:'+pre_key
        prefixMuList =reversed([value.decode('utf-8') for k, va in prefix_music.items()
                                for value in reversed(va.split(' '))])
        suffixMuList=reversed([value for k,va in suffix_music.items()
                                            for value in reversed(va.split(' '))])
        for preValue in prefixMuList:
            if sInput_py.startswith(preValue.encode('utf-8')) is True:

                sInput_py = sInput_py.replace(preValue, '')
                flag_pre = 1
        for suValue in suffixMuList:
            if sInput_py.startswith(suValue) is True:
                sInput_py = sInput_py.replace(suValue, '')
                flag_su = 1
        for mid_key,mid_value in middle_music.items():
            for mid_wrd in mid_value.split(' '):
                if sInput_py.find(''.join(mid_wrd))!=-1:
                    sInput_py=sInput_py.replace(''.join(mid_wrd),'#')
        flag_er = flag_pre + flag_su
        input_py=[]
        if sInput_py.find('#')!=-1:
            input_py.append(sInput_py.split('#')[0])
            input_py.append(sInput_py.split('#')[1])
        # print sInput_py,input_py

        return sInput_py,category,flag_er,input_py


# this is to deal non-necessary words
# this seperate numbers and chinese text
# i.e. set voloumn to 5,it will return:
# txt:set voloumn to;number:5
    def PreprocessAppTV(self,txt,clientDomian):

        txt = txt.strip('恩')
        txt = txt.strip('嗯')
        txt_ = self.transNumTV(txt)

        number = filter(lambda x: x in u'1234567890', txt_)

        if number == '':
            number = None
        else:
            number = number
            txt1 = txt_[0:-1]
            txt = filter(lambda x: x not in u'0123456789', txt1)

        sInput_py = pinyin.get_pinyin(txt, '')
        prefix_APPTV,suffix_AppTV=clientDomian

        tempcate = ''
        for pre_key, pre_value in prefix_APPTV.items():
            for confusion_word in pre_value.split(' '):
                if sInput_py.strip().startswith(''.join(confusion_word)) == True:
                    # print 'pre:',confusion_word,pre_key
                    tempcate = tempcate + pre_key
                    sInput_py = sInput_py.replace(''.join(confusion_word), '')
                else:
                    tempcate = tempcate

        for suf_key, suf_value in suffix_AppTV.iteritems():
            for con_word in suf_value.split(' '):
                if sInput_py.strip().endswith(''.join(con_word).strip()) is True:
                    # print 'suffix',con_word
                    tempcate += suf_key
                    sInput_py = sInput_py.replace(''.join(con_word), '')
                else:
                    tempcate = tempcate
# this is to find out whether it is a 'add' or 'deduct' action
        word_str = [u'增加', u'减少', u'一点']
        tvset_op = 'None'
        # print tempcate,'tempcate'
        for i in word_str:
            if tempcate.find(i) != -1:
                tvset_op = i
        return sInput_py, number, tvset_op

    def get_Suggests(self,txt,stopList, redisDBname):
        # stop_words = str(conR.get('semantic:error_correct:stopword4Video'))
        stop_words = str(conR.get(stopList))
        # stop_words=stop_words+'aide dege made'
        # print 'stopword4Video:', stop_words, type(stop_words)

        candidate_py = set();out_candidate=set()
        for word in txt:

            word = word.strip('看')
            word = word.strip('第')
            word = word.strip('集')
            word = word.strip('季')
            # word = word.strip('的')

            word_str = pinyin.get_pinyin(word, '')
            if stop_words.find(word_str) == -1 and len(word) > 1:
                candidate_py.add(word_str)
        if candidate_py != set():
            out = set(conR.hmget(redisDBname, candidate_py))
            for i in out:
                if i is not None and ',' not in i:
                    out_candidate.add(i.decode('utf-8'))
                elif i is not None and ',' in i:
                    newstr = str(i).split(',')
                    for line in newstr:
                        # print 'video',line.decode('utf-8')
                        out_candidate.add(line.decode('utf-8'))
        else:out_candidate=[]
        # print out_candidate,'video'
        return out_candidate

    def singular_match(self, txt, sInput_py, suggestlist):
        # temp = [txt[i] + txt[i + 1] for i in range(0, len(txt) - 1)]
        # suggestlist_actor=self.get_video(temp,'semantic:error_correct:stopword4Video','semantic:error_correct:ConfusingMusic')
        # suggestlist_actor = self.get_video(temp, stopWord, confusingRedis)
        # print len(suggestlist)

        # minScoreSet=[int(i) for i in ScoreSet.split(',')]
        # print 'minScoreSet:',minScoreSet
        mongodic = OrderedDict()
        # print ScoreSet
        suggestedStr = ''
        # tempdic_ac = OrderedDict()
        for key in suggestlist:
            key2_py=pinyin.get_pinyin(key,'')
            fuzz_ratio=fuzz.ratio(sInput_py,key2_py)
            if fuzz_ratio>80:
                suggestedStr=suggestedStr+key+':'+str(fuzz_ratio)
                # mongodic[suggestedStr]=suggestedStr
                mongodic[key]=fuzz_ratio
                # print 'result:',key,fuzz_ratio
        return mongodic

    def result_form(self, result,category):
        domain = result.split(':')[0].decode('utf-8').encode('utf-8')
        oralname=result.split(':')[1]
        result_dic = {};label='';final_name='';profession=[];formatnames=set()
        if domain != 'FailCorrecting' and domain != 'FailDetecting':
            # scoreDocs_error = clients.query_utils(oralname)
            entityAql_error = 'For doc In entity Filter "%s" In doc.formatNames and doc.status == "active" RETURN doc' % (oralname)
            scoreDocs_error = db_arango.AQLQuery(entityAql_error, rawResults=True, batchSize=1000)

            for scoredoc in scoreDocs_error:
                formatName=scoredoc['formatName']
                formatnames.add(formatName)
                label=scoredoc['label']
                if 'profession_active' in scoredoc:
                    professionScore = scoredoc['profession_active']
                    for profes in professionScore:
                        if profes['score']>=0.2:
                            profession.append(profes['profession'])
            if len(formatnames)==1:
                for real in formatnames:
                    final_name=real
            else:final_name=oralname.decode('utf-8')

            if category != '':
                result_dic['category'] = category.split(':')[1]
            if label == 'film':
                result_dic['name']=final_name
            elif label == 'figure':
                if profession != None:
                    for line in profession:
                        result_dic[line] = final_name
                else:result_dic['actor'] = final_name
            elif label=='role':
                result_dic['role'] = final_name
        else:
            result_dic=''
        return result_dic

    def writeToMongo(self, result, mongodic):
        result_dic = {}
        name = result.split(':')[1].decode('utf-8').encode('utf-8')
        category = result.split(':')[0].decode('utf-8').encode('utf-8')
        if category != 'FailDetecting' and category != 'FailCorrecting' and category!='Unsupported':
            result_dic['category'] = result.split(':')[0].decode('utf-8').encode('utf-8')
            result_dic['correct_oralname'] = name
            result_dic['updateAt']=str(datetime.now())
            dicMerged = dict(result_dic, **mongodic)
            correct_db.insert(dicMerged)
        elif mongodic():
                result_dic['fail_reason']=category
                result_dic['updateAt']=str(datetime.now())
                dicMerged = dict(result_dic, **mongodic)
                wrong_db.insert(dicMerged)

