#encoding:utf-8
#coding:utf-8

from xpinyin import Pinyin
from collections import defaultdict
from pyArango.connection import *
import sys
from ConfigError import clients,config
config.dev_address=102
pinyin=Pinyin()
# from config_database import config,clients
import redis



# conR=redis.Redis(host='10.9.46.102',port=6379,db=15)
# conn=Connection(arangoURL = 'http://10.9.46.114:8529',username='tester',password=123456)
# db=conn['knowledge-graph-test']

conR=redis.Redis(host=config.redis_ip,port=config.redis_port,db=config.redis_db_error)
conn=Connection(arangoURL = config.arrangoPath,username='tester',password=123456)
db=conn[config.arrangoName]

#contruct pinyin set
def confusing_map(data):
    confusing_dic=defaultdict(list)
    for line in data:
        if line!=None:
            counti = 0
            if len(line) >2:
                # type_line = line.decode('utf-8').encode('utf-8')
                while counti <= len(line) - 2:
                    two_grams = line[counti] + line[counti + 1]
                    two_grams_py = pinyin.get_pinyin(two_grams, '')

                    if two_grams_py in confusing_dic:
                        confusing_dic[two_grams_py]=confusing_dic[two_grams_py]+','+line
                        # value=value+line
                        # confusing_dic[two_grams_py].append(line)
                    else:
                        confusing_dic[two_grams_py]=line
                        # confusing_dic[two_grams_py] = [line, ]
                    counti += 1
            elif len(line) <= 2:
                line_py = pinyin.get_pinyin(line.strip(), '')
                if line_py in confusing_dic:
                    confusing_dic[line_py]=confusing_dic[line_py]+','+line
                    # confusing_dic[line_py].append(line)
                else:
                    confusing_dic[line_py]=line
                    # confusing_dic[line_py] = [line , ]
    # out_dic=json.dumps(confusing_dic, encoding="UTF-8", ensure_ascii=False)
    # print out_dic
    return confusing_dic
#get data from arango
def get_videos():
    video=set()
    aql = 'For doc In entity Filter doc.label=="film" && doc.hot==true ' \
          '&& doc.status=="active" Return doc.formatNames'
    queryResult_video = db.AQLQuery(aql, rawResults=True, batchSize=1)
    for key in queryResult_video:
        for item in key:
            if check_chinese(item)==True:
                # print item
                video.add(item)
    return video

def check_chinese(word):
    if u'\u4e00'<=word and word<=u'\u9fa5':
        return True
    else:return False

def get_hotcelebrity():
    celerity_dataset = set()
    hot_role=set()
    aql = 'For doc In entity Filter doc.label=="figure" && ' \
          'doc.hot==true && doc.status=="active" Return doc.formatNames'
    queryResult = db.AQLQuery(aql, rawResults=True, batchSize=1)
    for key in queryResult:
        for item in key:
            print item
            celerity_dataset.add(item)

    aql_role='For doc in entity filter doc.label=="film" && ' \
             'doc.hot==true && doc.status=="active" return doc.roleNames'
    queryResult_role = db.AQLQuery(aql_role, rawResults=True, batchSize=1)
    for key in queryResult_role:
        if key!=None:
            for item in key:
                hot_role.add(item)
    return celerity_dataset,hot_role

def update_data():
    get_video = get_videos()
    videos = confusing_map(get_video)
    get_celebrity,get_role = get_hotcelebrity()
    celebrity = confusing_map(get_celebrity)
    hot_role=confusing_map(get_role)

    return videos,celebrity,hot_role


def rule_error():
    stopword4Video = 'woxiang xiangkan yankan laiyi yibu youmei meiyou haoma dianying de dianyou dedian jiayi shouye shouji' \
                 'woyao dianshi shiju dedian yaokan bofang jieju zuihou huaqian shoucang shipian bangzhu jixu zhuzhu jinji' \
                 'me yingshi yingshi shuizhi dianbo guanzhi youmei sousuo yingxiong xiaoshi shijie bendan shichang boni ' \
                 'shouye xiaozi zhufu xingxing guiying youzhi guanjun kuaiqian houhui haoxiao jieguo diyi yici yitian ' \
                 'fangshi maopian fudao xuebao jiandao xiaoxiao haizi jiaren jiangui faxin liangshi guobao gaobie aima ' \
                 'bangbang guiying dongzhu weiliao shenme buchang huizhuan bianshen tongyi jiangjie gufeng shijian jimu ' \
                 'yande zhuyan canyu zhizuo shede daode danyan paide paishe huijia xiaohuang changde aide woai aini aita' \
                     'daini'
    stopword4Figure='woxiang xiangkan laiyibu youmeiy you mei ma chuan dianying de dianyou dedian woxiang woyao xiangkan ' \
                    'pindao xinwen dedian shiju deyingshi dianshi yingshi wode shijie diyi dier disan fusi dianbo jiazheng wuma'
    stopWordAPPTv='woxiang xiangkan laiyibu youmeiy you mei ma chuan'
    MinThresholds='90,86,94'
    return stopword4Video,stopword4Figure,MinThresholds,stopWordAPPTv


"""
write to Redis
"""

def writeRedis():
    stopword4Video, stopword4Figure, MinThresholds, stopWordAPPTv=rule_error()
    # videos, celebrity, hot_role = update_data()
    # conR.delete('semantic:error_correct:ConfusingVideo','semantic:error_correct:ConfusingFigure',
    #             'semantic:error_correct:ConfusingRole')
    # conR.delete('semantic:error_correct:ConfusingMusic')
    # conR.set('semantic:error_correct:stopword4Video', stopword4Video)
    # conR.set('semantic:error_correct:stopword4Figure', stopword4Figure)
    # conR.set('semantic:error_correct:MinThresholds', MinThresholds)
    # conR.hmset('semantic:error_correct:ConfusingVideo',videos)
    # conR.hmset('semantic:error_correct:ConfusingFigure',celebrity)
    # conR.hmset('semantic:error_correct:ConfusingRole',hot_role)

writeRedis()




