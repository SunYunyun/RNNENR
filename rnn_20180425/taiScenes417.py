# encoding:utf-8
from config_database import config,clients,redis_clients,mongo_ec
# import random
# import threading
import time
import jieba
# import codecs
import json
stopwords = [u'。', u'，', u'?', u'？', u'！', u'的', u'']

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

# for i in all_plot:
#     print i


class TaiSi(object):

    def __init__(self, scr,all_plot_list = all_plot_list):#默认变量

        self.scr = scr
        self.all_plot_list = all_plot_list
        self.scoreJson = {}
        self.main_run()

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


    def cal(self,query, all_tai):

        # 计算相似度
        #plays = totalplays(all_tai)
        scores = {}
        scoreMax = 0
        if query:
            query = self.cut_seg(query)
            l = len(query)
            scoreList = []
            for play in all_tai:  #

                score = 0
                for j in query:
                    if j in play:
                        score = score + 1
                score = score / float(l)  # 归一化
                #print score
                scoreList.append(score)
                # if score == 1.0:
                #     scoreMax = score
                #     #break
                #     return scoreMax
                #
                # else:
                #     scoreList.append(score)

                # scores[''.join(play)] = score
            #print scoreList
            if scoreList != []:
                scoreMax = max(scoreList)
                # print score #输入语句在一部video中个台词最高分

        return scoreMax

    def main_run(self):
        '''

        :param query:
        :return:
        '''
        #if preDatapross(query) >= 8:

        scoreDict = {}
        semantic = {}
        data = {}
        for doc in self.all_plot_list:  # 循环每个影片台词

            name = doc.get('formatName')
            #print name
            # if name ==  u'寻梦环游记':
            classicalLinesCut = doc.get('classicalLinesCutScenes')#doc.get('classicalLinesCut')
            # print name
            # print formatClassicalLines
            scoreMax = self.cal(self.scr, classicalLinesCut)
           # print scoreMax
            if scoreMax > 0.7:  # 概率
                scoreDict[name] = scoreMax

        #print self.scoreDict.keys()[0]
        if scoreDict:
            semantic['name'] = sorted(scoreDict, key=lambda x: scoreDict[x])[-1]
            self.scoreJson['flag'] = 1
            self.scoreJson['code'] = 200
            data['domain'] = "VIDEO"
            data['intent'] = "QUERY"
            data['src_txt'] = self.scr.decode('utf-8')
            data['semantic'] = semantic
            self.scoreJson['data'] = data
            #self.scoreJson['semantic'] = semantic

            self.scoreJson = json.dumps(self.scoreJson,ensure_ascii=False)
        print self.scoreJson
        #else:


            # else:return query #不写返回None
# if __name__ == '__main__':
#     s = time.time()
#     TaiSi('only you' ) #返回
#     e = time.time()
#     print e - s
#     TaiSi('根要扎在土壤里，和风一起生存和鸟儿一起歌颂春天，不管你拥有了多么惊人的武器，也不管你操纵了多少可怜的机器人，只要离开土地，就没办法生存。',all_plot_list)
#     print '2',time.time() - e



