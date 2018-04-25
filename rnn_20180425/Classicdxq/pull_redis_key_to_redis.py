# encoding:utf-8
import redis

# redis链接
# source redis connection
redis_conn_pool_1 = redis.ConnectionPool(host='10.9.46.102', port=6379, db=1, decode_responses=True)
r1 = redis.Redis(connection_pool=redis_conn_pool_1)
# target redis connection
# redis_conn_pool_2 = redis.ConnectionPool(host='127.0.0.1', port=6378, db=15, decode_responses=True)
# r2 = redis.Redis(connection_pool=redis_conn_pool_2)
#
# # redis_conn_pool_2 = redis.ConnectionPool(host='10.66.1.208', port=6379, db=15, decode_responses=True)
# # r2 = redis.Redis(connection_pool=redis_conn_pool_2)
#
# # redis keys
# # r1_keys = ['film', 'figure', 'role', 'del_film',
# #            'del_figure', 'del_role', 'common_words']
#
# r1_keys = ['sports_competition', 'sports_event', 'sports_team','stock_name','stock_code']
#
#
# i = 0.
# for key in r1_keys:
#     for str_ in r1.hkeys(key):
#         if not r2.hexists(key, str_):
#             r2.hset(key, str_, '')
#         i += 1
#         print i

# r1.hset('film', u'哆啦A梦', '')#添加‘谍战
# r1.hdel('common_words', u'呆头呆脑')#删除西甲
print r1.hexists('film', u'十二生肖')#查询西甲
