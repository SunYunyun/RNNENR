#encoding:utf-8
import sys
sys.path.append("..")

import data_procesee
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

from config_database import config,clients
import trie_bys_getname

import error_configRedis as ecR
ecR.ec_init()

from fuzzywuzzy import fuzz
from xpinyin import Pinyin
from pymongo import MongoClient
from collections import OrderedDict
from datetime import datetime
from pyArango.connection import *
import redis

pinyin=Pinyin()
#190mongo
mongoClient=MongoClient(host=config.mongo_path,port=config.mongo_port)
db_mongo=mongoClient.MovieKnowledgeMap

#153mongo
# mongoClient=MongoClient(host='10.66.1.153',port=80,)
# db_mongo=mongoClient.semantic_normal
# db_mongo.authenticate(name='semanticNormalUser',password='semanticAdminUser20180118')

correct_db=db_mongo.error_logging
wrong_db=db_mongo.error_fail

#12
# conn=Connection(arangoURL = '10.66.1.133：8529')
# db=conn['SEMANTIC_KG']

conn=Connection(arangoURL = config.arrangoPath,username='tester',password=123456)
# conn=Connection(arangoURL = config.arrangoPath)

db=conn['knowledge-graph-test']
#connect redis
conR=redis.Redis(host=config.redis_ip,port=config.redis_port,db=config.redis_db_ec)

class proofcheck:
    def proofreadAndSuggest(self, txt):
        mongodic = {};mongodic2={}
        mongodic['error_input'] = txt
        sInput_py,categorys,flag_er,input_list = self.preprocess_prefix_suffix(txt)
        mongodic['striped_py']=sInput_py
        if input_list==[]:
#here is a flag to test whether the length of input is longer than 4 letters
            if flag_er>0:
                result, mongodic2 = self.singular_match(txt, sInput_py)
            elif flag_er==0 and len(txt)>=4:
                result, mongodic2 = self.singular_match(txt, sInput_py)
            else:result='Unsupported'+':'+txt
            merge_dic=dict(mongodic, **mongodic2)
            final_result=self.result_form(result,categorys)
            self.writeToMongo(result,merge_dic)
            return final_result
        else:
            result1,mongodic_=self.singular_match(txt,input_list[0])
            result2,mongodic1=self.singular_match(txt,input_list[1])

            merge_dic1=dict(mongodic, **mongodic_)
            merge_dic2=dict(mongodic, **mongodic1)
            final_result1=dict(self.result_form(result1,categorys))
            final_result2=dict(self.result_form(result2,categorys))

            for label_e,value_e in final_result1.items():
                if label_e in final_result2.keys():
                    final_result2[label_e]=value_e+','+final_result2[label_e]
                else:
                    final_result2[label_e]=value_e
            self.writeToMongo(result1,merge_dic1)
            self.writeToMongo(result2, merge_dic2)
            return final_result2

#deal non-necessary words
    def preprocess_prefix_suffix(self, txt):
        txt = txt.strip('集')
        txt = txt.strip('季')
        txt=txt.strip('恩')
        txt=txt.strip('嗯')
        flag_pre=0;flag_su=0
        sInput_py = pinyin.get_pinyin(txt, '')
        sInput_py = ''.join(sInput_py)

        categorys={u'电影':'dedianying dedianyingmei dedianmei dedianyoumei pianer dianyinga'
                        'dedianyou zhuyandedianying yandedianying dianying pian'
                        'canyudedianying deyingpian depian yingpian leidedianying dianyingban',
                  u'电视剧': 'dedianshiju dianshiju yandedianshiju juji dianshilianxuju yingshi'
                         'leidedianxing leidongman leijilupian leidedongman leidedianying riju hanju'
                         'canyudedianshiju leideshenghuojiemu meiju yingju','综艺':'leizongyi leidezongyi zongyijiemu',
                  u'动画':'dongman donghua donghuapian riman','体育':'tiyu tiyulei tiyujiemu','娱乐':'yule'
                      }
        category=''
        for pre_key, pre_value in categorys.items():
            for confusion_word in pre_value.split(' '):
                if sInput_py.find(''.join(confusion_word))!=-1:
                    category='category:'+pre_key
        prefix_dic = {
            '我想看': 'tangxiaobai woxiangkan wokan woxiangkan enwoxiangkan woxiangkanhuo haoxiangkan woxiang woxiangkana '
                   'woxiangkange mawoxiangkan geiwolaiyibu woxiangkanyi enwoxiangkan','给我': 'geiwo bangwo',
            '我要看': 'woyaokan oyaokan woyaodian yaokan', '点播': 'dianbo jianbo yanbo chazhao',
            '来一部': 'laiyibu souyib fangyibu','切换至': 'qiehuanzhi qiehuanzi qiehuandao',
            '来一': 'laiyi laige kanyi', '播放': 'qingbofang qingbo bofang boqiu shoukan fangdianbo zhujiaoshi zhujiao',
            '来': 'lai nai na laige naige','那我': 'nawo lawo', '检索': 'jiansuo jianshuo jiasuo jiashuo',
            '有没有': 'youmeiyou youmei kanyikan baobao', '有': 'you kan jiebo',
            '打开': 'dakai dakaiwode', '电视剧': 'dianshiju dianshi dianshilianxuju yingshi yingshi',
            '电影': 'dianying pian yingpian','搜索': 'sousuo','调': 'tiao mv fang','搜': 'sou',
            '集': "zuixinyi zuixin1 zuihouyi zuijinyi zuijin1",
            '恩': 'you en gua', '类型': 'donghuapian donghua zongyi yingwenban yingyu'}

        suffix_dic = {'来一部': 'laiyibu laiyi nayibu nayi', '有哪些': 'youna younaxie youlaxie youmeiyou',
                      '有吗': 'youma youmei', '动画片': 'donghuapian donghuaban xijupian zongyijiemu',
                      '电视剧': 'dianshiju juji dianshilianxuju', '的影视': 'deyingshi yingshi pianzi',
                      '这部电影': 'zhebudianying zhebudian zhedianying zhedian zhepian nabudianying zhegedianying',
                      '类的电视': 'leidedianxing leidongman leijilupian leidedongman leidedianying leizongyi leidezongyi '
                              'leideshenghuojiemu','片儿': 'pianer depianer',
                      '类型': 'zongyi donghua dianying dongman tiyujiemu mv',
                      '的电影':'dedianying dedian deying dedianyingmei dedianyingma dedianyingyoumei dedianyou '
                            'deying deyingpian depian yingpian leidedianying',
                      '版本': 'guoyuban yingyuban guoyu yingyu gaoqingban languang gaoqing languangban nanguang '
                            'nanguangban chaogaoqing quangaoqing quangaoqingban yingwenban neidiban daluban',
                      '的电视剧': 'dedianshiju dianshiju yandedianshiju canyudedianshiju dejuji',
                      '拍摄': 'paishe paide canyan canyu yan biaoyan canyan zhuyan hezuo',
                      '结尾': 'dajieju diyi dier disan disi diwu diliu diqi diba dijiu dishi zuihouyi','没': 'haoba mei',
                      "集":"zuixinyi zuixin1 zuihouyi zuijinyi zuijin1 zuixin2 zuixinliang ne dao pai"}
        for pre_key, pre_value in prefix_dic.items():
            for confusion_word in pre_value.split(' '):
                if sInput_py.startswith(''.join(confusion_word)) is True:
                    sInput_py = sInput_py.replace(''.join(confusion_word), '')
                    flag_pre=1

        for suf_key, suf_value in suffix_dic.iteritems():
            for con_word in suf_value.split(' '):
                if sInput_py.endswith(con_word) is True:
                    sInput_py = sInput_py.replace(''.join(con_word), '')
                    flag_su=2
        flag_er=flag_pre+flag_su
        input_py=[]

        middle_dic={"演的":"zhuyande yande zuopeijiaode canyande","参与":"canyude hezuo banyan","拍摄":"paise daoyan zhizhuode"}
        for mid_key,mid_value in middle_dic.items():
            for mid_wrd in mid_value.split(' '):
                if sInput_py.find(''.join(mid_wrd))!=-1:
                    sInput_py=sInput_py.replace(''.join(mid_wrd),'#')

        if sInput_py.find('#')!=-1:
            input_py.append(sInput_py.split('#')[0])
            input_py.append(sInput_py.split('#')[1])
        return sInput_py,category,flag_er,input_py

    def get_celebrities(self, txt,redisName):
        stop_words = 'woxiang xiangkan laiyibu youmeiy you mei ma chuan dianying de dianyou dedian woxiang woyao xiangkan' \
                     'pindao xinwen dedian shiju deyingshi dianshi yingshi wode shijie diyi dier disan fusi dianbo'
        suggest = set();out_candidate=set()
        for word in txt:
            word_ = pinyin.get_pinyin(word, '')
            word_str = ''.join(word_)
            if stop_words.find(word_str) == -1:
                suggest.add(word_str)
        out = set(conR.hmget(redisName, suggest))
        for i in out:
            if i is not None and ',' not in i:
                out_candidate.add(i.decode('utf-8'))
            elif i is not None and ',' in i:
                newstr = str(i).split(',')
                for line in newstr:
                    out_candidate.add(line)
        return out_candidate

    def get_video(self,txt, redisDBname):
        stop_words = 'woxiang xiangkan yankan laiyi yibu youmei meiyou haoma dianying de dianyou dedian jiayi shouye shouji' \
                     'woyao dianshi shiju dedian yaokan bofang jieju zuihou huaqian shoucang shipian bangzhu jixu zhuzhu jinji' \
                     'me yingshi yingshi shuizhi dianbo guanzhi youmei sousuo yingxiong xiaoshi shijie bendan shichang boni ' \
                     'shouye xiaozi zhufu xingxing guiying youzhi guanjun kuaiqian houhui haoxiao jieguo diyi yici yitian ' \
                     'fangshi maopian fudao xuebao jiandao xiaoxiao haizi jiaren jiangui faxin liangshi guobao gaobie aima ' \
                     'bangbang guiying dongzhu weiliao shenme buchang huizhuan bianshen tongyi jiangjie gufeng shijian jimu ' \
                     'yande zhuyan canyu zhizuo paise sede daode danyan paide'
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
        out = set(conR.hmget(redisDBname, candidate_py))
        for i in out:
            if i is not None and ',' not in i:
                out_candidate.add(i.decode('utf-8'))
            elif i is not None and ',' in i:
                newstr = str(i).split(',')
                for line in newstr:
                    out_candidate.add(line)
        return out_candidate

#result form construction
    def result_form(self, result,category):

        domain = result.split(':')[0].decode('utf-8').encode('utf-8')
        oralname=result.split(':')[1]
        result_dic = {};label='';final_name='';profession=[];formatnames=set()
        scoreDocs_error = clients.query_utils(oralname)
        # entityAql_error = 'For doc In entity Filter "%s" In doc.formatNames and doc.status == "active" RETURN doc' % (oralname)
        # scoreDocs_error = db.AQLQuery(entityAql_error, rawResults=True, batchSize=1000)

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
        if domain!='FailCorrecting' and domain!='FailDetecting':
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
#save it to mongoDB
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
        else:
            if mongodic.has_key('suggestedmovies') or mongodic.has_key('suggestedcelebrities') \
                    or mongodic.has_key('suggestedroles'):
                result_dic['fail_reason']=category
                result_dic['updateAt']=str(datetime.now())
                dicMerged = dict(result_dic, **mongodic)
                wrong_db.insert(dicMerged)
#match figure,video,role
    def singular_match(self, txt, sInput_py):
        temp = [txt[i] + txt[i + 1] for i in range(0, len(txt) - 1)]
        suggestlist_actor=self.get_celebrities(temp,'semantic:error_correct:ConfusingFigure')

        mongodic = {}
        mongodic['error_input'] = txt
        suggestedcelebrities = ''
        tempdic_ac = OrderedDict()
        for actorname_key in suggestlist_actor:
            key2_py = pinyin.get_pinyin(actorname_key.decode('utf-8'), '')
            fuzz_ratio2 = fuzz.ratio(sInput_py, ''.join(key2_py))
            if fuzz_ratio2 > 70:
                suggestedcelebrities = suggestedcelebrities + actorname_key + ':' + str(fuzz_ratio2) + ' '
                mongodic['suggestedcelebrities'] = suggestedcelebrities
            if fuzz_ratio2 >=96:
                result = 'figure:' + actorname_key
                mongodic['highest_score']=actorname_key+':'+str(fuzz_ratio2)
                return result, mongodic
            elif 90 < fuzz_ratio2 <= 95:
                tempdic_ac[actorname_key] = fuzz_ratio2
        if tempdic_ac:
            value1, key1 = list(sorted(tempdic_ac.values())), list(sorted(tempdic_ac.keys()))
            actor_name = key1[value1.index(max(value1))]
            result = 'figure:' + actor_name
            mongodic['highest_score'] = actor_name + ':' + str(max(value1))
            return result, mongodic

        suggestmovies = '';tempdic =OrderedDict()
        suggestlist_movie = self.get_video(temp,'semantic:error_correct:ConfusingVideo')

        for movie_name_key in suggestlist_movie:
            key1_py = fuzz._process_and_sort(''.join(pinyin.get_pinyin(movie_name_key.decode('utf-8'), '')), force_ascii=True)
            sInput_py = fuzz._process_and_sort(sInput_py, force_ascii=True)
            fuzz_ratio1 = fuzz.ratio(sInput_py, ''.join(key1_py))
            if fuzz_ratio1 >= 70:
                suggestmovies = suggestmovies + movie_name_key + ':' + str(fuzz_ratio1) + ' '
                mongodic['suggestedmovies'] = suggestmovies
            if fuzz_ratio1 >= 96:
                result = 'video:' + movie_name_key
                mongodic['highest_score']=movie_name_key+':'+str(fuzz_ratio1)
                return result, mongodic
            elif 84<= fuzz_ratio1 < 96:
                tempdic[movie_name_key] = fuzz_ratio1
        if tempdic:
            value1, key1 = list(tempdic.values()), list(tempdic.keys())
            movie_name = key1[value1.index(max(value1))]
            result = 'video:' + movie_name
            mongodic['highest_score']=movie_name+':'+str(max(value1))
            return result, mongodic

        suggestroles=''
        suggerslit_hotrole=self.get_celebrities(temp,'semantic:error_correct:ConfusingRole')

        for role_name in suggerslit_hotrole:
            key3_py = fuzz._process_and_sort(''.join(pinyin.get_pinyin(role_name.decode('utf-8'), '')), force_ascii=True)
            sInput_py = fuzz._process_and_sort(sInput_py, force_ascii=True)
            fuzz_ratio3 = fuzz.ratio(sInput_py, ''.join(key3_py))
            if fuzz_ratio3 >= 70:
                suggestroles = suggestroles + role_name + ':' + str(fuzz_ratio3) + ' '
                mongodic['suggestedroles'] = suggestroles
            if fuzz_ratio3 >= 96:
                result = 'role:' + role_name
                mongodic['highest_score']=role_name+':'+str(fuzz_ratio3)
                return result, mongodic
            elif 90< fuzz_ratio3 < 96:
                tempdic[role_name] = fuzz_ratio3
        if tempdic:
            value1, key1 = list(tempdic.values()), list(tempdic.keys())
            rolename = key1[value1.index(max(value1))]
            result = 'role:' + rolename
            mongodic['highest_score']=rolename+':'+str(max(value1))
            return result, mongodic
        else:
            result = 'FailCorrecting:' + txt
            return result, mongodic

'''
RNN_LSTM
'''
import re
import extra as EX

target = proofcheck()

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
            if 'name' in reslut and ',' in reslut['name']:#20180108 s
                reslut.pop('name')
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

    def verfiy_data(self, data,src_txt):#20171218 d s
        '''

        :param data:
        :return:
        '''
        # if len(src_txt.replace(data['data']['semantic']['name'],''))==len(re.findall(r'[0-9]+',src_txt)[0]):
        #     data['data']['semantic']['name'] = data['data']['semantic']['name'] +re.findall(r'[0-9]+',src_txt)[0]
        if not re.findall(r'季', src_txt) and not re.findall(r'部', src_txt) and 'season' in data['data']['semantic'] and 'name' in data['data'][
            'semantic']:
            data['data']['semantic']['name'] = "%s%s" % (
            data['data']['semantic']['name'], data['data']['semantic']['season'])
            data['data']['semantic'].pop('season')

        if len(data['data']['semantic']) == 1:
            if 'category' in data['data']['semantic']:
                ss = data['data']['semantic']['category']

                if 'category' in data['data']['semantic'] and ss == '电影' or ss == '电视剧' or ss == '动漫' or ss == '综艺':
                    data['data']['intent'] = 'RECOMMEND'
            else:
                tt = ['episode', 'season', 'year', 'language', 'relative', 'rate', 'extra',
                      'resolution',"publisher",'tag','app_category','app_type','appname','ktv_type','region','site','station',
                      'playTime', 'moviePlayDuration', 'type', 'area']
                for i in tt:
                    if i in data["data"]['semantic']:
                        data = {}
                        break

        else:
            rr = ['publisher','photographer','subdirector','producer', 'app_type', 'appname', 'sub_director','art_designer','ktv_type', 'television_presenter','region', 'site', 'station','writer','dubbing','producer''photographer']#20180108 d
            for j in rr:
                if j in data["data"]['semantic']:
                    data["data"]['semantic'].pop(j)
        return data

    def verfiy_dataKG(self, data,src_txt):#20171226 d s
        '''

        :param data:
        :return:
        '''
        # if len(src_txt.replace(data['data']['semantic']['name'],''))==len(re.findall(r'[0-9]+',src_txt)[0]):
        #     data['data']['semantic']['name'] = data['data']['semantic']['name'] +re.findall(r'[0-9]+',src_txt)[0]
        if  not re.findall(r'季', src_txt) and not re.findall(r'部', src_txt) and 'season' in data['data']['semantic'] and 'name' in data['data']['semantic']:
            data['data']['semantic']['name']= "%s%s" % (data['data']['semantic']['name'], data['data']['semantic']['season'])
            data['data']['semantic'].pop('season')
        if len(data['data']['semantic']) == 1:
            if 'category' in data['data']['semantic']:
                ss = data['data']['semantic']['category']
                if 'category' in data['data']['semantic'] and ss == '电影' or ss == '电视剧' or ss == '动漫' or ss == '综艺':
                    data['data']['intent'] = 'RECOMMEND'
            else:
                tt = ['episode', 'season', 'year', 'language', 'relative', 'rate', 'extra',
                      'resolution','publisher','app_type','appname','ktv_type','region','site','station',
                      'playTime', 'moviePlayDuration', 'area','tag']
                for i in tt:
                    if i in data["data"]['semantic']:
                        data = {}
                        break

        else:
            rr = ['publisher','photographer','subdirector','producer','app_type','appname','art_designer','ktv_type','sub_director','television_presenter','region','site','station','writer','dubbing','producer','photographer']#20180108 d
            for j in rr:
                if j in data["data"]['semantic']:
                    data["data"]['semantic'].pop(j)
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

    def category_verfy(self,info,txt):
        if  info:
            if 'category' in info:
                if '片' in txt and '影片' not in txt and '片子' not in txt:
                    if 'type' not in info or 'area' not in info:
                        del info['category']
        return info

    def verify_year_rate(self,reslut,src_txt):
        if reslut:
            if 'year' in reslut:
                if type(reslut['year']) is int and (reslut['year']<10 or reslut['year']>2030):
                        reslut.pop('year')
            # if 'year' in reslut and not re.findall(r'至',reslut['year']) and re.findall(r'年代',src_txt):#20180116 d
            #     ss = re.findall(r'[0-9]+年代',src_txt)[0]
            #     reslut['year'] =data_procesee.ear(ss) #20180116 d
            if 'rate' in reslut:
                if reslut['rate']>10 or reslut['rate']<1:
                    reslut.pop('rate')
            if 'season' in reslut:
                if reslut['season']>20:
                    reslut={}
            if 'rate' in reslut:
                reslut['rate'] = str(float(reslut['rate']))
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
            if '韩国版' in src:  # add 20180116 s
                src = src.replace('韩国版', '')
                return 'area', '韩国', src
            if value in src:
                value_=value
                key_ = key
                break
        src = src.replace(value_,'')
        return 'language',key_,src

    def verfiy_area(self,src):
        key_ = ''
        value_ = ''
        for value, key in directo_actor.__area__.iteritems():
            if value in src:
                value_ = value
                key_ = key
                break
        src = src.replace(value_, '')
        return 'area', key_, src

    def verfiy_time_ban(self,src):

        ban = re.findall(r'[0-9零一二三四五六七八九]+版', src)
        s='';s_=''
        if ban:
            ban = ban[0]
            s = data_procesee.remove_chinese(ban)
            if s != '':  # --20180111 s
                if int(s) == 0:
                    s = str(2000)  # --20180111 s
                elif int(s) <= 17:
                    s = str(2000 + s)
                elif s > 17 and s < 100:
                    s = str(1900 + s)
                elif len(str(s)) == 4:
                    s = str(s)
                s_ = re.sub(r'[0-9零一二三四五六七八九]+版(的)?', '', src)

        return s,s_

    def verfiy_role(self, reslut):#20171215
        if reslut:

            if 'episode' in reslut and 'role' not in reslut and 'name' not in reslut:
                reslut.pop('episode')
            if 'season' in reslut and 'role' not in reslut and 'name' not in reslut:
                reslut.pop('season')
            return reslut

    def verfiy_ec(self,rnn,ec,src_txt):
        ec_num={'1':'一','2':'二','3':'三','4':'四','5':'五','6':'六','7':'七','8':'八','9':'九','-1':'千','10':'十'}
        if  not re.findall(r'季', src_txt) and not re.findall(r'部', src_txt) and 'season' in rnn and 'name' in ec:
           ec['name']= "%s%s" % (ec['name'], rnn['season'])
           rnn.pop('season')
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
                            elif n + u'部' in ec[j].decode('utf-8'):#20180108 d start
                                rnn.pop('season')
                                nf = 1
                            elif u'第'+n in ec[j].decode('utf-8'):
                                rnn.pop('episode')
                                nf = 1                               #20180108 d end
                                break

            if nf:
                break

        return rnn

    def verfiy(self,buf,fouth_actor,relation,relation_alis,sub_award_contain_year):

        ti = time.time()
        i_ = buf.rstrip().decode('utf-8').encode('utf-8')
        src_txt = i_
        i_ = i_.replace('+', '').replace('-', '').replace('*', '').replace('+', '').replace('÷', '').replace('-', '') \
            .replace('//', '').replace('×', '').replace(' ', '').replace('[', '').replace(']', '').replace('（', '') \
            .replace('）', '').replace('·', '').replace('`', '').replace('<', '').replace('%', '').replace('=', '')

        allflag = 1
        if len(i_)>46:
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

        for _ii_ in ['一键观影','umax','深度优化','金鹰卡通','播放一下','我想看一下','模拟电视','全局搜索','换到视频','切换到视频','视频',"模拟电视","换到视频","切换到视频","视频","视频源",
                 "高清","高清源","换到高清","换到高清源","切换到高清","切换到高清源","劲爆体育","切换到劲爆体育","打开劲爆体育","一键观影","切换到一键观影","设置一键观影",'片尾','片头','幻灯片',
                "打开一键观影","切换到NBATV","切换到FASHIONTV","切换到FashionTV","切换到星空体育","切换到SITV点播影院","切换到SiTV点播影院","切换到上海台",'我的电影','我的电视剧'
                  '照片','片面','片断','图片','应用','声音调到','音量','亮度调到','快进到','减','乘','除','等于','是什么','帅不','是谁','美不','安徽芜湖娱乐','关键比赛']:
            if _ii_ in i_:
                allflag=-1
                break
        if re.findall(u"[0-9a-zA-Z]",i_):#20171227 d
            ss = re.findall(u"[0-9a-zA-Z]+", i_)
            ss_  = ''
            for i in ss:
                ss_ = ss_ + i
            if len(ss)==1 and len(ss[0]) == len(i_) and len(i_)<=3 :
                allflag = -1
            elif len(ss_)>8 and ss_!= 'ANGELABABY':
                allflag = -1


        for i in directo_actor.man_country:
            if i in i_:
                info['area'] = directo_actor.man_country[i]

        domain_final = self.domain_function(i_)

        for j in directo_actor.__tag__:  # add 20180116
            if i_.find(j) != -1:
                info['tag'] = '环绕声'

        if domain_final != 'NULL':

            for lany,lanv in directo_actor._language_.iteritems():
                if lany in i_:
                    info['language'] = lanv
                    i_ = i_.replace(lany,'')
                    break
            if '英文原声版' in i_:
                extra_, result_ = '英文原声版',i_.replace('英文原声版','')
            else:
                extra_, result_ = EX.find_num(i_)#20180111 d
            if extra_  is '4k' or extra_ is '4K':
                info['resolution']='4K' #20180111
                i_ = result_
            elif '高清' in extra_:  # 20180116 s
                info['resolution'] = '高清'  # 20180116 s
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
        l, lk, i_ = self.verfiy_area(i_)
        if lk:
            info[l] = lk

        esi_flag=0
        if '最后一集' in i_:
            i_ = i_.replace('最后一集', '')
            session_espiod['episode'] = -1
        if allflag != -1:
            _,ses, esi, si = self.find_session_epsiod(i_)
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
        for i in directo_actor._part_:
            if i in i_ :
                if 'session' not in info:
                    info['extra'] = i
                elif 'session' in info:
                    info.pop('session')
                i_ = i_.replace(i,'')
                break
        time_ban , time_s = self.verfiy_time_ban(i_)
        if time_ban !='':
            session_espiod['year'] = time_ban
            i_ = time_s
        # if domain_final !='NULL'and not re.findall(r'.*第.*(季|集|部)', i_) and allflag!=-1:
        if not re.findall(r'.*第.*(季|集|部)', i_) and allflag != -1:
            if '大结局' in i_:
                session_espiod['episode']=-1
                if i_[i_.index('大结局')-3:i_.index('大结局')] is '的':
                    i_ = i_[:i_.index('大结局')-3]
                else:
                    i_ = i_[:i_.index('大结局')]

            #i_ = i_.replace('电视连续剧','').replace('这部电视剧','').replace('的电视剧','').replace('长虹小白','')
            ii_ = i_.replace('电视连续剧', '').replace('这部电视剧', '').replace('的电视剧', '').replace('长虹小白', '') #20180115 s
            name_only,name_semantic,full,item = find_core_word.nameOnly(command=ii_#numberTranform(ii_).decode('utf-8').encode('utf-8'),
                                                                        ,corefindFlag=1, searcherEngine='',
                                                                   searchItem1='formatName', searchItem2='formatNames',get_words='label'
                                                                ).postproces()#searcherEngine=searcher_all

            if item:
                name_semantic = self.reasonableness_test(name_semantic)
                if name_semantic:
                    seman_data['src_txt']=src_txt
                    # if domain_final:
                    if 'director' in name_semantic and not re.findall(r'导', src_txt):  # 20180116 d
                        name_semantic.pop('director')
                    if 'appname' in name_semantic or 'station' in name_semantic or 'radio' in name_semantic :
                        lstmresult = {}
                        allflag = 2
                    else:
                        if 'name' in name_semantic and self.in_out(name_semantic['name']) and domain_final and domain_final !='NULL':
                            name_semantic['category']=domain_final

                        elif 'name' not in name_semantic  and domain_final:
                            name_semantic['category'] = domain_final
                        if 'award' in name_semantic and 'category' in name_semantic:#20180116 d
                            if not re.findall(r'电影',src_txt.replace(name_semantic['award'],'')):
                                name_semantic.pop('category')
                        seman_data['domain']='VIDEO'
                        if'season'  in session_espiod and not re.findall(r'部', src_txt) and not re.findall(r'季', src_txt) and 'extra' in info and 'name' in name_semantic:
                            name_semantic['name'] = "%s%s%s" % (name_semantic['name'], session_espiod['season'], info['extra'])#20180113 d
                            info.pop('extra')
                            session_espiod.pop('season')
                        if re.findall(r'部',src_txt) and 'season' in session_espiod:#20180116 d
                            session_espiod['part'] = str(session_espiod['season'])
                            session_espiod.pop('season')
                        if re.findall(r'期',src_txt):
                            session_espiod['term'] = str(session_espiod['episode'])
                            session_espiod.pop('episode')#20180116 d
                        if 'episode' in session_espiod:
                            session_espiod['episode'] = str(session_espiod['episode'])
                        if 'season' in session_espiod:
                            session_espiod['season']=str(session_espiod['season'])
                        if 'extra' in info and 'name' in name_semantic:
                            if info['extra'] not in name_semantic['name'] :
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
                                session_espiod = self.verfiy_ec(session_espiod, name_semantic,src_txt)#20180113 d
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
        searcher_flag=0
        if domain_final !='NULL'and re.findall(r'.*第.*(季|集|部)', i_) or allflag is 0:

            i_ = data_procesee.check_char(i_)


            if isinstance(i_, unicode):
                i_ ,_i= data_procesee.character_separation_unicon(i_)
            elif isinstance(i_, str):
                i_ ,_i= data_procesee.character_separation(i_)

            if 'category' not in info and domain_final:
                if domain_final != 'NULL':
                    info['category'] = domain_final

            if i_.find('电 影')!=-1 or i_.find('影 片')!=-1:
                seman_data['domain'] = 'VIDEO';seman_data['intent'] = 'QUERY'

            elif i_.find('片') != -1 and i_.find('动 画') == -1: #20180110 d
                if 'category' not in info:info['category'] = '电影'#20171214
                seman_data['domain'] = 'VIDEO';seman_data['intent'] = 'QUERY'
            elif i_.find('看')!=-1:
                seman_data['domain'] = 'VIDEO';seman_data['intent'] = 'QUERY'

            if i_.find('剧') !=-1 and '剧 场' not in i_:#20180111 s
                if 'category' not in info:info['category']='电视剧'

            # print i_
            predictions_test =  rnn_model.rec(i_.replace(' ',''))

            s_ = ' '.join(predictions_test)
            # print 'RNN', s_
            self.neural = s_

            # logg.DEBUG(self.neural,'recurrent network prediction')
            if _i is '':
                _i = i_
            cmd = label2command.lbel2command(_i.split(' '), predictions_test)


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
                        if value in src_txt:
                            valueindex = src_txt.index(value)
                            if '版' == src_txt[valueindex+len(value):valueindex+len(value)+3]:
                                key = 'year'
                        if sesson_s and sesson_s!=1000000000:
                            value = sesson_s
                        else:
                            continue
                    if key == 'year' and value <18:
                        value = str(value + 2000)
                    elif key == 'year' and value > 18:
                        value = str(value + 1900)
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
                                elif ti_  is  'sub_award' and tv_.find('奖')  is  -1 and tv_.find('角')  is -1:
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
                        elif value in ['评分高','评价高','比较高']:
                            info['tag'] = '高分'
                            continue
                        elif value in ['抗日战争']:#20171121
                            info['type'] = '战争'
                            continue
                        elif value in directo_actor._type_:
                            info['type'] = value
                            continue

                    if value in sub_award_contain_year:
                        info['sub_awrad']=value
                        continue
                    if (key  is  'year' or key is 'type')and value in ['最近','最新','今年']:
                        info['year']=str(datetime.now().year)
                        continue
                    if value in directo_actor.award_contain_year:
                        info['awrad']=value
                        continue
                    if key  is  'language' and value in directo_actor._language_.keys():
                        info['language'] = directo_actor._language_[value]
                        continue
                    if key == 'year' and value == '年' :#20180116 d
                        ss = re.findall(r'[0-9零一二三四五六七八九]+年',src_txt)[0]
                        value = ss
                    tf,_value = data_procesee.verfy_num(key,value)
                    # if re.findall(r'年以前',src_txt):#20180116 d
                    #     _value = _value + '年前'
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
                                        if tmpvalue not in value:
                                            single_actors.append(tmpvalue)
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
                        if 'director' in info and not re.findall('导',src_txt):#20180116 d
                            info.pop('director')
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

            info = self.category_verfy(info,src_txt)
            info = self.verfiy_result(info)
            info = self.relation_search(info)
            info = self.verify_area(info)
            info = self.verfy_actor_name(info)
            info = self.verify_year_rate(info,src_txt)

            if info and ('season' not in info or 'episode' not in info):
                info = dict(info, **session_espiod)
            info = self.verfiy_role(info)#--20171215 d

            info = self.reasonableness_test(info)

            if searcher_flag and not info:
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
        ec_flag = 1
        if data:
            final = self.verfiy_dataKG(data,src_txt)#20171226 s
            # print 'lucene'
        elif lstmresult and not searcher_flag:
            final = self.verfiy_data(lstmresult,src_txt)#20180108
            # print 'lstm'
        else:
            # print 'jiucuo'
            # if allflag != 2
            if allflag != 2 and allflag !=-1:#20171227 d
                # logg.DEBUG(src_txt, 'here is ec input')
                target = proofcheck()

                result = target.proofreadAndSuggest(u"%s"%src_txt)
                # print result
                if result:
                    if 'appname' in result or 'station' in result or 'radio' in result:
                        final['flag'] = 0; final['code'] = 201
                    else:
                        ec_flag = 0
                        if session_espiod:
                            session_espiod = self.verfiy_ec(session_espiod,result,src_txt)

                            result = dict(result,**session_espiod)
                        if info:
                            if 'role' in info and 'name' in result:
                                if info['role'] in result['name']:
                                    info.pop('role')

                            result = dict(result,**info)
                            if 'category' in result and 'name' in result and (result['category'] in result['name']):
                                result.pop('category')#20171225 s
                            if 'app_category' in result and 'name' in result and (result['app_category'] in result['name']):
                                result.pop('app_category')#20171227 d
                        # result = self.verfiy_data(result, src_txt)
                        tdic={'domain':'VIDEO','intent':'QUERY','src_txt':src_txt}
                        tdic['semantic'] = result
                        final['data'] = tdic
                        final['flag'] = 1
                        final['code'] = 200
                else:
                    final['flag'] = 0
                    final['code'] = 201
            else:
                final['flag']=0;final['code']=201

        if ec_flag and 'data' in final and "semantic" in final['data'] and len(final['data']['semantic']) == 1:
            label = trie_bys_getname.classify(unicode(src_txt))
            if label == 'video':
                final['data']['domain'] = 'VIDEO'
            else:
                final['flag'] = 0
                final['code'] = 201

        s=''
        self.jsonStr = json.dumps(final,ensure_ascii=False)
        ti1 = time.time()
        # logg.DEBUG('%s %s %s %s'%(self.jsonStr,str((ti1 - ti)*1000),ti,ti1))

        # print self.jsonStr

        if s  is '':
            s = 'Sorry, I didn\'t hear clearly, please repeat again'
        s = s+'<br>'+' '+'<br>'+'亲，目前我只会 视频\电视台 相关的哟，不要淘气哟~~~'


if __name__  ==  '__main__':
   k =  rnnIntent('我想看狗狗与疯狂假期')
   # import profile

   # profile.run("rnnIntent.verfiy")