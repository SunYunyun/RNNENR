#encoding:utf-8
'''
ac:syy
time:20180119
function:python 处理Excel
 pandas+xlrd+numpy按元素计算批量处理excel所有sheet
'''
import codecs
import os
import pandas as pd
import xlrd
import numpy as np
#import http2server_raw
import traceback #报错
import json
from collections import OrderedDict

import coreControl
#path = unicode(r'E:\学习工作\语义云','utf-8')
#xlsfile = r'basetest-20180125.xlsx'



def baseTestInterface(inPath,outPath):
    '''
    author：syy
    time：20180128
    function：video基础用例单元测试接口

    :param inPath:测试数据路径
    :param outPath:测试结果保存路径

    '''
    book = xlrd.open_workbook(inPath)  #xlrd用于获取每个sheet的sheetname


    with pd.ExcelWriter(outPath) as writer:

        for sheet in book.sheets():#循环每个sheetname
            #print sheet.name

            if sheet.name == u'VIDEO-推荐':#推荐类不测试
                continue

            #print sheet.name
            df = pd.read_excel(xlsfile, sheetname=sheet.name)
            lst = [u'domain', u'intent', u'name', u'category', u'type', u'actor', u'director', u'role',
                   u'tag', u'year', u'area', u'season',u'episode', u'resolution', u'award', u'sub_award',
                   u'language', u'rate', u'relative', u'extra',u'source', u'part', u'term', u'value',u'code']

            colDict = OrderedDict()
            for i in lst:
                colDict.update({i: []})


            #print colDict

            testcase = df['testcase']
            #print type(testcase)
            for txt in testcase :
                #print 'txt',txt
                try:#报错
                    s = time.time()
                    da = coreControl.CoreContro(txt.decode('utf-8'))
                    print time.time()-s
                    da = da.reslutJson
                except:da = u'报错'

                print 'da',da
                #print type(da) str
                if da == u'报错':
                    da = '{}'
                    da = json.loads(da)
                else:da = json.loads(da)
                #print type(da)
                if da == {}:
                    for key in colDict:  # 循环每个返回实体
                        if key == 'code':
                            l = colDict[key]

                            l.append(u'报错')
                            colDict[key] = l
                        else:
                            l = colDict.get(key)
                            l.append('')
                            colDict[key] = l
                    #print u'报错',colDict
                elif  'data' in da:

                    for key in colDict:

                        if key in da['data']:

                            l = colDict[key]

                            l.append(da['data'][key])

                            colDict[key]=l

                        elif key == 'code':
                            l = colDict[key]
                            l.append(da[key])
                            colDict[key] = l
                        elif key in da['data']['semantic']:
                            l = colDict[key]
                            l.append(da['data']['semantic'][key])
                            colDict[key] = l
                        else:
                            l = colDict[key]
                            l.append('')
                            colDict[key]=l
                else:
                    for key in colDict:
                        if key == 'code':
                            l = colDict[key]
                            l.append(da[key])
                            colDict[key] = l
                        else:
                            l = colDict[key]
                            l.append('')
                            colDict[key] = l

            #print 'colDict',colDict

            dfreslut = pd.DataFrame(colDict)#字典转换为DF
            #print dfreslut.head(1)
            #dfreslut.to_excel(writer, sheet_name=sheet.name)
            #break
            dfOri = df[df.columns[0:list(df.columns).index('testcase')+1]]
            #dfreslut1 = pd.concat([testcase,dfreslut],axis = 1)
            dfreslut1 = pd.concat([dfOri, dfreslut], axis=1)#
            reTest = reCompare(dfreslut1, sheet.name)
            # print 'reTest',reTest
            dfreslut1[u'测试结果'] = reTest

            #读取每个sheetname表格内容
            dfreslut1.to_excel(writer, sheet_name=sheet.name,index = False)
            #writer.save()
            #break


def reCompare(df, sheetName):
    '''
    function：基础测试用例测试结果比较
    time:20180130
    :param df:测试结果数据框
    :param sheetName:
    :return:
    '''
    testRes = []
    column = list(df.columns)

    if sheetName == 'VIDEO-QUERY':
        for i in range(df.shape[0]):

            # if df[u'期望intent'][i] != df[u'intent'][i] or df[df[u'期望参数'][i]][i] != df[u'期望参数值'][i]:
            #     testRes.append('FAIL')
            # else:
            #     testRes.append('PASS')
            if type(df[u'期望参数值'][i]) == int and (
                    type(df[df[u'期望参数'][i]][i]) == str or type(df[df[u'期望参数'][i]][i]) == unicode):
                res = str(df[u'期望参数值'][i])
            else:
                res = df[u'期望参数值'][i]  # 集季转换为int型再比较
            if df[u'期望intent'][i] != df[u'intent'][i] or res != res:
                testRes.append('FAIL')
            else:
                testRes.append('PASS')
    elif sheetName == u'category遍历' or sheetName == u'type遍历':
        for i in range(df.shape[0]):

            if df[df.columns[0]][i] != df[column[0].replace(u'期望', '')][i] or df[df.columns[1]][i] != \
                    df[column[1].replace(u'期望', '')][i]:  # yaojia u
                testRes.append('FAIL')
            else:
                testRes.append('PASS')
    elif sheetName == u'extra遍历':
        for i in range(df.shape[0]):
            if df[df.columns[0]][i] in df['name'][i]:
                testRes.append('PASS')
            else:
                testRes.append('FAIL')
    else:
        for i in range(df.shape[0]):
            if sheetName == u'year遍历':
                # print type(df[df.columns[0]][i])

                if type(df[df.columns[0]][i]) == np.int64 and type(df[column[0].replace(u'期望', '')][i]) == unicode:
                    res = str(df[df.columns[0]][i])
                else:
                    res = df[df.columns[0]][i]  # year compare
                # if res == df[column[0].replace(u'期望', '')][i]:
                #     print 11
                # df[column[0].replace(u'期望', '')][i]
                if res != df[column[0].replace(u'期望', '')][i]:
                    testRes.append('FAIL')
                else:
                    testRes.append('PASS')
            else:
                # print type(df[df.columns[0]][i]), type(df[column[0].replace(u'期望', '')][i])
                if df[df.columns[0]][i] != df[column[0].replace(u'期望', '')][i]:
                    testRes.append('FAIL')
                else:
                    testRes.append('PASS')
    # testRes = pd.DataFrame(testRes, columns=[u'测试结果'])
    return testRes


def testInterface(inPath,outPath):
    '''
    author：syy
    time：20180128
    function：video测试接口

    :param inPath:测试数据路径
    :param outPath:测试结果保存路径
    :return:
    '''


    lst = [u'domain', u'intent', u'name', u'category', u'type', u'actor', u'director', u'role',
           u'tag', u'year', u'area', u'season', u'episode', u'resolution', u'award', u'sub_award',
           u'language', u'rate', u'relative', u'extra', u'source', u'part', u'term', u'value', u'code']

    colDict = OrderedDict()
    for i in lst:
        colDict.update({i: []})

    # print colDict
    df = pd.read_excel(inPath,sheet_name=1)####change
    testcase = df['testcase']
    # print type(testcase)
    for txt in testcase:
        print 'txt',txt
        try:  # 报错
            da = coreControl.CoreContro(txt.decode('utf-8'))
            da = da.reslutJson
        except:
            da = u'报错'

        print 'da', da
        # print type(da) str
        if da == u'报错':
            da = '{}'
            da = json.loads(da)
        else:
            da = json.loads(da)
        # print type(da)
        if da == {}:
            for key in colDict:  # 循环每个返回实体
                if key == 'code':
                    l = colDict[key]

                    l.append(u'报错')
                    colDict[key] = l
                else:
                    l = colDict.get(key)
                    l.append('')
                    colDict[key] = l
                    # print u'报错',colDict
        elif 'data' in da:

            for key in colDict:

                if key in da['data']:

                    l = colDict[key]

                    l.append(da['data'][key])

                    colDict[key] = l

                elif key == 'code':
                    l = colDict[key]
                    l.append(da[key])
                    colDict[key] = l
                elif key in da['data']['semantic']:
                    l = colDict[key]
                    l.append(da['data']['semantic'][key])
                    colDict[key] = l
                else:
                    l = colDict[key]
                    l.append('')
                    colDict[key] = l
        else:
            for key in colDict:
                if key == 'code':
                    l = colDict[key]
                    l.append(da[key])
                    colDict[key] = l
                else:
                    l = colDict[key]
                    l.append('')
                    colDict[key] = l

    # print 'colDict',colDict

    dfreslut = pd.DataFrame(colDict)  # 字典转换为DF

    dfreslut = pd.concat([testcase, dfreslut], axis=1)  #
    dfreslut.to_excel(outPath, index = False)

# if __name__ == '__main__':
#
#     for i in xrange(5):
#
#         xlsfile = r'basetest-20180125.xlsx'
#         outPath = 'newbug%d.xls'%i
#         baseTestInterface(xlsfile,outPath)#basetest
#         #testInterface(xlsfile, outPath)
if __name__ == '__main__':
    import time
    s = time.time()
    xlsfile = r'basetest-20180125.xlsx'
    outPath = 'newbug0.xls'
    baseTestInterface(xlsfile,outPath)#basetest
    e = time.time()
    print e - s

