#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pyArango.connection import *
import redis
from pymongo import MongoClient

class config():

    dev_address = 208


    arrangoPath = 'http://10.9.46.114:8529'
    mongo_path = '10.9.201.190'

    arrangoName = 'knowledge-graph-test'
    mongo_port = 27017
    redis_ip = '10.9.46.102'
    redis_port = 6379
    redis_db_c = 1
    redis_db_ec = 15

    if dev_address == 208:

        arrangoPath = 'http://10.66.1.208:11003'
        mongo_path = '10.66.1.208'
        arrangoName = 'knowledge-graph-test'
        mongo_port = 27017
        redis_ip = '10.66.1.208'
        redis_port = 6379
        redis_db_c = 15
        redis_db_ec = 15

    elif dev_address == 12:
        mongo_path = '10.66.1.153'
        mongo_port = 80
        arrangoPath = 'http://10.66.1.133:8529'
        arrangoName = 'SEMANTIC_KG'
        # redis_ip = 'http://10.66.2.13'
        # redis_port = 6379
        # redis_db_ec = 15
        # redis_db_c = 15
        redis_ip = '10.66.1.208'
        redis_port = 6379
        redis_db_c = 15
        redis_db_ec = 15


class clients():
    conn = []
    if config.dev_address == 102 :
        conn = Connection(arangoURL=config.arrangoPath,username='tester',password=123456)
    else:
        conn = Connection(arangoURL=config.arrangoPath)
    db = conn[config.arrangoName]

    @staticmethod
    def query(name):
        entityAql = 'FOR doc IN entity Filter doc.formatName =="%s" && doc.label == "figure" RETURN doc._id' % (name)
        entityRelute = clients.db.AQLQuery(entityAql, rawResults=True, batchSize=1000000)

        return entityRelute

    @staticmethod
    def _query(relation,id):
        personRelationAql = 'FOR doc IN personRelations Filter doc.relation == "%s" && doc._from == "%s" \
                            RETURN doc._to' % (relation, id)
        personRelationAqlR = clients.db.AQLQuery(personRelationAql, rawResults=True, batchSize=1000000)

        return personRelationAqlR

    @staticmethod
    def _query_(i):
        entityAql = 'FOR doc IN entity Filter doc._id == "%s" RETURN doc.formatName' % i

        relute = clients.db.AQLQuery(entityAql, rawResults=True, batchSize=1000000)
        return relute

    @staticmethod
    def query_utils(command):
        entityAql = 'For doc In entity Filter "%s" In doc.formatNames and doc.status == "active" RETURN doc' % (command)
        scoreDocs = clients.db.AQLQuery(entityAql, rawResults=True, batchSize=10000)
        return scoreDocs

    @staticmethod
    def ec_queryResult_video(name,label):
        aql = 'For doc In entity Filter doc.label== "%s" && doc.hot==true and doc.status == "active" Return %s' %(name,label)
        queryResult_video = clients.db.AQLQuery(aql, rawResults=True, batchSize=20000)
        return queryResult_video

    aql = 'For doc In entity Filter doc.label=="figure" && doc.hot==true && doc.status=="active" Return doc.formatNames'

    @staticmethod
    def query_formates(name,num):
        aql = 'for doc in entity filter "%s" in doc.formatNames and doc.status == "active" limit %s return doc' % (name, num)
        if num == -1:
            aql = 'for doc in entity filter "%s" in doc.formatNames and doc.status == "active" return doc' % (name)
            num = 1000
        formatNames = clients.db.AQLQuery(aql, rawResults=True, batchSize=num)
        return formatNames

    @staticmethod
    def query_plot():
        '''
        台词剧情搜索
        :return:
        '''
        aql = 'for doc in entity filter doc.formatClassicalLines != null return {"formatName":doc.formatName,' \
              '"formatClassicalLines":doc.formatClassicalLines,"formatScenes":doc.formatScenes}'  # classicalLines formatClassicalLines

        sorces =  clients.db.AQLQuery(aql, rawResults=True, batchSize=1000)
        return sorces
    # @staticmethod
    # def ec_queryResult_video():
    #     aql = 'For doc In entity Filter doc.label=="film" && doc.hot==true && doc.status=="active" Return doc.formatNames'
    #     queryResult_video = clients.db.AQLQuery(aql, rawResults=True, batchSize=20000)
    #     return queryResult_video

class redis_clients():

    conR = redis.Redis(host=config.redis_ip, port=config.redis_port, db=config.redis_db_ec)

    @staticmethod
    def redis_get(name):
        return redis_clients.conR.get(name)

    @staticmethod
    def redis_hmt(redisName, suggest):
        return redis_clients.conR.hmget(redisName, suggest)

    @staticmethod
    def redis_set(name,stopword4Video):
        return redis_clients.conR.set(name, stopword4Video)


class mongo_ec():

    mongoClient = MongoClient(host=config.mongo_path, port=config.mongo_port)

    if config.dev_address == 102 or config.dev_address == 208:
        db_mongo = mongoClient.MovieKnowledgeMap
    else:
        db_mongo=mongoClient.semantic_normal
        db_mongo.authenticate(name='semanticNormalUser', password='semanticAdminUser20180118')

    correct_db = db_mongo.error_logging
    wrong_db = db_mongo.error_fail

    @staticmethod
    def ec_insert(name):
        mongo_ec.correct_db.insert(name)

    @staticmethod
    def ec_wrong_insert(name):
        mongo_ec.wrong_db.insert(name)


class arrango2redis():

    redis_conn_pool = redis.ConnectionPool(host=config.redis_ip, port=config.redis_port, db=config.redis_db_c, decode_responses=True)
    r = redis.Redis(connection_pool=redis_conn_pool)

    @staticmethod
    def redis_verify(index,name):
      return arrango2redis.r.hexists(index,name)


if __name__ == '__main__':

    print arrango2redis.redis_verify('figure','周星驰')