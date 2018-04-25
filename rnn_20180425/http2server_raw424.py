#encoding:utf-8
import sys
sys.path.append("..")

import data_procesee
from datetime import datetime
import time
import logg
import url_request
from ErrorVideoYingxin import ConfigError,proofCheck

time_1 = time.time()

from nlu_predict import nlu as rnn_model
print 'load rnn'

import find_core_word
import label2command
import directo_actor
import utils_main
from num_process import find_name,numberTranform

from config_database import config,clients,redis_clients,mongo_ec
import trie_bys_getname

import error_configRedis as ecR
ecR.writeRedis()

from fuzzywuzzy import fuzz
from xpinyin import Pinyin
# from pymongo import MongoClient
from collections import OrderedDict
from datetime import datetime
from pyArango.connection import *
# import redis

import re
import extra as EX
from ErrorVideoYingxin import ConfigError,proofCheck
import sys
reload(sys)

sys.setdefaultencoding('utf-8')
target = proofCheck.ProofCheck()
txt = '赵微的电影'#放一下急诊科医生
resultVIDEO = target.ErrorSuggestMUVIDEO(u"%s" %txt,ConfigError.clients.redundentVideo(),
                                         'semantic:error_correct:stopword4Video',
                                          'semantic:error_correct:ConfusingVideo','FILM'
 )
print resultVIDEO #None #{'name': u'\u6025\u8bca\u79d1\u533b\u751f'}
#target = proofcheck()
'''
RNN_LSTM
'''


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
        else:return reslut

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
                      'playTime', 'moviePlayDuration', 'type','area']
                for i in tt:
                    if i in data["data"]['semantic']:
                        data = {}
                        break

        else:
            rr = ['app_type', 'appname', 'ktv_type', 'television_presenter', 'region', 'site', 'station']  # 20180124 s
            #rr = ['publisher','photographer','subdirector','producer', 'app_type', 'appname', 'sub_director','art_designer','ktv_type', 'television_presenter','region', 'site', 'station','writer','dubbing','producer''photographer']#20180108 d
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
            rr = ['app_type', 'appname', 'ktv_type', 'television_presenter', 'region', 'site', 'station']  # 20180124 s
            #rr = ['publisher','photographer','subdirector','producer','app_type','appname','art_designer','ktv_type','sub_director','television_presenter','region','site','station','writer','dubbing','producer','photographer']#20180108 d
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
                    if 'type' not in info and 'area' not in info:
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
        bflag=0
        for value,key in directo_actor._language_.iteritems():
            if '韩国版' in src:  # add 20180116 s
                src = src.replace('韩国版', '')
                return 'area', '韩国', src
            if value in src:
                value_=value
                key_ = key
                bflag = 1
                break
        if not bflag:
            for value, key in directo_actor._language_non_ban_.iteritems():
                if '韩国版' in src:  # add 20180116 s
                    src = src.replace('韩国版', '')
                    return 'area', '韩国', src
                if value in src:
                    value_ = value
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
           if str(rnn['season']) not in ec['name']:
               ec['name'] = "%s%s" % (ec['name'], rnn['season'])
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
    def rate_piont(self,src):
        refinal = re.findall(r'(评分|打分|得分|分数)(为|是|大于|不低于|超过|高于)?(\d+(\.)?(\d+)?)',src)
        rate = ''
        if refinal and refinal[0][0]:
            if refinal and refinal[0][2]:
                rate = refinal[0][2]
        else:
            refinal = re.findall(r'(为|是|大于|不低于|超过|高于)?(\d+(\.)?(\d+)?)(分)',src)
            if refinal and refinal[0][4]:
                rate = refinal[0][1]
        return rate

    def type_name(self,src,info):
        if info and 'name' in info and info['name'] in ['CBA','侦探'] and '类' in src:
            info['type'] = info['name']
            del info['name']
        elif info and ('都市剧' in src or '都市片' in src) and ('type' not in info or info['type'] != '都市'):
            info['type'] = '都市'

        return info

    def verfiy_gossip(self,info,src):
        relative=''
        for i in directo_actor.relation_gossip.keys():
            if i in src and 'relative' not in info or ('relative' in info and info['relative'] != directo_actor.relation_gossip[i]):
                relative = directo_actor.relation_gossip[i]
                src = src.replace(i,'')
                break
        return relative,src
    def verfiy_sub_award(self,src):
        sub = ''
        for i in directo_actor.sub_award_sub:
            if i in src:
                if '最佳暑期电影' == i and '迄今' in src:
                    sub = '迄今最佳暑期电影'
                    i = '迄今最佳暑期电影'
                else:
                    sub = i
                src = src.replace(i,'')
                break
        return sub,src

    def verfiy(self,buf,fouth_actor,relation,relation_alis,sub_award_contain_year):

        ti = time.time()
        i_ = buf.rstrip().decode('utf-8').encode('utf-8')
        src_txt = i_
        i_ = i_.replace('+', '').replace('-', '').replace('*', '').replace('+', '').replace('÷', '').replace('-', '') \
            .replace('//', '').replace('×', '').replace(' ', '').replace('[', '').replace(']', '').replace('（', '') \
            .replace('）', '').replace('·', '').replace('`', '').replace('<', '').replace('%', '').replace('=', '')

        allflag = 1
        # if len(i_)>46:
        #     allflag = -1
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

        for _ii_ in ['一键观影','umax','深度优化','金鹰卡通','播放一下','我想看一下','模拟电视','全局搜索','换到视频','切换到视频',"模拟电视","换到视频","切换到视频","视频源",'想听','卸载',
                     "高清源","换到高清","换到高清源","切换到高清","切换到高清源","劲爆体育","切换到劲爆体育","打开劲爆体育","一键观影","切换到一键观影","设置一键观影",'片尾','片头','幻灯片','快进',
                     "打开一键观影","切换到NBATV","切换到FASHIONTV","切换到FashionTV","切换到星空体育","切换到SITV点播影院","切换到SiTV点播影院","切换到上海台",'我的电影','我的电视剧','播放历史',
                     '照片','片面','片断','图片','应用','声音调到','音量','亮度调到','快进到','减','乘','除','等于','是什么','帅不','是谁','美不','安徽芜湖娱乐','关键比赛','我想听','黄骅TV',
                     '新视觉','兰州综艺体育','粤语台','天华高清','中国微电影','NVOD','CCTV','3D台','上海电视剧','睢县教育综艺','SITV','合肥欢笑','HBTV','SDTV','综艺台','电影台','DRAGONTV',
                     '广播台','历史播放']:
            if _ii_ in i_:
                if '删减' in i_:
                    continue
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

            if '英文原声版' in i_:
                extra_, result_ = '英文原声版',i_.replace('英文原声版','')
            else:
                extra_, result_ = EX.find_num(i_)#20180111 d
                if extra_ == 'TV' and 'TVB' in i_:
                    pass
                elif extra_ == '特辑' and '电影特辑' in i_:
                    pass
                elif extra_ == '高清' and '高清演唱会' in i_:
                    pass
                else:i_ = result_
            if extra_ in ['4k','4K']:
                info['extra'] = '4K'
            elif extra_ in ['全高清','超高清','1080P']:
                info['resolution'] = '超清'
            elif extra_ in ['720P','高清']:
                info['resolution'] = '高清'
            elif extra_ in ['流畅','极速','蓝光',]:
                info['resolution']= extra_ #20180111
            elif extra_ is '特辑' and '电影特辑' in src_txt:
                info['type'] = '电影特辑'
            # elif '高清' in extra_:  # 20180116 s
            #     info['resolution'] = '高清'  # 20180116 s
            #     i_ = result_
            elif extra_ and 'TVB' not in i_ and '电影特辑' not in i_:
                info['extra']=extra_
                i_ = result_
            else:
                if allflag !=-1:
                    allflag=0
        if 'resolution' in info and info['resolution'] == '高清' and '高清演唱会' in i_:
            info.pop('resolution')

        gfo,greslut = self.verfiy_gossip(info,i_)
        if gfo:
            info['relative'] = gfo
            i_ = greslut
        subaward,subreslut = self.verfiy_sub_award(i_)
        if subaward:
            if subaward in ['MTV电影奖','多伦多国际电影节']:
                info['award'] = subaward
            else:
                info['sub_award'] = subaward
            i_ = subreslut

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
                        session_espiod['episode'] = esi###
            # print '941',session_espiod
        #20180419 s
        if re.findall(r'部', src_txt) and 'season' in session_espiod:  # 20180116 d
            session_espiod['part'] = str(session_espiod['season'])
            session_espiod.pop('season')
        if re.findall(r'期', src_txt):#if re.findall(r'期', self.src)
            if 'episode' in session_espiod:  # if 'episode'in session_espiod:#######
                session_espiod['term'] = str(session_espiod['episode'])
                session_espiod.pop('episode')  # 20180116 d
        if 'episode' in session_espiod:
            session_espiod['episode'] = str(session_espiod['episode'])
        if 'season' in session_espiod:
            session_espiod['season'] = str(session_espiod['season'])

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
            kg_actor = ['刘德华', '张学友','周星驰']
            kg_name = ['芈月传']

            if item:
                name_semantic = self.reasonableness_test(name_semantic)
                if name_semantic:
                    seman_data['src_txt']=src_txt
                    # if domain_final:
                    # if 'director' in name_semantic and not re.findall(r'导', src_txt):  # 20180116 d
                    #     name_semantic.pop('director') #20180124 s
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
                            #20180419
                        # if re.findall(r'部',src_txt) and 'season' in session_espiod:#20180116 d
                        #     session_espiod['part'] = str(session_espiod['season'])
                        #     session_espiod.pop('season')
                        # if re.findall(r'期',src_txt):
                        #     if 'episode'in session_espiod:#if 'episode'in session_espiod:#######
                        #         session_espiod['term'] = str(session_espiod['episode'])
                        #         session_espiod.pop('episode')#20180116 d
                        # if 'episode' in session_espiod:
                        #     session_espiod['episode'] = str(session_espiod['episode'])
                        # if 'season' in session_espiod:
                        #     session_espiod['season']=str(session_espiod['season'])
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
                            seman_data['lines'] = '0'#add 20180423
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

            if (i_.find('电 影')!=-1 or i_.find('影 片')!=-1) and '电 影 台' not in i_:
                seman_data['domain'] = 'VIDEO';seman_data['intent'] = 'QUERY'

            elif i_.find('片') != -1 and i_.find('动 画') == -1: #20180110 d
                if 'category' not in info:info['category'] = '电影'#20171214
                seman_data['domain'] = 'VIDEO';seman_data['intent'] = 'QUERY'
            elif i_.find('看')!=-1:
                seman_data['domain'] = 'VIDEO';seman_data['intent'] = 'QUERY'

            if i_.find('剧') !=-1 and '剧 场' not in i_:#20180111 s
                if 'category' not in info:info['category']='电视剧'

            # print i_
            if '我 要 看' in i_:
                i_ = i_.replace('我 要 看','我 想 看')
            predictions_test =  rnn_model.rec(i_.replace(' ',''))

            # ppos.POS.pos_rnn(unicode(src_txt))

            s_ = ' '.join(predictions_test)
           # print 'RNN', s_
            self.neural = s_

            logg.DEBUG(self.neural,'recurrent network prediction')
            if _i is '':
                _i = i_
            cmd = label2command.lbel2command(_i.split(' '), predictions_test)


            for key,value in cmd.iteritems():
                if value  is  '':
                    continue
                if key == 'relative' and '他' in value or '她' in value:
                    if '和' in src_txt or '跟' in src_txt or '与' in src_txt:
                        info['_relative'] = value[3:]
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
                    if '分钟' in value or '秒' in value:
                        continue
                    if value in directo_actor._part_:
                        value = dir#encoding:utf-8ecto_actor._part_[value]
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
                    if value == '金像奖' and '香港' not in src_txt:
                        info['award'] = '奥斯卡金像奖'
                        continue
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
                                    tmvalue_ = tv_ #add 20180418
                                   #encoding:utf-8 tmvalue_ = tv_
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
                        elif value == '电影,特辑':
                            info['type'] = '电影特辑'
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
                    if key is 'language' and value in directo_actor._language_non_ban_.keys():
                        info['language'] = directo_actor._language_non_ban_[value]
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
                                            if 'actor' in info and 'actor' in ftmp:
                                                info['actor'] = ('%s%s%s')%(info['actor'],',',ftmp['actor'])
                                            elif 'director' in info and 'director' in ftmp:
                                                info['director'] = ('%s%s%s') % (info['director'], ',', ftmp['director'])
                                            else:info = dict(info,**ftmp)
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
                        if 'ANGELABABY' in value :
                            single_actors.append('ANGELABABY')
                            if  ',' in value:
                                if re.sub(r'(ANGELABABY)+', '', value):single_actors.append(re.sub(r'(ANGELABABY)+', '', value))
                        else:
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
                            if '我想看有' in src_txt:
                                info['role'] = fv
                                break
                            if fk in info:
                                info[fk] = info[fk]+','+fv
                            else:info[fk]=fv
                        # if 'director' in info and not re.findall('导',src_txt):#20180116 d
                        #     info.pop('director')#20180124 s
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
            info_rate =  self.rate_piont(src_txt)
            #print info
            if '_relative' in info:
                info['relative'] = info['_relative']
                del info['_relative']
            if info_rate:
                if 'rate' not in info:
                    info['rate'] = info_rate
                elif 'rate' in info and info['rate']!=info_rate:
                    info['rate'] = info_rate
            info = self.type_name(src_txt,info)

            if info and ('season' not in info or 'episode' not in info):
                info = dict(info, **session_espiod)
            info = self.verfiy_role(info)#--20171215 d

            info = self.reasonableness_test(info)

            if searcher_flag and not info:####
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
                        seman_data['lines'] = '0'#add 20180423
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
            if src_txt in directo_actor.area_tvPlay.keys():
                final['data']['semantic']['area'] = directo_actor.area_tvPlay[src_txt]

        else:
            # print 'jiucuo'
            # if allflag != 2
            if allflag != 2 and allflag !=-1:#20171227 d
                logg.DEBUG(src_txt, 'here is ec input')
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

                            if session_espiod: result = dict(result,**session_espiod)
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
                        tdic['lines'] = '0'
                        final['data'] = tdic

                        final['flag'] = 1
                        final['code'] = 200
                        #final['lines'] = '0'
                else:
                    final['flag'] = 0
                    final['code'] = 201
            else:
                final['flag']=0;final['code']=201

        if ec_flag and 'data' in final and "semantic" in final['data'] and len(final['data']['semantic']) == 1:
            if 'area' not in final['data']['semantic']:
                label = trie_bys_getname.classify(unicode(src_txt))

                if label == 'video':
                    final['data']['domain'] = 'VIDEO'
                else:
                    final={}
                    final['flag'] = 0
                    final['code'] = 201

        s=''
        self.jsonStr = json.dumps(final,ensure_ascii=False)
        ti1 = time.time()
        logg.DEBUG('%s %s %s %s'%(self.jsonStr,str((ti1 - ti)*1000),ti,ti1))

        #print self.jsonStr

        if s  is '':
            s = 'Sorry, I didn\'t hear clearly, please repeat again'
        s = s+'<br>'+' '+'<br>'+'亲，目前我只会 视频\电视台 相关的哟，不要淘气哟~~~'


if __name__  ==  '__main__':

    import time
    s = time.time()
    k =  rnnIntent('我想看赵微的电影')#我想看狗狗与疯狂假期
    print time.time() - s


   # import profile

   # profile.run("rnnIntent.verfiy")
