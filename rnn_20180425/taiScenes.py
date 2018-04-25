# encoding:utf-8
from config_database import config,clients,redis_clients,mongo_ec
# import random
# import threading
import time
import jieba
# import codecs
import json

stopwords = [u'。', u'，', u'?', u'？', u'！', u'的', u'',u'"',u'（',u'）',u'：',u'']
all_plot = clients.query_plot()  # 将所有台词场景加载到内存

def cut_seg(src):
    '''
    分词,返回list
    :param src:
    :return:
    '''
    if src:
        segs = jieba.cut(src, False)
        segs = '/'.join(segs).rstrip().split('/')
        segs = [val for val in segs if val not in stopwords]
        return segs
def totalplays(src):

    allplays = []
    if src:
        for i in src:
            allplays.append(cut_seg(i))
    # print allplays
    return allplays

all_plot_list = []

for video in all_plot:
    #print video
    formatName = video[u'formatName']
    for lines in video[u'formatClassicalLines']:
       # print lines
        every_video = {}
        every_video['formatName'] = formatName
        every_video['classicLine']=cut_seg(lines[u'classicalLine'])#台词分词后的list 台词场景均是classLine字段
        if lines.get('time'):
            every_video['time'] = lines['time']
        if lines.get('episode'):
            every_video['episode'] = lines['episode']

        all_plot_list.append(every_video)

    for scene in video[u'formatScenes']:

        every_video = {}
        every_video['formatName'] = formatName
        every_video['classicLine'] = cut_seg(scene[u'scene'])  # 台词分词后的list 台词场景均是classLine字段
        if scene.get('time'):
            every_video['time'] = scene['time']
        if scene.get('episode'):
            every_video['episode'] = scene['episode']
        all_plot_list.append(every_video)

import codecs
f = codecs.open('taisi4181.txt','w','utf-8')
for i in   all_plot_list:
   # f.write(i['formatName'] + '  ')
    for j in i['classicLine']:
        f.write(j)
    # f.write('   ')
    # if i.get('time'):
    #     f.write(i['time'])
    #     f.write('  ')
    #
    # if i.get('episode'):
    #     f.write(str(i['episode']))
    #     f.write('  ')
    f.write('\r\n')
f.close()


#
# for video in all_plot:
#     all_plot_cut = {}
#
#     # print video[u'classicalLines']
#     all_plot_cut['formatName'] = video[u'formatName']
#     #台词分词list
#     classicalLinesCut = totalplays(video[u'classicalLines'])
#     #台词场景分词list合并
#     classicalLinesCut.extend(totalplays(video[u'scenes']))
#     all_plot_cut['classicalLinesCutScenes'] = classicalLinesCut
#     # all_plot_cut[u'classicalLinesCut'] = totalplays(video[u'classicalLines'])
#     # all_plot_list.append(all_plot_cut)
#     all_plot_list.append(all_plot_cut)

# for i in all_plot_list:
#     print i['formatName']
#     for j in i['classicLine']:
#         print j
#     break

class TaiSi(object):

    def __init__(self, scr,all_plot_list = all_plot_list):#默认变量


        self.scr = scr
        self.all_plot_list = all_plot_list
        self.scoreJson = {}
        self.main_fun()

    def proData(self,query):
        '''

        :return:
        '''
        part = ['我想看', '我要看', '播放', '观看', '台词', '剧情']
        query = query.replace('。','').replace(' ','').replace('，','').replace('！', '').replace('？', '')\
            .replace(',', '').replace('：', '').replace('"', '').replace('\'', '').upper()#！ ？

        for word in part:
            if query.find(word) != -1:
                query = query.replace(word, '')
                break
        #print query
        #self.proQuery = query

        #处理短台词剧情  20180417 wan onlyyou

        return query

    def cut_seg(self, src):
        '''
        分词,返回list
        :param src:
        :return:
        '''
        if src:
            segs = jieba.cut(src, False)
            segs = '/'.join(segs).rstrip().split('/')
            segs = [val for val in segs if val not in stopwords]
            return segs

    def calSimilarity(self, query, all_tai):
        '''
        计算相似度
        :param query:
        :param all_tai:
        :return:
        '''
        scoreMax = 0
        reDict = {}
        query = self.proData(query)
        if query:
            query_cut = self.cut_seg(query)

            l = len(query_cut)#

            scoreList = []

            for every_line in all_tai:
                score = 0
                for word in query_cut:
                    if word in every_line['classicLine']:

                        score = score + 1
                score = score / float(l)  # 归一化
                #print score

                if score == 1.0:
                    reDict = every_line
                    return reDict#20180423
                    break

                # elif  0.7 < score < 1.0:
                #     scoreList.append(score)
                else:
                    scoreList.append(score)
            #print max(scoreList)
            if scoreList:
                scoreMax = max(scoreList)
                #print scoreMax
                if scoreMax > 0.66:
                    reDict = all_tai[scoreList.index(scoreMax)]

        #print reDict
        return reDict

    def main_fun(self):
        '''

        :return:
        '''
        scoreDict = {}
        semantic = {}
        data = {}

        re = self.calSimilarity(self.scr, self.all_plot_list)
        if re:
            semantic['name'] = re['formatName']
            self.scoreJson['flag'] = 1
            self.scoreJson['code'] = 200
            data['domain'] = "VIDEO"
            data['intent'] = "QUERY"
            data['lines'] = '1'
            data['src_txt'] = self.scr.decode('utf-8')
            if re.get('time'):
                semantic['play_time'] = re['time']
            if re.get('episode'):
                semantic['episode'] = re['episode']

            data['semantic'] = semantic
            self.scoreJson['data'] = data
            # self.scoreJson['semantic'] = semantic

            self.scoreJson = json.dumps(self.scoreJson, ensure_ascii=False)
        #print self.scoreJson



            # else:return query #不写返回None
if __name__ == '__main__':
    import cProfile
    s = time.time()
    TaiSi('我要看张一曼自杀了')#返回
    e = time.time()
    print e - s
#     TaiSi('根要扎在土壤里，和风一起生存和鸟儿一起歌颂春天，不管你拥有了多么惊人的武器，也不管你操纵了多少可怜的机器人，只要离开土地，就没办法生存。',all_plot_list)
#     print '2',time.time() - e




