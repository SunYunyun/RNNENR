#encoding:utf-8

from config_database import clients
import re

# class Weather(object):
#
#     def __init__(self,command,pseg):
#         self.command = command
#
#         self.score = 0
#         self.FINAL={}
#
#         words,flag = self.cut_pos(pseg)
#         self.juge(words,flag)
#         self.intention(words, flag)
#
#     def cut_pos(self,pseg):
#
#         seg_list = pseg.cut(self.command)
#         W=[];F=[]
#         for word, flag in seg_list:
#             W.append(word.encode('utf-8'))
#             F.append(flag.encode('utf-8'))
#         return W,F
#
#     def juge(self,words,flag):
#
#         if '天气' in words:
#             self.score = 80
#         if '天气' in self.command:
#             if 't' in flag and 'n' in flag :
#                 self.score = 90
#             if 'm' in flag and 'n' in flag :
#                 self.score = 90
#             if 'ns' in flag and 'n' in flag:
#                 self.score = 90
#             if 'ns' in flag and 'n' in flag and 't' in flag:
#                 self.score = 95
#             if 't' in flag and 'm' in flag and 'n' in flag:
#                 self.score = 95
#             if 'ns' in flag and 'n' in flag and 't' in flag and 'm' in flag:
#                 self.score = 98
#
#     def intention(self,words,flag):
#         if self.score>80:
#             self.FINAL['domain'] = 'WEATHER'
#             self.FINAL['intent'] = 'WEATHER_QUERY'
#             nt = [words[val] for val in range(len(flag)) if flag[val]=='nt']
#             t = [words[val] for val in range(len(flag)) if flag[val]=='t']
#             m = [words[val] for val in range(len(flag)) if flag[val] == 'm']
#             ns = [words[val] for val in range(len(flag)) if flag[val] == 'ns']
#
#             if nt !=[]:
#                 self.FINAL['sation'] = nt[0]
#             if t !=[] and m!=[]and 'sation' not in self.FINAL.keys():
#                 if len(m[0])<3:
#                     self.FINAL['sation'] = t[0]+m[0]+'天'
#                 else:self.FINAL['sation'] = t[0]+m[0]
#             if t!=[]:
#                 self.FINAL['sation'] = t[0]
#             if ns!=[]:
#                 self.FINAL['area']=ns[0]
#             if m!=[]:
#                 if len(m[0])<3:
#                     self.FINAL['sation'] = m[0]+'天'
#                 else:self.FINAL['sation'] = m[0]
#         elif self.score==80:
#             self.FINAL['domain'] = 'WEATHER'
#             self.FINAL['intent'] = 'WEATHER_QUERY'
#
#     def get_score(self):
#         return self.score,self.FINAL


class Domain(object):

    def __init__(self,command):

        self.category=''
        if '直播' in command:
            self.category='直播'
        elif '电视剧' in command or '国产剧' in command or '日剧' in command or '电视连续剧'in command or '连续剧' in command:
            self.category =  "电视剧"
        elif '看节目' in command:
            self.category = '推荐节目'
        elif '综艺' in command or '综艺节目 ' in command:  # 20180117 d
            self.category = '综艺'
        elif '电影' in command or '影片' in command or '观影' in command or '片子' in command:#20180116 d
            self.category = '电影'
        elif ('动漫' in command  or '儿童节目' in command or '少儿节目' in command or '动画' in command\
                or '卡通' in command or '二次元' in command or '少儿' in command or '日漫' in command or '国漫' in command \
                or '美漫' in command or '韩漫' in command or '台漫' in command or '港漫' in command or '欧漫' in command or '动画' in command or '动画片' in command) and '频道' not in command\
                and '台' not in command:
            self.category = '动漫'
        elif ('体育' in command or '比赛' in command) and '频道' not in command:
            self.category = '体育'
        elif '娱乐' in command:
            self.category = '娱乐'
        elif '游戏' in command and '我想玩' not in command:
            self.category = '游戏'
        elif '纪录片' in command or '记录' in command:
            self.category = '纪录'
        elif 'MV' in command or 'mv' in command:
            self.category = "MV"
        elif '时尚' in command:
            self.category = '时尚'
        elif '教育' in command:
            self.category = '教育'
        elif command.find('汽车') != -1:
            self.category = '汽车'
        elif '生活' in command and '生活台' not in command and '生活频道' not in command and '生活电视频道' not in command and '日常' not in command:
            self.category = '生活'
        elif '想听' in command or '来一曲' in command or '我想听' in command or '听' in command or '曲子' in command or '蓝牙' in command or 'YPBPR1' in command:
            self.category = 'NULL'

    def get_value(self):
        return self.category

class nameOnly(object):

    def __init__(self,command,corefindFlag,searcherEngine,searchItem1='videoName',searchItem2='anotherName',get_words='videoName'):

        self.flag=0
        self.full=''
        self.command = command
        self.searchItem1 = searchItem1
        self.searchItem2 = searchItem2
        self.get_words = get_words
        self.name=''
        self.final = ''
        self.label=''
        self.nameori = ''

        self.name = command
        self.search_video(searcherEngine)

        # if self.final == {} and corefindFlag:
        #     self.find_key_word()
        #
        # self.search_video(searcherEngine)

        if self.final == {} and corefindFlag:
            self.find_key_word()
            self.search_video(searcherEngine)
        else:
            # if re.findall(r'[0-9]',command):
            if re.findall((u'[0-9零一两二三四五六七八九]'), command.decode('utf-8')):  # add  20180118 s
                if type(self.final) is not dict: self.final = command  # --add 20180117 s shuzi

        self.postproces()

    def numberTranform_(self,txt):

        '''
        function:将语句中含阿拉伯数字0-9转换为零到九 1013 只用这一个目前
        :param txt:
        :return:
        '''
        numberDict = {u'0': u'零', u'1': u'一', u'2': u'二', u'3': u'三', u'4': u'四', u'5': u'五', u'6': u'六',
                      u'7': u'七', u'8': u'八', u'9': u'九'}

        if isinstance(txt, str):
            txt = txt.decode('utf-8')

        txt = list(txt)
        for i in txt:
            if i in numberDict:
                txt[txt.index(i)] = numberDict.get(i)
        relute = ''.join(txt)
        return relute

    def find_key_word(self):
        command_words=['我想看','我想要','我要看','来一','找一找','我想要看', '我想点播', '我想播放', '想播放', '想点播', '有没有', '想看', '点播', '播放', '想播','来部',
                        '放', '看', '点播', '播', '有什么好看的','打开','搜索','想放', '想要',  '点播','转到','调到','切换','切换到','我要点','我看','请播放',
                        '我想看电影','我想要电影','我要看电影','我想点播电影','我想播放电影','想播放电影','有没有电影','想看电影','点播电影','播一下','放放','放一下',
                       '播放电影','想播电影','想放电影','想要电影','搜索电影','点播电影','放电影','看电影','播电影','我想看电视剧','我想要电视剧','我要看电视剧','切到','跳到',
                       '我想要看电视剧','我想点播电视剧','我想播放电视剧','想播放电视剧','想点播电视剧','有没有电视剧','想看电视剧','点播电视剧','播放电视剧','换到','有吗',
                       '想播电视剧','想放电视剧','想要电视剧','搜索电视剧','点播电视剧','放电视剧','看电视剧','播电视剧','放映','切换到','再看一遍','重播','回放','看一下','好不好','放','的电影','电视剧']
        flag=1
        for i in command_words:
            if i in self.command:#self.command.find(i)!=-1:
                # if '电影' in self.command or '影片' in self.command or '片子' in self.command or '电视剧' in self.command:
                #     break
                # else:
                if i == '播' and '直播' in self.command:
                    continue
                # elif i == '看' and ('看片' in self.command or '看电视' in self.command or '乐看' in self.command or  '看台' not in self.command
                #                    or '看TV' in self.command or '回看' in self.command or '酷看' in self.command):
                elif i == '看' and (
                    '看片' in self.command or '看电视' in self.command or '乐看' in self.command or '看台'  in self.command#2017-12-18
                                       or '看TV' in self.command or '回看' in self.command or '酷看' in self.command):
                    continue

                else:

                    name = self.command[self.command.index(i)+len(i):]
                    # if len(name.replace('推荐','')) > 3:#20171120
                    #     break
                    if name=='':
                        name = self.command.replace(i,'')
                        self.command = name
                    if  name not in ['电视剧','电影','']:
                        if '电影' in name:  # add 20180117 s
                            name = name.replace('电影', '')
                        # vname = self.numberTranform_(self.command[self.command.index(i)+len(i):])
                        vname = self.numberTranform_(name)
                        self.nameori = name
                        self.command = name
                        self.name = vname
                    flag = 0
                    self.full = 'sub'
                    break
        if flag:
            self.full='y'
            self.name = self.command

    def search_video(self,searcherEngine=''):

        if self.name:

            # conn = Connection(arangoURL=config.arrangoPath)
            # db = conn[config.arrangoName]

            scoreDocs = clients.query_utils(self.name)

            # entityAql = 'For doc In entity Filter "%s" In doc.formatNames and doc.status == "active" RETURN doc' % (self.name)
            # scoreDocs = db.AQLQuery(entityAql, rawResults=True, batchSize=10000)
            # conn.disconnectSession()

            final={}
            actorflag={}
            ts=''
            if len(scoreDocs) != 0:
                counter=0

                p = [scoreDoc.get(self.get_words).encode('utf-8') for scoreDoc in scoreDocs]
                if 'appname' in p and '打开' in self.command:
                    final['appname'] = self.name
                elif 'station' in p and '打开' in self.command:
                    final['station'] = self.name
                elif 'radio' in p and '打开' in self.command:
                    final['radio'] = self.name
                else:
                    for doc in scoreDocs:
                        ts = doc.get(self.get_words).encode('utf-8')
                        tm = doc.get(self.searchItem1).encode('utf-8')
                        if ts in ['appname','station'] :
                            final[ts] = self.name
                            # break
                            continue#20171227 d
                        elif ts == 'figure':
                            tp_ = doc['profession']
                            eflag=1
                            for i in tp_:
                                if i=='singer' or i=='writer' or i=='art_designer' or i=='compose':
                                    eflag=0
                                    continue
                                final[i]=tm
                                actorflag[i]=tm
                            if eflag and counter>len(scoreDocs):
                                break
                        elif ts =='film' and tm == self.name:
                            final['name'] = self.name
                            break
                        elif ts =='film' and tm != self.name:
                            ts = 'name'
                            if 'name'in final:
                                final[ts] = "%s///%s"%(final['name'],tm)
                            else:
                                final[ts] = tm
                        else:
                            final[ts] = tm
                        counter = counter+1


            if final:
                self.flag=1
                if 'name' in final:
                    if '///' in final['name']:
                        if re.findall(r'[0-9]', self.nameori):  # 20180117 d
                            self.final = self.nameori
                            self.label = 'name'
                        else:
                            self.final = self.name
                            self.label = 'name'
                    else:
                        self.final = final['name']
                        self.label = 'name'
                elif 'name' not in final and ('actor' in final or 'director' in final):
                    self.final = actorflag
                    self.label = 'figure'
                elif 'name' not in final and 'figure' not in final and 'role' in final:
                    self.final = final['role']
                    self.label = 'role'
                else:
                    for key,value in final.iteritems():
                        self.final = value
                        self.label = key
                        break

            else:
                self.final = final
                self.label = ts

    def postproces(self):
        data={};semantic={}
        if self.final != '':
            if self.label == 'name':
                data['domain'] = 'VIDEO'; semantic['name'] = self.final;data['intent'] = 'QUERY'
            elif self.label == 'category':
                semantic['category'] = self.final;data['intent'] = 'QUERY'
            elif self.label == 'figure':
                semantic = self.final
                data['domain'] = 'VIDEO'; data['intent'] = 'QUERY'
            elif self.label == 'station':
                data['domain'] = 'TV';  semantic['station'] = self.final;data['intent'] = 'QUERY'
            elif self.label=='role':
                # if isinstance(self.final,dict):
                #     semantic = dict(semantic,**self.final)
                # elif isinstance(self.final,str):
                semantic['role'] = self.final
                data['intent'] = 'QUERY';data['domain'] = 'VIDEO'
            elif self.label =='category':
                data['domain'] = 'VIDEO'; data['intent'] = 'QUERY'
            else:
                data['domain'] = 'VIDEO'; data['intent'] = 'QUERY'
                # if isinstance(self.final,dict):
                #     semantic = dict(semantic,**self.final)
                # elif isinstance(self.final,str):
                semantic[self.label] = self.final
        if self.full:
            flag = self.full
        else: flag =''
        lable = self.label
        return data,semantic,flag,lable


# if __name__ == '__main__':
#
#     fm = Weather("我想知道成都明天的天气",pseg)
#     s,k  = fm.get_score()
    # print s
    # for key ,value in k.iteritems():
    #     print key,': ',value
    # fm = nameOnly('我想看贫民张大嘴的幸福生活')
    # print fm.name
    # import sys, os, lucene
    #
    # from java.nio.file import Paths
    # from org.apache.lucene.analysis.standard import StandardAnalyzer
    # from org.apache.lucene.index import DirectoryReader, Term
    # from org.apache.lucene.queryparser.classic import QueryParser
    # from org.apache.lucene.store import SimpleFSDirectory
    # from org.apache.lucene.search import IndexSearcher, TermQuery, BooleanQuery, BooleanClause
    # from org.apache.lucene.analysis.cn.smart import SmartChineseAnalyzer
    #
    # lucene.initVM(vmargs=['-Djava.awt.headless=true'])
    #
    #
    # base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    # INDEX_DIR_all = "entity"
    # directory_all = SimpleFSDirectory(Paths.get(os.path.join(base_dir, INDEX_DIR_all)))
    # searcher_all = IndexSearcher(DirectoryReader.open(directory_all))
    #
    #
    # name_only = {}
    #
    # # nameonly = find_core_word.nameOnly(i_,searchervideo, TermQuery, Term, BooleanQuery, BooleanClause)
    # nameonly,s,l = nameOnly('CCTV6', 1,searcher_all, TermQuery, Term, BooleanQuery, BooleanClause,
    #                         searchItem1='name', searchItem2='formatName', get_words='label').postproces()
    #
    # # if nameonly.final != '':
    # #     name_only['videoName'] = nameonly.final
    # #     if nameonly.label == 'film':
    # #         name_only['domain'] = 'VIDEO';
    # #     elif nameonly.label == 'station':
    # #         name_only['domain'] = 'TV';
    # #     name_only['intent'] = 'QUERY';
    #
    # print nameonly,' ',s,' ',l