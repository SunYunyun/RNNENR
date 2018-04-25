#encoding:utf-8
import sys
sys.path.append("..")

import data_procesee
import datetime
import time
import logg

time_1 = time.time()

from nlu_predict import nlu as rnn_model
print 'load rnn'

import find_core_word
import label2command
import directo_actor
import utils_main
from num_process import find_name,numberTranform

from fuzzywuzzy import fuzz
from xpinyin import Pinyin
from collections import defaultdict
from pymongo import MongoClient
from collections import OrderedDict
# from datetime import datetime
from pyArango.connection import *

from config_database import config,clients

# p=Pinyin()
# mongoClient=MongoClient(host=config.mongo_path,port=config.mongo_port)
# db_mongo=mongoClient.MovieKnowledgeMap
# correct_db=db_mongo.error_logging
# wrong_db=db_mongo.error_fail
#
# def confusing_map(data):
#     confusing_dic=defaultdict(list)
#     for line in data:
#         if line!=None:
#             counti = 0
#             if len(line) >2:
#                 while counti <= len(line) - 2:
#                     two_grams = line[counti] + line[counti + 1]
#                     two_grams_py = p.get_pinyin(two_grams, '')
#                     if two_grams_py in confusing_dic:
#                         confusing_dic[two_grams_py].append(line)
#                     else:
#                         confusing_dic[two_grams_py] = [line, ]
#                     counti += 1
#             elif len(line) <= 2:
#                 line_py = p.get_pinyin(line.strip(), '')
#                 if line_py in confusing_dic:
#                     confusing_dic[line_py].append(line)
#                 else:
#                     confusing_dic[line_py] = [line, ]
#     return confusing_dic
#
# def get_videos():
#     video=set()
#     # conn = Connection(arangoURL=config.arrangoPath)
#     # db = conn[config.arrangoName]
#     # aql = 'For doc In entity Filter doc.label=="film" && doc.hot==true Return doc.formatNames'
#     # queryResult_video = db.AQLQuery(aql, rawResults=True, batchSize=20000)
#     queryResult_video = clients.ec_queryResult_video('film','doc.formatNames')
#     # conn.disconnectSession()
#
#     for key in queryResult_video:
#         for item in key:
#             video.add(item)
#     return video
#
# def get_hotcelebrity():
#     celerity_dataset = set()
#     hot_role=set()
#     # conn = Connection(arangoURL=config.arrangoPath)
#     # db = conn[config.arrangoName]
#     # aql = 'For doc In entity Filter doc.label=="figure" && doc.hot==true Return doc.formatNames'
#     # queryResult = db.AQLQuery(aql, rawResults=True, batchSize=3000)
#     queryResult = clients.ec_queryResult_video('figure','doc.formatNames')
#     # conn.disconnectSession()
#
#     for key in queryResult:
#         for item in key:
#             celerity_dataset.add(item)
#
#     # aql_role='For doc in entity filter doc.label=="film" && doc.hot==true return doc.roleNames'
#     # queryResult_role = db.AQLQuery(aql_role, rawResults=True, batchSize=20000)
#
#     queryResult_role = clients.ec_queryResult_video('film','doc.roleNames')
#
#     for key in queryResult_role:
#         if key!=None:
#             for item in key:
#                 hot_role.add(item)
#     return celerity_dataset,hot_role
#
# def update_data():
#     get_video = get_videos()
#     videos = confusing_map(get_video)
#     get_celebrity,get_role = get_hotcelebrity()
#     celebrity = confusing_map(get_celebrity)
#     hot_role=confusing_map(get_role)
#
#     return videos,celebrity,hot_role
#
# videos,celebrity,hot_role=update_data()

# class proofcheck:
#     def __init__(self,videos=videos,celebrity=celebrity,hot_role=hot_role):
#         self.videos=videos
#         self.celebrity=celebrity
#         self.hot_role=hot_role
#         pass
#
#     def proofreadAndSuggest(self, txt):
#         mongodic = {};mongodic2={}
#         mongodic['error_input'] = txt
#         sInput_py,categorys,flag_er,input_list = self.preprocess_prefix_suffix(txt)
#         mongodic['striped_py']=sInput_py
#         if input_list==[]:
#             if flag_er>0:
#                 result, mongodic2 = self.singular_match(txt, sInput_py)
#             elif flag_er==0 and len(txt)>=4:
#                 result, mongodic2 = self.singular_match(txt, sInput_py)
#             else:result='Unsupported'+':'+txt
#             merge_dic=dict(mongodic, **mongodic2)
#             final_result=self.result_form(result,categorys)
#             self.writeToMongo(result,merge_dic)
#             return final_result
#         else:
#             result1,mongodic_=self.singular_match(txt,input_list[0])
#             result2,mongodic1=self.singular_match(txt,input_list[1])
#             merge_dic1=dict(mongodic, **mongodic_)
#             merge_dic2=dict(mongodic, **mongodic1)
#             final_result1=dict(self.result_form(result1,categorys))
#             final_result2=dict(self.result_form(result2,categorys))
#
#             for k,v in final_result1.items():
#                 if k in final_result2.keys():
#                     final_result2[k]=v+','+final_result2[k]
#                 else:
#                     final_result2[k]=v
#             self.writeToMongo(result1,merge_dic1)
#             self.writeToMongo(result2, merge_dic2)
#             return final_result2
#
#
#     def preprocess_prefix_suffix(self, txt):
#         txt = txt.strip('集')
#         txt = txt.strip('季')
#         txt=txt.strip('恩')
#         txt=txt.strip('嗯')
#         flag_pre=0;flag_su=0
#         sInput_py = p.get_pinyin(txt, '')
#         sInput_py = ''.join(sInput_py)
#
#
#         categorys={u'电影':'dedianying dedianyingmei dedianmei dedianyoumei pianer dianyinga'
#                         'dedianyou zhuyandedianying yandedianying dianying pian pianzi'
#                         'canyudedianying deyingpian depian yingpian leidedianying dianyingban',
#                   u'电视剧': 'dedianshiju dianshiju yandedianshiju juji dianshilianxuju yingshi'
#                          'leidedianxing leidongman leijilupian leidedongman leidedianying riju hanju'
#                          'canyudedianshiju leideshenghuojiemu meiju yingju','综艺':'leizongyi leidezongyi zongyijiemu',
#                   u'动画':'dongman donghua donghuapian riman','体育':'tiyu tiyulei tiyujiemu','娱乐':'yule'
#                       }
#         category=''
#         for pre_key, pre_value in categorys.items():
#             for confusion_word in pre_value.split(' '):
#                 if sInput_py.find(''.join(confusion_word))!=-1:
#                     category='category:'+pre_key
#         prefix_dic = {
#             '我想看': 'tangxiaobai woxiangkan wokan woxiangkan enwoxiangkan woxiangkanhuo haoxiangkan woxiang woxiangkana '
#                    'woxiangkange mawoxiangkan geiwolaiyibu woxiangkanyi enwoxiangkan','给我': 'geiwo bangwo',
#             '我要看': 'woyaokan oyaokan woyaodian yaokan', '点播': 'dianbo jianbo yanbo chazhao',
#             '来一部': 'laiyibu souyib fangyibu','切换至': 'qiehuanzhi qiehuanzi qiehuandao',
#             '来一': 'laiyi laige kanyi', '播放': 'qingbofang bofang qingbo boqiu shoukan fangdianbo zhujiaoshi zhujiao',
#             '来': 'lai nai na laige naige','那我': 'nawo lawo', '检索': 'jiansuo jianshuo jiasuo jiashuo',
#             '有没有': 'youmeiyou youmei kanyikan baobao', '有': 'you kan jiebo',
#             '打开': 'dakai dakaiwode', '电视剧': 'dianshiju dianshi dianshilianxuju yingshi yingshi',
#             '电影': 'dianying pian yingpian','搜索': 'sousuo','调': 'tiao mv fang','搜': 'sou',
#             '集': "zuixinyi zuixin1 zuihouyi zuijinyi zuijin1",
#             '恩': 'you en gua', '类型': 'donghuapian donghua zongyi yingwenban yingyu'}
#
#         suffix_dic = {'来一部': 'laiyibu laiyi nayibu nayi', '有哪些': 'youna younaxie youlaxie youmeiyou',
#                       '有吗': 'youma youmei', '动画片': 'donghuapian donghuaban xijupian zongyijiemu',
#                       '电视剧': 'dianshiju juji dianshilianxuju', '的影视': 'deyingshi yingshi pianzi',
#                       '这部电影': 'zhebudianying zhebudian zhedianying zhedian zhepian nabudianying zhegedianying',
#                       '类的电视': 'leidedianxing leidongman leijilupian leidedongman leidedianying leizongyi leidezongyi '
#                               'leideshenghuojiemu','片儿': 'pianer depianer',
#                       '类型': 'zongyi donghua dianying dongman tiyujiemu mv',
#                       '的电影':'dedianying dedian deying dedianyingmei dedianyingma dedianyingyoumei dedianyou '
#                             'deying deyingpian depian yingpian leidedianying',
#                       '版本': 'guoyuban yingyuban guoyu yingyu gaoqingban languang gaoqing languangban nanguang '
#                             'nanguangban chaogaoqing quangaoqing quangaoqingban yingwenban neidiban daluban',
#                       '的电视剧': 'dedianshiju dianshiju yandedianshiju canyudedianshiju dejuji',
#                       '拍摄': 'paishe paide canyan canyu yan biaoyan canyan zhuyan hezuo',
#                       '结尾': 'dajieju diyi dier disan disi diwu diliu diqi diba dijiu dishi zuihouyi','没': 'haoba mei',
#                       "集":"zuixinyi zuixin1 zuihouyi zuijinyi zuijin1 zuixin2 zuixinliang ne dao pai"}
#         for pre_key, pre_value in prefix_dic.items():
#             for confusion_word in pre_value.split(' '):
#                 if sInput_py.startswith(''.join(confusion_word)) is True:
#                     sInput_py = sInput_py.replace(''.join(confusion_word), '')
#                     flag_pre=1
#
#         for suf_key, suf_value in suffix_dic.iteritems():
#             for con_word in suf_value.split(' '):
#                 if sInput_py.endswith(con_word) is True:
#                     sInput_py = sInput_py.replace(''.join(con_word), '')
#                     flag_su=2
#         flag_er=flag_pre+flag_su
#         input_py=[]
#         middle_dic={"演的":"zhuyande yande zuopeijiaode","参与":"canyude hezuo banyan canyu","拍摄":"paise daoyan zhizhuode"}
#         for mid_key,mid_value in middle_dic.items():
#             for mid_wrd in mid_value.split(' '):
#                 if sInput_py.find(''.join(mid_wrd))!=-1:
#                     sInput_py=sInput_py.replace(''.join(mid_wrd),'#')
#
#         if sInput_py.find('#')!=-1:
#             input_py.append(sInput_py.split('#')[0])
#             input_py.append(sInput_py.split('#')[1])
#         return sInput_py,category,flag_er,input_py
#
#     def get_celebrities(self, Word_Cut,confusion_data):
#         stop_words = 'woxiang xiangkan laiyibu youmeiy you mei ma chuan dianying de dianyou dedian woxiang woyao xiangkan' \
#                      'pindao xinwen dedian shiju deyingshi dianshi yingshi wode shijie diyi dier disan fusi dianbo'
#         suggest = set()
#         for word in Word_Cut:
#             word_ = p.get_pinyin(word, '')
#             word_str = ''.join(word_)
#             if stop_words.find(word_str) == -1:
#                 if word_str in confusion_data:
#                     if isinstance(confusion_data[word_str], unicode) is True:
#                         suggest.add(confusion_data[word_str])
#                     else:
#                         for list in confusion_data[word_str]:
#                             suggest.add(list)
#                 else:suggest.add('**')
#             else:suggest.add('**')
#         return suggest
#
#     def get_video(self, words):
#         stop_words = 'woxiang xiangkan yankan laiyi yibu youmei meiyou haoma dianying de dianyou dedian jiayi shouye shouji' \
#                      'woyao dianshi shiju dedian yaokan bofang jieju zuihou huaqian shoucang shipian bangzhu jixu zhuzhu jinji' \
#                      'me yingshi yingshi shuizhi dianbo guanzhi youmei sousuo yingxiong xiaoshi shijie bendan shichang boni ' \
#                      'shouye xiaozi zhufu xingxing guiying youzhi guanjun kuaiqian houhui haoxiao jieguo diyi yici yitian ' \
#                      'fangshi maopian fudao xuebao jiandao xiaoxiao haizi jiaren jiangui faxin liangshi guobao gaobie aima ' \
#                      'bangbang guiying dongzhu weiliao shenme buchang huizhuan bianshen tongyi jiangjie gufeng shijian jimu ' \
#                      'yande zhuyan canyu zhizuo paise sede daode danyan'
#         suggest = set()
#         for word in words:
#             word = word.strip('看')
#             word = word.strip('第')
#             word = word.strip('集')
#             word = word.strip('季')
#             # word = word.strip('的')
#             word_str = p.get_pinyin(word, '')
#             if stop_words.find(word_str) == -1 and len(word) > 1:
#                 if word_str in self.videos:
#                     if isinstance(self.videos[word_str], unicode):
#                         suggest.add(self.videos[word_str])
#                     else:
#                         for line in self.videos[word_str]:
#                             suggest.add(line)
#                 else:suggest.add('**')
#             else:suggest.add('**')
#         return suggest
#
#     def result_form(self, result,category):
#
#         domain = result.split(':')[0].decode('utf-8').encode('utf-8')
#         oralname=result.split(':')[1]
#         result_dic = {};label='';final_name='';profession=[];formatnames=set()
#         # conn = Connection(arangoURL=config.arrangoPath)
#         # db = conn[config.arrangoName]
#         # entityAql_error = 'For doc In entity Filter "%s" In doc.formatNames and doc.status == "active" RETURN doc' % (oralname)
#         # scoreDocs_error = db.AQLQuery(entityAql_error, rawResults=True, batchSize=1000)
#         scoreDocs_error = clients.query_utils(oralname)
#         # conn.disconnectSession()
#
#         for scoredoc in scoreDocs_error:
#             formatName=scoredoc['formatName']
#             formatnames.add(formatName)
#             label=scoredoc['label']
#             if 'profession' in scoredoc:
#                 for profes in scoredoc['profession']:
#                     profession.append(profes)
#         if len(formatnames)==1:
#             for real in formatnames:final_name=real
#         else:final_name=oralname
#         if domain!='FailCorrecting' and domain!='FailDetecting':
#             if category != '':
#                 result_dic['category'] = category.split(':')[1]
#             if label == 'film':
#                 result_dic['name']=final_name
#             elif label == 'figure':
#                 if profession != None:
#                     for line in profession:
#                         result_dic[line] = final_name
#                 else:result_dic['actor'] = final_name
#             elif label=='role':
#                 result_dic['role'] = final_name
#         else:
#             result_dic=''
#         return result_dic
#
#     def writeToMongo(self, result, mongodic):
#         result_dic = {}
#         name = result.split(':')[1].decode('utf-8').encode('utf-8')
#         category = result.split(':')[0].decode('utf-8').encode('utf-8')
#         if category != 'FailDetecting' and category != 'FailCorrecting' and category!='Unsupported':
#             result_dic['category'] = result.split(':')[0].decode('utf-8').encode('utf-8')
#             result_dic['correct_oralname'] = name
#             result_dic['updateAt']=str(datetime.datetime.now())
#             dicMerged = dict(result_dic, **mongodic)
#             correct_db.insert(dicMerged)
#         else:
#             if mongodic.has_key('suggestedmovies') or mongodic.has_key('suggestedcelebrities') \
#                     or mongodic.has_key('suggestedroles'):
#                 result_dic['fail_reason']=category
#                 result_dic['updateAt']=str(datetime.datetime.now())
#                 dicMerged = dict(result_dic, **mongodic)
#                 wrong_db.insert(dicMerged)
#
#     def singular_match(self, txt, sInput_py):
#             temp = [txt[i] + txt[i + 1] for i in range(0, len(txt) - 1)]
#
#             suggestlist_actor = self.get_celebrities(temp,self.celebrity)
#             mongodic = {}
#             mongodic['error_input'] = txt
#             suggestedcelebrities = ''
#             tempdic_ac = OrderedDict()
#             for right_actorname in suggestlist_actor:
#                 actorname_key = right_actorname
#                 key2_py = p.get_pinyin(actorname_key, '')
#                 fuzz_ratio2 = fuzz.ratio(sInput_py, ''.join(key2_py))
#                 if fuzz_ratio2 > 70:
#                     suggestedcelebrities = suggestedcelebrities + actorname_key + ':' + str(fuzz_ratio2) + ' '
#                     mongodic['suggestedcelebrities'] = suggestedcelebrities
#                 if fuzz_ratio2 >=96:
#                     result = 'figure:' + actorname_key
#                     mongodic['highest_score']=actorname_key+':'+str(fuzz_ratio2)
#                     return result, mongodic
#                 elif 90 < fuzz_ratio2 <= 95:
#                     tempdic_ac[actorname_key] = fuzz_ratio2
#             if tempdic_ac:
#                 value1, key1 = list(sorted(tempdic_ac.values())), list(sorted(tempdic_ac.keys()))
#                 actor_name = key1[value1.index(max(value1))]
#                 result = 'figure:' + actor_name
#                 mongodic['highest_score'] = actor_name + ':' + str(max(value1))
#                 return result, mongodic
#
#             suggestmovies = '';suggestlist_movie = self.get_video(temp);tempdic =OrderedDict()
#
#             for moviename in suggestlist_movie:
#                 movie_name_key = moviename
#                 key1_py = fuzz._process_and_sort(''.join(p.get_pinyin(movie_name_key, '')), force_ascii=True)
#                 sInput_py = fuzz._process_and_sort(sInput_py, force_ascii=True)
#                 fuzz_ratio1 = fuzz.ratio(sInput_py, ''.join(key1_py))
#                 if fuzz_ratio1 >= 70:
#                     suggestmovies = suggestmovies + movie_name_key + ':' + str(fuzz_ratio1) + ' '
#                     mongodic['suggestedmovies'] = suggestmovies
#                 if fuzz_ratio1 >= 96:
#                     result = 'video:' + movie_name_key
#                     mongodic['highest_score']=movie_name_key+':'+str(fuzz_ratio1)
#                     return result, mongodic
#                 elif 84<= fuzz_ratio1 < 96:
#                     tempdic[movie_name_key] = fuzz_ratio1
#             if tempdic:
#                 value1, key1 = list(tempdic.values()), list(tempdic.keys())
#                 movie_name = key1[value1.index(max(value1))]
#                 result = 'video:' + movie_name
#                 mongodic['highest_score']=movie_name+':'+str(max(value1))
#                 return result, mongodic
#             suggestroles='';suggerslit_hotrole=self.get_celebrities(temp,self.hot_role)
#             for role_name in suggerslit_hotrole:
#                 key3_py = fuzz._process_and_sort(''.join(p.get_pinyin(role_name, '')), force_ascii=True)
#                 sInput_py = fuzz._process_and_sort(sInput_py, force_ascii=True)
#                 fuzz_ratio3 = fuzz.ratio(sInput_py, ''.join(key3_py))
#                 if fuzz_ratio3 >= 70:
#                     suggestroles = suggestroles + role_name + ':' + str(fuzz_ratio3) + ' '
#                     mongodic['suggestedroles'] = suggestroles
#                 if fuzz_ratio3 >= 96:
#                     result = 'role:' + role_name
#                     mongodic['highest_score']=role_name+':'+str(fuzz_ratio3)
#                     return result, mongodic
#                 elif 90< fuzz_ratio3 < 96:
#                     tempdic[role_name] = fuzz_ratio3
#             if tempdic:
#                 value1, key1 = list(tempdic.values()), list(tempdic.keys())
#                 rolename = key1[value1.index(max(value1))]
#                 result = 'role:' + rolename
#                 mongodic['highest_score']=rolename+':'+str(max(value1))
#                 return result, mongodic
#             else:
#                 result = 'FailCorrecting:' + txt
#                 return result, mongodic

'''
RNN_LSTM
'''
import re
import extra as EX

# target = proofcheck()

class rnnIntent(object):

    def __init__(self,command,swith='r'):

        self.command = command
        self.jsonStr={}
        self.neural=''

        fouth_actor_ = directo_actor.dd
        relation_ = directo_actor.relation
        relation__alis = directo_actor.relation_alias
        sub_award_contain_year = directo_actor.sub_award_contain_year
        try:
            self.verfiy(self.command,fouth_actor=fouth_actor_,
                        relation=relation_,relation_alis=relation__alis,
                        sub_award_contain_year=sub_award_contain_year)
        except (IOError ,ZeroDivisionError),e:
            logg.DEBUG(e)
            pass

    def domain_function(self,i_):
        domain = find_core_word.Domain(i_)
        domain_score = domain.get_value()
        return domain_score

    def verfiy_result(self,reslut):

        if reslut:
            if 'episode' in reslut and 'name' not in reslut:
                reslut.pop('episode')
            if 'season' in reslut and 'name' not in reslut:
                reslut.pop('season')
            return reslut

    def relation_search(self,reslut):

        if reslut:
            pname =''
            if 'relative' in reslut:
                rel = reslut['relative']
                if rel in directo_actor.relation_alias.keys():
                    rel = directo_actor.relation_alias[rel]
                    reslut['relative']=rel
                if 'actor' in reslut:
                    pname = reslut['actor']
                elif 'director' in reslut:
                    pname = reslut['director']
                elif 'dubbing' in reslut:
                    pname = reslut['dubbing']

                _, _, relName = data_procesee.getRelation(name=pname,relation=rel)
                if relName!=[]:
                    if 'actor' in reslut :reslut.pop('actor')
                    if 'director'in reslut : reslut.pop('director')
                    if 'dubbing' in reslut : reslut.pop('dubbing')
                    if 'relative' in reslut :reslut.pop('relative')

                if len(relName) is 1:
                    reslut['actor'] = relName[0].decode('utf-8').encode('utf-8')
                elif len(relName)>1:
                    relName['actor'] = ','.join(relName).decode('utf-8').encode('utf-8')
            return  reslut
        else: return reslut

    def verify_area(self,reslut):

        if reslut:
            if 'area' in reslut:
                value = reslut['area']
                if value in directo_actor._area_:
                    reslut['area'] = directo_actor._area_[value]
            if 'type' in reslut:
                value = reslut['type']
                if value in directo_actor._tag_:
                    reslut['type']=directo_actor._tag_[value]

            if 'category' in reslut and 'name' in reslut:
                cvalue = reslut['category']
                nvalue = reslut['name']
                if nvalue  is  cvalue:
                    reslut.pop('name')
                elif cvalue in nvalue:
                    reslut.pop('category')
            return reslut
        else: return reslut

    def verfiy_data(self, data):#20171218 d s
        '''

        :param data:
        :return:
        '''
        if len(data['data']['semantic']) == 1:
            tt = ['episode', 'season', 'year', 'language', 'relative', 'rate', 'extra', 'award', 'sub_award',
                  'resolution',"publisher",'tag'
                  'playTime', 'moviePlayDuration', 'type', 'area']
            for i in tt:
                if i in data["data"]['semantic']:
                    data = {}
                    break
        return data

    def verfiy_dataKG(self, data):#20171226 d s
        '''

        :param data:
        :return:
        '''
        if len(data['data']['semantic']) == 1:
            tt = ['episode', 'season', 'year', 'language', 'relative', 'rate', 'extra', 'award', 'sub_award',
                  'resolution','publisher',
                  'playTime', 'moviePlayDuration', 'area','tag']
            for i in tt:
                if i in data["data"]['semantic']:
                    data = {}
                    break
        return data

    def in_out(self,str):
        flag=1
        for _name in  directo_actor._nameContaincategory_ :
            if _name in str:
                flag = 0
                break
        return flag

    def reasonableness_test(self,reslut):

        if reslut:

            if 'season' in reslut or 'episode' in reslut :
                if 'name' not in reslut and 'role' not in reslut:# --20171215 d
                    reslut={}
            elif 'relation_person' in reslut:  # --20171214 s
                if 'actor' not in reslut and 'director' not in reslut:
                    reslut = {}# --20171214 s

            return reslut
        else:return reslut

    def verify_year_rate(self,reslut):
        if reslut:
            if 'year' in reslut:
                if type(reslut['year']) is int and (reslut['year']<10 or reslut['year']>2030):
                        reslut.pop('year')
            if 'rate' in reslut:
                if reslut['rate']>10 or reslut['rate']<1:
                    reslut.pop('rate')
            if 'season' in reslut:
                if reslut['season']>20:
                    reslut={}
            return reslut
        return reslut

    def verfy_actor_name(self,reslut):
        if reslut:
            if 'name' in reslut and 'actor' in reslut:
                name = reslut['name']
                if ',' in name:
                    name = name.split(',')
                    actor = reslut['actor']
                    r = [i for i in name if i != actor]
                    reslut['name'] = ''.join(r)
            return reslut
        return reslut

    def find_session_epsiod(self,string):
        if type(string)  is  str:
            string = string.decode("utf-8")
        else:
            string = string
        data_result, session, esipod, string = find_name(string)
        return data_result, session.decode('utf-8').encode('utf-8'), esipod.decode('utf-8').encode('utf-8'), string.decode('utf-8').encode('utf-8')

    def verfiy_ban(self,src):
        key_=''
        value_=''
        for value,key in directo_actor._language_.iteritems():
            if value in src:
                value_=value
                key_ = key
                break
        src = src.replace(value_,'')
        return 'language',key_,src

    def verfiy_role(self, reslut):#20171215
        if reslut:

            if 'episode' in reslut and 'role' not in reslut and 'name' not in reslut:
                reslut.pop('episode')
            if 'season' in reslut and 'role' not in reslut and 'name' not in reslut:
                reslut.pop('season')
            return reslut

    def verfiy_ec(self,rnn,ec):
        ec_num={'1':'一','2':'二','3':'三','4':'四','5':'五','6':'六','7':'七','8':'八','9':'九','-1':'千','10':'十'}
        for i in ['season','episode']:
            nf = 0
            if i in rnn:
                if str(rnn[i]) in ec_num.keys():
                    n = ec_num[str(rnn[i])]
                    for j in ['name','actor','role']:
                        if j in ec and n in ec[j]:
                            if ec[j].decode('utf-8')[-1]  ==  n: #20171227 d
                                rnn.pop('season')
                                nf = 1
                            # elif ec[j].decode('utf-8')[-2:]  ==  n+u'部': #20171227 d
                            elif n + u'部' in ec[j].decode('utf-8') :  # 20171227 d
                                rnn.pop('season')
                                nf = 1
                                break
            if nf:
                break
        return rnn

    def verfiy(self,buf,fouth_actor,relation,relation_alis,sub_award_contain_year):

        ti = time.time()
        i_ = buf.rstrip().decode('utf-8').encode('utf-8')
        src_txt = i_
        i_ = i_.replace('+', '').replace('-', '').replace('*', '').replace('+', '').replace('×', '').replace('-','')\
            .replace('//', '').replace('×','').replace(' ','').replace('[','').replace(']','').replace('（','')\
            .replace('）','').replace('·','').replace('`','').replace('<','').replace('%','')

        allflag = 1

        if i_.replace(' ','').isdigit() and len(i_.replace(' ',''))>5:
            allflag = -1

        command = ['我要看']#--20171215 d
        for i in command:
            ss = i_.count(i)
            if ss == 2:
                list1 = i_.strip().split(i)
                list1.remove('')
                i_ = i + list1[1]
            else:
                pass #--20171215 d

        ex = ['来一集', '来一季', '来一期', '来一部','瞅一眼','看一集']
        for i in ex:
            if i in i_:
                i_ = i_.replace(i, '我想看')
            else:
                i_ = i_

        data = {}
        lstmresult = {}
        info = {}
        seman_data = {}
        session_espiod = {}

        if i_ in ['一键观影','umax','深度优化','金鹰卡通','播放一下','放一下','我想看一下','模拟电视','全局搜索','换到视频','切换到视频','视频',"模拟电视","换到视频","切换到视频","视频","视频源",
                 "高清","高清源","换到高清","换到高清源","切换到高清","切换到高清源","劲爆体育","切换到劲爆体育","打开劲爆体育","一键观影","切换到一键观影","设置一键观影",
                "打开一键观影","切换到NBATV","切换到FASHIONTV","切换到FashionTV","切换到星空体育","切换到SITV点播影院","切换到SiTV点播影院","切换到上海台"]:
            allflag=-1
        wen = ['声音调到','音量','亮度调到','快进到','加','减','乘','除','等于']#20171226 d
        for ii in wen:
            if ii in i_:
                allflag = -1
                break
        if re.findall(u"[0-9a-zA-Z]",i_):#20171227 d
            ss = re.findall(u"[0-9a-zA-Z]+", i_)
            ss_  = ''
            for i in ss:
                ss_ = ss_ + i
            if len(ss)==1 and len(ss[0]) == len(i_) and len(i_)<=3 :
                allflag = -1
            elif len(ss_)>8:
                allflag = -1

        for i in directo_actor.man_country:
            if i in i_:
                info['area'] = directo_actor.man_country[i]

        domain_final = self.domain_function(i_)

        if domain_final != 'NULL':
            if '英文原声版' in i_:
                extra_, result_ = '英文原声版',i_.replace('英文原声版','')
            else:
                extra_, result_ = EX.find_num(i_)
            if extra_  is '4k' or extra_ is '4K':
                info['resolution']='4k'
                i_ = result_
            elif extra_:
                info['extra']=extra_
                i_ = result_
            else:
                if allflag !=-1:
                    allflag=0
        l,lk,i_ = self.verfiy_ban(i_)
        if lk:
            info[l] = lk
        esi_flag=0
        if '最后一集' in i_:
            i_ = i_.replace('最后一集', '')
            session_espiod['episode'] = -1
        if allflag!=-1:
            _,ses, esi, si = self.find_session_epsiod(i_ )
            partflag=1
            if '部' in ses and '第'not in ses and '最近' not in ses and '最新' not in ses and '最后' not in ses and esi=='':
                partflag=0
            if ses in ['部','季'] and esi=='':
                partflag = 0
            if si != i_ and partflag :
            # if si != i_ :#20171225 d
                i_ = si
                if ses in directo_actor._season_num_:
                    session_espiod['season'] = directo_actor._season_num_[ses]
                else:
                    if ses:
                        ses_ = data_procesee.find_num_str_unicode(ses)
                        if ses_ and ses_ != 1000000000:
                            if ses_>999 or ses_<-999 :
                                if len(str(ses_))!=8 :
                                    ses = -1
                                else: ses = ses_
                            else:ses = ses_
                            session_espiod['season'] = ses
                if esi:
                    esi_ = data_procesee.find_num_str_unicode(esi)
                    if esi_ and esi_ != 1000000000:
                        if (esi_>999 or esi_<-999) :
                            if len(str(esi_))!=8:
                                esi = -1
                            else:esi = esi_
                        else:esi = esi_
                        if esi_flag:
                            esi = -1*esi
                        session_espiod['episode'] = esi
        # print '941',session_espiod

        if domain_final !='NULL'and not re.findall(r'.*第.*(季|集|部)', i_) and allflag!=-1:
            if '大结局' in i_:
                session_espiod['episode']=-1
                if i_[i_.index('大结局')-3:i_.index('大结局')] is '的':
                    i_ = i_[:i_.index('大结局')-3]
                else:
                    i_ = i_[:i_.index('大结局')]

            i_ = i_.replace('电视连续剧','').replace('这部电视剧','').replace('电视剧','').replace('长虹小白','')
            name_only,name_semantic,full,item = find_core_word.nameOnly(command=numberTranform(i_).decode('utf-8').encode('utf-8'), corefindFlag=1,
                                                                   searcherEngine='',
                                                                   searchItem1='formatName', searchItem2='formatNames',get_words='label'
                                                                ).postproces()#searcherEngine=searcher_all

            if item:
                name_semantic = self.reasonableness_test(name_semantic)
                if name_semantic:
                    seman_data['src_txt']=src_txt
                    # if domain_final:
                    if 'appname' in name_semantic or 'station' in name_semantic or 'radio' in name_semantic :
                        lstmresult = {}
                        allflag = 2
                    else:
                        if 'name' in name_semantic and self.in_out(name_semantic['name']) and domain_final:
                            name_semantic['category']=domain_final
                        elif 'name' not in name_semantic and domain_final:
                            name_semantic['category'] = domain_final
                        seman_data['domain']='VIDEO'
                        if 'extra' in info and 'name' in name_semantic:
                            if info['extra'] not in name_semantic['name']:
                                name_semantic['name'] = "%s%s" % (name_semantic['name'], info['extra'])
                                info.pop('extra')
                        elif 'extra' in info and 'name' not in name_semantic:
                            name_semantic['extra'] = info['extra']
                            info.pop('extra')

                        if info:
                            name_semantic = dict(name_semantic,**info)
                        if 'scene' in name_semantic:#20171226 s
                            name_semantic.pop('scene')
                        if 'resolution' in info:
                            name_semantic['resolution'] = info['resolution']

                        if session_espiod and ('season' not in name_semantic or 'episode' not in name_semantic):
                            if session_espiod:
                                session_espiod = self.verfiy_ec(session_espiod, name_semantic)
                            name_semantic = dict(name_semantic,**session_espiod)
                            name_semantic = self.reasonableness_test(name_semantic)
                        if not name_semantic:
                            allflag=0
                        else:
                            seman_data['semantic'] = name_semantic
                            seman_data = dict(seman_data,**name_only)
                            data['data'] = seman_data
                            data['flag'] = 1
                            data['code'] = 200
                            allflag=1
                else:allflag=0
            else:allflag=0
#rnn
        if domain_final !='NULL'and re.findall(r'.*第.*(季|集|部)', i_) or allflag is 0:

            i_ = data_procesee.check_char(i_)


            if isinstance(i_, unicode):
                i_ ,_i= data_procesee.character_separation_unicon(i_)
            elif isinstance(i_, str):
                i_ ,_i= data_procesee.character_separation(i_)



            if i_.find('电 影')!=-1 or i_.find('影 片')!=-1:
                seman_data['domain'] = 'VIDEO';seman_data['intent'] = 'QUERY'

            elif i_.find('片') != -1 :
                # info['category'] = '电影'#20171214
                seman_data['domain'] = 'VIDEO';seman_data['intent'] = 'QUERY'
            elif i_.find('看')!=-1:
                seman_data['domain'] = 'VIDEO';seman_data['intent'] = 'QUERY'

            if i_.find('剧') !=-1 :
                info['category']='电视剧'

            if 'category' not in info and domain_final:
                info['category'] = domain_final
            # print i_
            predictions_test =  rnn_model.rec(i_.replace(' ',''))

            s_ = ' '.join(predictions_test)
            # print 'RNN', s_
            self.neural = s_

            logg.DEBUG(self.neural,'recurrent network prediction')
            if _i is '':
                _i = i_
            cmd = label2command.lbel2command(_i.split(' '), predictions_test)

            searcher_flag=0
            for key,value in cmd.iteritems():
                if value  is  '':
                    continue
                elif key in ['playTime']:
                    # info[key]=value
                    continue #2017-12-19
                elif key in ['moviePlayDuration']:#2017-12-19
                    # info[key]=value
                    continue  # 2017-12-19
                elif value in directo_actor.area_tvPlay:
                    info['area'] = directo_actor.area_tvPlay[value]
                    if 'category' not in info:
                        info['category'] = '电视剧'
                elif key is 'season' or key  is  'episode':
                    if value in directo_actor._part_:
                        value = directo_actor._part_[value]
                    else:
                        sesson_s = data_procesee.find_num_str_unicode(value)
                        if sesson_s and sesson_s!=1000000000:
                            value = sesson_s
                        else:
                            continue
                    info[key] = value
                elif key  is 'relative' and value in relation:#directo_actor.relation
                    info['relative']=value
                elif key  is  'award' and value:
                    many_value = value.split(',')
                    for iv in many_value:
                        tm_ = ''; tmvalue_ = ''
                        ftmp = utils_main.Multi_character_star(origal=i_, command=iv.decode('utf-8').encode('utf-8'),
                                                               manyFlag=0, searcherEngine='',TermQuery='',Term='',
                                                               relation=relation,
                                                               relation_alis=relation_alis).final#searcherEngine=searcher_all
                        elseflag=1
                        if ftmp:
                            ftmp_key = ftmp.keys()
                            for ti_, tv_ in ftmp.iteritems():
                                if ti_  is  'film' and tv_  is  '奥斯卡' and key  is  'award':
                                    tm_ = 'award'
                                    tmvalue_ = '奥斯卡金像奖'
                                elif ti_  is  'sub_award' and tv_.find('奖')  is  -1 and tv_.find('角')  is  -1:
                                    tm_ = 'sub_award'
                                    tmvalue_ = tv_
                                elif 'actor' in ftmp_key or 'director' in ftmp_key or 'writer' in ftmp_key or 'dubbing' in ftmp_key:
                                    info = dict(info, **ftmp)
                                    elseflag = 0
                                    break
                                else:
                                    tm_ = ti_
                                    tmvalue_ = tv_
                            cflag = 1
                            if elseflag:
                                if tm_  is  'category' and tm_ not in info:
                                    cflag = 0
                                    info[tm_] = tmvalue_
                                if cflag:
                                    if tm_ and tmvalue_ and tm_ not in info:
                                        info[tm_] = tmvalue_
                                    elif tm_ and tmvalue_:
                                        if tm_ != 'category': info[tm_] = info[tm_] + ',' + tmvalue_
                        else:
                            searcher_flag=1
                            break
                elif value and key!='actor' and key!='videoName' and key!='area':
                    if key  is 'type' :
                        if value in ['德甲类','生活']:
                            info['type']=value
                            continue
                        elif value in ['评分高','评价高']:
                            info['tag'] = '高分'
                            continue
                        elif value in ['抗日战争']:#20171121
                            info['type'] = '战争'
                            continue

                    if value in sub_award_contain_year:
                        info['sub_awrad']=value
                        continue
                    if key  is  'year' and value in ['最近','最新','今年']:
                        info['year']=datetime.datetime.now().year
                        continue
                    if value in directo_actor.award_contain_year:
                        info['awrad']=value
                        continue
                    if key  is  'language' and value in directo_actor._language_.keys():
                        info['language'] = directo_actor._language_[value]
                        continue
                    tf,_value = data_procesee.verfy_num(key,value)
                    if not tf and not _value:
                        many_value = value.split(',')
                        for iv in many_value:
                            __tf, __value = data_procesee.verfy_num(key, iv)
                            if __value and __tf:
                                info[__tf]=__value
                                continue
                            if iv in ['纪录']:
                                continue
                            tm_ = '';tmvalue_ = ''
                            if key is 'award' and len(iv)<4:
                                continue
                            ftmp = utils_main.Multi_character_star(origal=i_, command=iv.decode('utf-8').encode('utf-8'),
                                                               manyFlag=0, searcherEngine='',TermQuery='',Term='',
                                                               relation=relation,relation_alis=relation_alis).final
                            elseflag=1
                            if ftmp:
                                ftmp_key = ftmp.keys()
                                if key in ftmp_key:
                                    tm_ = key
                                    tmvalue_ = ftmp[key].decode('utf-8').encode('utf-8')
                                    # tmvalue_ = iv.decode('utf-8').encode('utf-8')
                                elif key  is  'award' and 'sub_award' in ftmp_key:
                                    tm_ = 'sub_award'
                                    tmvalue_ = ftmp['sub_award'].decode('utf-8').encode('utf-8')
                                else:
                                    for ti_ ,tv_ in ftmp.iteritems():
                                        if ti_ is 'film' and tv_  is '奥斯卡' and key  is  'award':
                                            tm_ ='award'
                                            tmvalue_='奥斯卡金像奖'
                                        elif ti_  is 'sub_award' and tv_.find('奖') is -1 and tv_.find('角') is -1:
                                            tm_='sub_award'
                                            tmvalue_ = tv_
                                        elif 'actor' in ftmp_key or 'director' in ftmp_key or 'writer' in ftmp_key or 'dubbing'in ftmp_key:
                                            info = dict(info,**ftmp)
                                            elseflag=0
                                            break
                                        else:
                                            tm_ = ti_
                                            tmvalue_ = tv_
                            else:
                                searcher_flag=1
                                break
                            cflag=1
                            if elseflag:
                                if tm_  is 'category' and tm_ not in info:
                                    cflag=0
                                    info[tm_] = tmvalue_
                                if cflag:
                                    if tm_ and tmvalue_ and tm_ not in info:
                                            info[tm_]=tmvalue_
                                    elif tm_ and tmvalue_ :
                                        if tm_!='category':info[tm_] = info[tm_]+','+tmvalue_

                    else:info[tf]=_value
                elif key is 'area':
                    if value in directo_actor.single_conutry:
                        info['area']= directo_actor.single_conutry[value]
                        continue
                    elif value in directo_actor._area_:
                        info['area'] = directo_actor._area_[value]
                        continue
                    many_value = value.split(',')
                    if len(many_value)!=1:
                        ftmp = utils_main.Multi_character_star(origal=i_, command=''.join(many_value).decode('utf-8').encode('utf-8'),
                                                               manyFlag=0, searcherEngine='',TermQuery='',Term='',
                                                               relation=relation,relation_alis=relation_alis).final
                        if ftmp:
                            if 'area' in ftmp:
                                info['area']=''.join(many_value)
                            else: info = dict(info,**ftmp)
                        else:
                            for ai in many_value:
                                ftmp = utils_main.Multi_character_star(origal=i_, command=ai.decode(
                                    'utf-8').encode('utf-8'), manyFlag=0, searcherEngine='',TermQuery='',Term='',
                                    relation=relation,relation_alis=relation_alis).final
                                if ftmp:
                                    if 'area' in info:
                                        info['area']=info['area']+','+ai
                                    else:info['area']=ai
                                else:
                                    searcher_flag=1
                                    break
                    else:
                        if len(many_value[0])>3:
                            ftmp = utils_main.Multi_character_star(origal=i_,
                                                                   command=many_value[0].decode('utf-8').encode(
                                                                       'utf-8'),
                                                                   manyFlag=0, searcherEngine='',TermQuery='',Term='',
                                                                   relation=relation,relation_alis=relation_alis).final
                            if ftmp:
                                if 'type' in ftmp:
                                    info['type'] = many_value[0]
                                elif 'area' not in ftmp:
                                    info = dict(info,**ftmp)
                                else:
                                    info['area'] = many_value[0]
                            else:
                                searcher_flag=1
                                break

                elif (key  is  'actor' and len(value) > 10):
                    # 多明星处理方式
                    if value not in fouth_actor:

                        many_value = value.split(',')
                        four_actor = [];
                        single_actors = []

                        for i in many_value:
                            if len(i) > 10:
                                four_actor.append(i)

                            else:
                                single_actors.append(i)

                        for one in four_actor:
                            if re.findall(ur'[0-9]+',one):
                                searcher_flag = 1
                                break
                            _ftmp = utils_main.Multi_character_star(origal=i_,
                                                                   command=one.decode('utf-8').encode('utf-8'),
                                                                   manyFlag=1,searcherEngine='',TermQuery='',Term='',
                                                                   relation=relation,relation_alis=relation_alis)
                            ftmp =_ftmp.actors
                            ftmp_ = _ftmp.relation_ship
                            if ftmp:
                                for vvi in ftmp:
                                    tmpvalue = vvi.replace('·','').replace('.','')
                                    if ftmp_:
                                        single_actors.append(tmpvalue)
                                        break
                                    else:
                                        value = value.replace(tmpvalue,'')
                                        if not value or len(value)<=len(tmpvalue):
                                            single_actors.append(tmpvalue)
                                        else:searcher_flag=1
                            else:
                                searcher_flag=1
                            if ftmp_:
                                info = dict(info,**ftmp_)

                        single_actor_set = {}

                        for one in single_actors:
                            ftmp = utils_main.Multi_character_star(origal=i_,
                                                                   command=one.decode('utf-8').encode('utf-8'),
                                                                   manyFlag=0, searcherEngine='',TermQuery='',Term='',
                                                                   relation=relation,relation_alis=relation_alis).final
                            if ftmp:
                                for ky, vu in ftmp.iteritems():
                                    if ky in ['appname','station']:
                                        allflag = 2
                                        searcher_flag = 1
                                        break
                                    if ky in single_actor_set:
                                        if single_actor_set[ky] != vu:
                                            single_actor_set[ky] = single_actor_set[ky] + ',' + vu
                                    else:
                                        single_actor_set[ky] = vu
                            else:
                                searcher_flag=1
                                break

                        if single_actor_set:
                            info = dict(info, **single_actor_set)
                        else:
                            lstmresult['flag'] = 0
                    else:
                        info[key] = value

                elif (key  is  'actor' and len(value)<10):
                    ftmp = utils_main.Multi_character_star(origal=i_,command=value.decode('utf-8').encode('utf-8'),manyFlag=0, searcherEngine='',TermQuery='',Term=''
,                                                           relation=relation,relation_alis=relation_alis).final
                    if ftmp:
                        if 'station' in ftmp.keys() or 'appname' in ftmp.keys():
                            searcher_flag = 1
                            allflag = 2
                            lstmresult['flag'] = 0
                            break
                        for fk,fv in ftmp.iteritems():
                            if fk in info:
                                info[fk] = info[fk]+','+fv
                            else:info[fk]=fv
                    else:
                        searcher_flag = 1
                        lstmresult['flag']=0
                        break

                elif key  is  'videoName':
                    value = numberTranform(value).decode('utf-8').encode('utf-8')
                    nameonly, name_semantic, full,item = find_core_word.nameOnly(command=value, corefindFlag=0,
                                                                             searcherEngine='',
                                                                             searchItem1='formatName',
                                                                             searchItem2='formatNames',
                                                                             get_words='label'
                                                                             ).postproces()
                    if item:
                        if item in ['appname','station','scene']:#add scene 20171226
                            searcher_flag = 1
                            allflag = 2
                            lstmresult['flag'] = 0
                            break
                        elif item  is  'film':
                            item = 'name'
                            info[item] = name_semantic[item]
                        else:
                            for vki_,vkv_ in name_semantic.iteritems():
                                if vki_ in ['appname' , 'station' , 'radio']:
                                    allflag = 2
                                    continue
                                info[vki_] = vkv_
                    else:
                        searcher_flag=1
                        lstmresult['flag'] = 0
                        break

                elif key  is  'directorName':
                    ftmp = utils_main.Multi_character_star(origal=i_,command=value.decode('utf-8').encode('utf-8'),
                                                           manyFlag=0, searcherEngine='',TermQuery='',Term='',
                                                           relation=relation,relation_alis=relation_alis).final#searcher_all
                    if ftmp:
                        info = dict(info, **ftmp)
                    else:
                        lstmresult['flag'] = 0
                else:
                    info[key] = value

            if searcher_flag :
                if 'name' in info:
                    info.pop('name')
            if 'relation_person' in info:
                info['relative'] = info['relation_person']
                info.pop('relation_person')

            if 'relative' in info :#20171214 s
                if 'actor' not in info and 'director' not in info:
                    info = {}
            # if "moviePlayDuration" in info:#20171214 s
                # if 'type' not in info and 'category' not in info:
                #     info = {}
                # pass

            info = self.verfiy_result(info)
            info = self.relation_search(info)
            info = self.verify_area(info)
            info = self.verfy_actor_name(info)
            info = self.verify_year_rate(info)

            if info and ('season' not in info or 'episode' not in info):
                info = dict(info, **session_espiod)
            info = self.verfiy_role(info)#--20171215 d

            info = self.reasonableness_test(info)

            if searcher_flag:
                lstmresult={}
            else:
                if info:
                    if 'appname' in info or 'station' in info or 'radio' in info:
                        allflag = 2
                        lstmresult = {}
                    else:
                        _info={}
                        for __ ,_v_ in info.iteritems():
                            if data_procesee.is_chinese(_v_) and len(_v_)<4 and __ in ['type','area']:
                               continue
                            _info[__] = _v_
                        if _info:
                            seman_data['semantic'] = _info
                        seman_data['domain']="VIDEO"
                        seman_data['intent']="QUERY"
                        seman_data['src_txt']=src_txt
                        lstmresult['data'] = seman_data
                        lstmresult['flag']=1;lstmresult['code']=200
        #print session_espiod
        final={}
        if data:
            final = self.verfiy_dataKG(data)#20171226 s
            # print 'lucene'
        elif lstmresult:
            final = self.verfiy_data(lstmresult)
            # print 'lstm'
        else:
            # print 'jiucuo'
            # if allflag != 2
            final['flag']=0;final['code']=201

        s=''
        self.jsonStr = json.dumps(final,ensure_ascii=False)
        ti1 = time.time()
        logg.DEBUG('%s %s %s %s'%(self.jsonStr,str((ti1 - ti)*1000),ti,ti1))

        # print self.jsonStr

        if s  is '':
            s = 'Sorry, I didn\'t hear clearly, please repeat again'
        s = s+'<br>'+' '+'<br>'+'亲，目前我只会 视频\电视台 相关的哟，不要淘气哟~~~'


if __name__  ==  '__main__':
   k =  rnnIntent('')
   print k.jsonStr
   # import profile
   #
   # profile.run("rnnIntent.verfiy")