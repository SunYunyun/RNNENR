# -*- coding:utf-8 -*-
from pyArango.connection import *
import redis

# arango链接
conn = Connection(arangoURL='http://10.9.46.114:8529', username='tester', password='123456')
arangodb = conn['knowledge-graph-test']

# redis链接
redis_conn_pool = redis.ConnectionPool(host='10.9.46.102', port=6379, db=1, decode_responses=True)
r = redis.Redis(connection_pool=redis_conn_pool)

area = ['sports_competition', 'sports_event', 'sports_team','stock_name','stock_code']

# print len(area)

for i in xrange(len(area)):
    # entityAql = 'For doc In entity Filter "%s" In doc.formatNames and doc.status == "active" RETURN doc.formatNames'
    # entityAql = 'let names = (for doc in entity filter doc.formatName == "周星驰" and doc.label == "%s" and doc.status == "active" ' \
    #             'return doc.formatNames) return append([],flatten(names),true)' % area[i]
    entityAql = 'let names = (for doc in entity filter doc.label == "%s" and doc.status == "active" ' \
                'return doc.formatNames) return append([],flatten(names),true)' % area[i]

    entityResult = arangodb.AQLQuery(entityAql, rawResults=True, batchSize=10000)

    # print entityResult[0]
    # print len(set(entityResult[0]))
    for temp_str in set(entityResult[0]):
        # if not r.hexists("all_formatName", temp_str):
        #     r.hset("all_formatName", temp_str, '')
        #     print temp_str

        if not r.hexists(area[i], temp_str):
            r.hset(area[i], temp_str, '')
            print temp_str
