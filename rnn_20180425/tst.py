# #encoding:utf-8

from pyArango.connection import *

import multiprocessing

def getRelation(name, relation):  # , relation
    '''
    :param name: 人名 邓超
    :param relation: 关系 老婆
    :return: 关系对应的人物  孙俪
    '''
    # relation_ = relation
    if isinstance(name, str):
        name = name.decode('utf-8')

    if isinstance(relation, str):
        relation_ = relation.decode('utf-8')
    else:
        relation_ = relation

    relName = []  # 找出的对应关系名称

    personRelationDict = {u'爸爸':u'father',u'父亲':u'father',u'父':u'father',u'爹':u'father',u'老爸':u'father',
                        u'阿爸':u'father',u'妈妈':u'mother',u'母亲':u'mother',u'母':u'mother',u'娘':u'mother',
                        u'老妈':u'mother',u'阿妈':u'mother',u'儿子':u'son',u'儿':u'son',u'子':u'son',
                        u'女儿':u'daughter',u'爱女':u'daughter',u'闺女':u'daughter',u'孩子':u'child',u'妻子':u'wife',
                        u'妻':u'wife',u'太太':u'wife',u'老婆':u'wife',u'夫人':u'wife',u'媳妇':u'wife',
                        u'娘子':u'wife',u'丈夫':u'husband',u'夫':u'husband',u'老公':u'husband',u'相公':u'husband',
                        u'夫君':u'husband',u'女朋友':u'girlfriend',u'女友':u'girlfriend',u'女票':u'girlfriend',u'绯闻女友':u'girlfriend_gossip',
                        u'男友':u'boyfriend',u'男朋友':u'boyfriend',u'男票':u'boyfriend',u'绯闻男友':u'boyfriend_gossip',u'前女友':u'girlfriend_former',
                        u'前未婚妻':u'fiance_former',u'前男友':u'boyfriend_former',u'前未婚夫':u'fiancee_former',u'前妻':u'wife_former',u'前老婆':u'wife_former',
                        u'前夫':u'husband_former',u'前老公':u'husband_former',u'哥哥':u'brother_e',u'哥':u'brother_e',u'兄长':u'brother_e',
                        u'义兄':u'brother_se',u'堂哥':u'cousin_mme',u'堂兄':u'cousin_mme',u'表哥':u'cousin_fme',u'表兄':u'cousin_fme',
                        u'弟弟':u'brother_y',u'弟':u'brother_y',u'胞弟':u'brother_y',u'义弟':u'brother_sy',u'堂弟':u'cousin_mmy',
                        u'表弟':u'cousin_fmy',u'姐姐':u'sister_e',u'姐':u'sister_e',u'堂姐':u'cousin_mfe',u'表姐':u'cousin_ffe',
                        u'妹妹':u'sister_y',u'妹':u'sister_y',u'堂妹':u'cousin_mfy',u'表妹':u'cousin_ffy',u'祖父':u'grandfather_f',
                        u'爷爷':u'grandfather_f',u'祖母':u'grandmather_f',u'奶奶':u'grandmather_f',u'孙子':u'grandson_f',u'孙':u'grandson_f',
                        u'孙儿':u'grandson_f',u'孙女':u'granddaughter_f',u'孙女儿':u'granddaughter_f',u'外祖父':u'grandfather_m',u'外公':u'grandfather_m',
                        u'姥爷':u'grandfather_m',u'外祖母':u'grandmather_m',u'外婆':u'grandmather_m',u'姥姥':u'grandmather_m',u'外孙':u'grandson_m',
                        u'外孙儿':u'grandson_m',u'外孙女':u'granddaughter_m',u'外孙女儿':u'granddaughter_m',u'伯伯':u'uncle_f',u'伯父':u'uncle_f',
                        u'舅舅':u'uncle_m',u'舅':u'uncle_m',u'婶婶':u'uncle_fw',u'姑妈':u'aunt_fs',u'姑姑':u'aunt_fs',
                        u'舅妈':u'uncle_mw',u'姨妈':u'aunt_ms',u'未婚夫':u'fiancee',u'未婚妻':u'fiance',u'义父':u'adopted_father',
                        u'义母':u'adopted_mother',u'干儿子':u'adopted_son',u'干儿':u'adopted_son',u'义子':u'adopted_son',u'干女儿':u'adopted_daughter',
                        u'干女':u'adopted_daughter',u'义女':u'adopted_daughter',u'继父':u'stepfather',u'继母':u'stepmother',u'继子':u'stepson',
                        u'继女':u'stepdaughter',u'侄子':u'nephew_b',u'外甥':u'nephew_s',u'外甥儿':u'nephew_s',u'侄女':u'niece_b',
                        u'外甥女':u'niece_b',u'外甥女儿':u'niece_b',u'老师':u'teacher',u'师傅':u'teacher',u'师父':u'teacher',
                        u'徒弟':u'student',u'徒':u'student',u'学生':u'student',u'爱徒':u'student',u'弟子':u'student',
                        u'好友':u'friend',u'朋友':u'friend',u'队友':u'teammate',u'搭档':u'partner',u'女婿':u'son_in_law',
                        u'儿媳':u'daughter_in_law',u'儿媳妇':u'daughter_in_law',u'岳父':u'father_in_law',u'岳丈':u'father_in_law',u'丈人':u'father_in_law',
                        u'岳母':u'mother_in_law',u'丈母娘':u'mother_in_law',u'同学':u'classmate',u'同门':u'classmate',u'师姐':u'sister_o_t',
                        u'师兄':u'brother_o_t',u'师妹':u'sister_y_t',u'师弟':u'brother_y_t',u'干爹':u'godfather',u'干妈':u'godmother',
                        u'配偶':u'spouse',u'爱人':u'spouse'}

    if personRelationDict.has_key(relation_):  # 传入参数关系在arangodb的关系字典中

        relation_ = personRelationDict.get(relation_)

        entityAql = 'FOR doc IN entity Filter  doc.formatName =="%s" && doc.label == "figure" ' \
                    'RETURN doc._id' % (name)  # 从实体集合中获取人名的_id
        conn = Connection(arangoURL='http://10.9.201.197:8529')
        db_ = conn['knowledge-graph-test']
        entityRelute = db_.AQLQuery(entityAql, rawResults=True, batchSize=1000000)

        conn.disconnectSession()

        # print '人物在实体集的_id:%s' % (entityRelute)
        # 从关系集合中获取人名对应关系的人物_to id
        for _id  in entityRelute:
            personRelationAql = 'FOR doc IN personRelations Filter doc.relation == "%s" && doc._from == "%s" \
                    RETURN doc._to' % (relation_, _id)

            # print personRelationAql
            personRelationAqlR = db_.AQLQuery(personRelationAql, rawResults=True, batchSize=1000000)
            # print '从关系集合中获取人名对应关系的人物_to id :%s' % (personRelationAqlR)

            # 再从实体集合获取

            for i in personRelationAqlR:
                entityAql = 'FOR doc IN entity Filter  doc._id == "%s" ' \
                            'RETURN doc.formatName' % i
                relute = db_.AQLQuery(entityAql, rawResults=True, batchSize=1000000)
                relName.append(relute[0])

    else:
        relName = []

    # print relute[0]
    print name, relation, relName


class arrango(object):

    def __init__(self,name,search=''):

        if search:
            entityAql = 'FOR doc IN personRelations Filter doc.relation == "%s" && doc._from == "%s" \
                                RETURN doc._to' % (name, search)
        else:
            entityAql = 'FOR doc IN entity Filter  doc.formatName =="%s" && doc.label == "figure" ' \
                        'RETURN doc._id' % (name)  # 从实体集合中获取人名的_id
        conn = Connection(arangoURL='http://10.9.201.197:8529')
        db_ = conn['knowledge-graph-test']
        self.entityRelute = db_.AQLQuery(entityAql, rawResults=True, batchSize=1000000)
        conn.disconnectSession()

    def get(self):
        return self.entityRelute


if __name__ == '__main__':


    pool = multiprocessing.Pool(processes=10)
    for i in xrange(100):
        pool.apply_async(getRelation, (u'邓超', u'老婆',))
    pool.close()
    pool.join()
    print "Sub-process(es) done."



    # print getRelation('邓超', '老婆')
    # print'---------------------------------------------------'
    # print'--                                                -'
    # print'---------------------------------------------------'
    # print getRelation_2('邓超', '老婆', DB=conn)