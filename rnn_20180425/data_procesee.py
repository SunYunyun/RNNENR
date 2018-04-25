#encoding:utf-8
import codecs
import re
import random
import collections
import numpy as np
import time

def _character_separation(issue):

    '''
    :param issue: '我 想 看 上 世 纪 90 年 代 的 电 影'
    :return: ['我', '想' ,'看', '上', '世'. '纪'. 'DIGTDIGT', '年', '代', '的', '电', '影']
    '''
    s=[]
    issue = issue.split(' ')
    for value in issue:
        if re.findall(ur"[0-9]+",value):
            digit_len = len(value)
            flag = 0
            _s = ''
            while (flag < digit_len):
                _s = _s + 'DIGIT'
                flag = flag + 1
            s.append(_s)
        else:
            s.append(value)
    return s


def command_labels_dict(path,flag):
    '''
    :param path: text path
    :param flag: flag = 'command' means start from line 1.txt ,programm read command, or read labels
    :return: commands or labels dict
    '''

    command_dict = {}
    if path:

        f = codecs.open(path).readlines()
        sflag=0
        if flag == 'commands':
            sflag = 1

        for i in f:
            if sflag%2 == 0:
                sflag = sflag + 1
                continue

            text = i.rstrip()
            text_seg = _character_separation(text)
            text_seg = [seg.decode('utf-8') for seg in text_seg]

            for seg in text_seg:
                if seg not in command_dict.keys():
                    command_dict[seg] = 1
                else: command_dict[seg] = command_dict[seg]+1
            sflag = sflag+1

        fw = codecs.open(flag+'.dict','w','utf-8')
        for key,value in command_dict.items():
            fw.write(key+' '+str(value)+'\n')
        print 'write in text over'

def sort_by_value(d):
    items=d.items()
    backitems=[[v[1],v[0]] for v in items]
    backitems.sort()
    _dict = collections.OrderedDict()
    for i in range(0,len(backitems)):
        _dict[backitems[i][0]] = backitems[i][1]
    return _dict

def find_num(issue):
    _index={}
    num_index = re.findall(ur"[0-9]+",issue)
    pre_ = ''
    for j in range(len(num_index)):
        if j > 0:
            pre_ = num_index[j - 1]
        if num_index[j] in pre_:
            issue_ = issue
            # issue_ = issue_.replace(pre_, '')
            issue_ = issue_[:_index[pre_]]+issue_[_index[pre_]+len(pre_):]
            tmp = num_index[j]
            if num_index[j] in  _index:
                tmp = num_index[j]+'_'
            _index[tmp] = issue_.index(num_index[j]) + len(pre_)
            continue
        i = num_index[j]
        _index[i] = issue.index(i)
    repat = re.compile(ur"[0-9]+")
    isu = repat.split(issue)

    if '' in isu:#20171227 d
        isu.remove('')

    pre=''
    for i in range(len(isu)):
        if i >0:
            pre = isu[i-1]
        if isu[i] in pre:
            issue_ = issue
            if isu[i]!=pre:
                issue_ = issue_.replace(pre,'')
                _index[isu[i]] = issue_.index(isu[i]) + len(pre) - 1
            elif isu[i] == pre:
                m = re.search(pre, issue_)
                issue_ = issue_[:m.start(0)]+issue_[m.end(0):]
                tisu = isu[i]+'_'
                _index[tisu] = issue_.index(isu[i])+len(pre)-1
            continue
        _index[isu[i]] = issue.index(isu[i])

    _index = sort_by_value(_index)
    return _index

def find_char(issue):
    _index = {}
    num_index = re.findall(ur"[A-Za-z]+", issue)
    for i in num_index:
        _index[i] = issue.index(i)
    repat = re.compile(ur"[A-Za-z]+")
    isu = repat.split(issue)
    for i in isu:
        _index[i] = issue.index(i)

    _index = sort_by_value(_index)
    return _index

def character_separation(issue):
    s='';s_num=''
    if re.findall(ur"[0-9]+",issue):
        dic_ = find_num(issue)
        for key,value in dic_.items():
            if value.find('_')!=-1:
                value = value.rstrip('_')
            if re.findall(ur"[0-9]+",value):
                digit_len = len(value)
                flag = 0
                _s = ''
                while (flag < digit_len):
                    _s = _s + 'DIGIT'
                    flag = flag + 1
                s_num = s_num + " " + value
                s = s + " " + _s
            else:
                if re.findall(ur"[A-Za-z]+", value):
                    _dic_ = find_char(value)
                    for key, value in _dic_.items():
                        if re.findall(ur"[A-Za-z]+", value):
                            s = s + " " + value
                            s_num = s_num + " " + value
                        else:
                            t = 0
                            k = 3
                            l = value.__len__()
                            while (k <= l):
                                s = s + ' ' + value[t:k]
                                s_num = s_num + " " + value[t:k]
                                t = k
                                k = k + 3

                else:
                    t=0
                    k=3
                    l = value.__len__()
                    if l <3:
                        s = s + ' ' + value[t:k]
                        s_num = s_num + ' ' + value[t:k]
                    else:
                        while(k<=l):
                            s = s+' '+value[t:k]
                            s_num = s_num + ' ' + value[t:k]
                            t = k
                            k = k + 3
    elif re.findall(ur"[A-Za-z]+",issue):
        dic_ = find_char(issue)
        for key,value in dic_.items():
            if re.findall(ur"[A-Za-z]+",value):
                s = s+" "+value
            else:
                t=0
                k=3
                l = value.__len__()
                while(k<=l):
                    s = s+' '+value[t:k]
                    t = k
                    k = k + 3
    else:
        issue = issue.rstrip()
        l = issue.__len__()
        t=0
        k=3
        while(k<=l):
            s = s+' '+issue[t:k]
            t = k
            k = k + 3
    return s[1:],s_num[1:]


def character_separation_unicon(issue):
    s='';s_num=''
    if re.findall(ur"[0-9]+",issue):
        dic_ = find_num(issue)
        for key,value in dic_.items():
            if value.find('_')!=-1:
                value = value.rstrip('_')
            if re.findall(ur"[0-9]+",value):
                digit_len = len(value)
                flag = 0
                _s = ''
                while (flag < digit_len):
                    _s = _s + 'DIGIT'
                    flag = flag + 1
                s = s+" "+_s
                s_num = s_num + " " + value
            else:
                if re.findall(ur"[A-Za-z]+", value):
                    _dic_ = find_char(value)
                    for key, value in _dic_.items():
                        if re.findall(ur"[A-Za-z]+", value):
                            s = s + " " + value
                            s_num = s_num + " " + value
                        else:
                            t=0
                            k=1
                            l = value.__len__()
                            while(k<=l):
                                s = s+' '+value[t:k]
                                s_num = s_num +' '+value[t:k]
                                t = k
                                k = k + 1
                else:
                    t=0
                    k=1
                    l = value.__len__()
                    if l <3:
                        s = s + ' ' + value[t:k]
                        s_num = s_num + ' ' + value[t:k]
                    else:
                        while(k<=l):
                            s = s+' '+value[t:k]
                            s_num = s_num + ' ' + value[t:k]
                            t = k
                            k = k + 1

    elif re.findall(ur"[A-Za-z]+",issue):
        dic_ = find_char(issue)
        for key,value in dic_.items():
            if re.findall(ur"[A-Za-z]+",value):
                s = s+" "+value
                s_num = s_num + " " + value
            else:
                t=0
                k=1
                l = value.__len__()
                while(k<=l):
                    s = s+' '+value[t:k]
                    s_num = s_num + " " + value[t:k]
                    t = k
                    k = k + 1
    else:
        issue = issue.rstrip()
        l = issue.__len__()
        t=0
        k=1
        while(k<=l):
            s = s+' '+issue[t:k]
            t = k
            k = k + 1
    return s[1:],s_num[1:]

def ear(src):
    src = src.replace('上世纪','')
    _ear_={'20年代': '1920至1929', '30年代': '1930至1939', '40年代': '1940至1949', '50年代': '1950至1959','60年代':'1960至1969','70年代':'1970至1979','80年代':'1980至1989','90年代':'1990至1999',
           '二零年代':'1920至1929','三零年代':'1930至1939','四零年代':'1940至1949','五零年代':'1950至1959','六零年代':'1960至1969','七零年代':'1970至1979','八零年代':'1980至1989','九零年代':'1990至1999',
           '二十年代': '1920至1929','三十年代': '1930至1939','四十年代': '1940至1949', '五十年代': '1950至1959','六十年代': '1960至969','七十年代': '1970至1979','八十年代': '1980至1989','九十年代': '1990至1999',
    }
    if src in _ear_.keys():
        return _ear_[src]
    else:return ''


def verfy_num(key,value):
    if ',' in value:
        return '',''
    elif value =='4K':
        return 'resolution',value
    elif value in ['电影年度榜单', 'FIRST青年电影展','第86日剧学院赏']:
        return 'award', value
    elif key == 'episode' and value.find('集')!=-1:
        return key,find_num_str_unicode(value)
    elif key =='moviePlayDuration' and (value.find('小时')!=-1 or value.find('分钟')!=-1):
        return key,remove_chinese(value)
    elif key == 'season' and value.find('部')!=-1 or value.find('季')!=-1:
        return key, find_num_str_unicode(value)
    elif value.find('年代')!=-1:
        value = ear(value)
        return 'year',value
    elif value =='口碑比较好' or value.find('评价')!=-1 :
        return 'tag','好评'
    elif value.find('高分')!=-1 or value.find('评分比较高') != -1:
        return 'tag','高分'
    elif value.find('好评')!=-1 :
        return 'tag', '好评'
    elif value.find('口碑')!=-1:
        return 'tag','好评'
    elif value.find('分')!=-1:
        if value in ['最佳分镜','评分最高的英美剧','评分最低的外语电影','评分最高的大陆电视剧','评分最高的动画片','评分最高的韩剧','评分最高的英美剧']:
            return 'sub_award',value
        else:return 'rate',remove_chinese(value)
    elif re.findall(ur"[1-9]{1,1}\.\d{0,1}",value) or re.findall(r"[1-9]{1,1}\.\d{0,1}",value):
        return 'rate',remove_chinese(value)
    elif value.find('年代')!=-1 or value.find('年')!=-1:
        if value in ['年轻视野大奖','年度被忽略影片','60周年纪念奖','55周年纪念奖','青年电影奖别奖']:
            return 'sub_award',value
        else:
            s = remove_chinese(value)

            #if s:
            if s != '':#--20180111 s
                if int(s) == 0:
                    s = str(2000) #--20180111 s
                elif int(s) <= 18:
                    s = str(2000 + s)
                elif s > 18 and s < 100:
                    s = str(1900 + s)
            if not s:
                return key,value
            #else:return 'year',s
            else:
                if '年' in value and '后'in value and '后年' not in value:##--20180111 s
                    return 'year',str(s) + '年后'
                elif '年' in value and '前'in value and '前年' not in value:
                    return 'year', str(s) + '年前'##--20180111 s
                else:
                    return 'year',str(s)
    elif re.findall(ur"[0-9]+",value) and '版' in value:
        # dic_ = re.findall(ur"[0-9]+",value)
        return 'year', remove_chinese(value)
        # dic_ = [val.encode('utf-8') for val in dic_ if int(val.encode('utf-8'))<10 and int(val.encode('utf-8'))>0 and val!='00']
    #     if dic_:
    #         return 'rate',remove_chinese(value)
    #     else:return 'year',remove_chinese(value)
    # elif re.findall(r'(零|一|二|三|四|五|六|七|八|九)+',value):
    #     return 'year',remove_chinese(value)
    # elif re.findall(ur'[零|一|二|三|四|五|六|七|八|九]+',value):
    #     return 'year', remove_chinese(value)
    else:
        return '',''

# def remove_chinese(issue):
#     ymd = {'去年': -1, '前年': -2,'今年':0,'后年':2,'明年':1}#jia20180111 s
#     if not re.findall('[0-9]+',issue):
#         if issue in ymd:
#             return str(int(time.strftime('%Y',time.localtime(time.time())))+ymd[issue]) #add int to str 20180113 s
#         #else:return '' s20180111
#     s = ''
#     flag=0
#     common_used_numerals_tmp = {'零': 0, '一': 1, '二': 2, '两': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9,
#                                 '十': 10, '百': 100, '千': 1000, '万': 10000, '亿': 100000000}
#     if re.findall(ur"[0-9]+", issue):
#         dic_ = find_num(issue)
#         for key, value in dic_.items():
#             if value =='.':
#                 s = s+'.'
#                 flag=1
#             elif not value.isdigit() :
#                 continue
#             else:
#                 s = s+value
#     # elif issue in common_used_numerals_tmp:
#     #     s = common_used_numerals_tmp[issue]
#     else:
#         i = 0
#         while (i < len(issue)):  # --20180111 s
#             if issue[i:i + 3] in common_used_numerals_tmp:
#                 s = s + str(common_used_numerals_tmp[issue[i:i + 3]])
#             i = i + 3
#
#
#     if s == '':
#         return ''  # --20180111 s
#
#     if flag:
#         s = float(s)
#     else:s = int(s)
#     return s
def remove_chinese(issue):
    ymd = {'去年': -1, '前年': -2,'今年':0,'后年':2,'明年':1}#jia20180111
    if not re.findall('[0-9]+',issue):
        if issue in ymd:
            return str(int(time.strftime('%Y',time.localtime(time.time())))+ymd[issue])# add from int to str 20180113 s
        #else:return '' #20180111
    s = ''
    flag=0
    common_used_numerals_tmp = {'零': 0, '一': 1, '二': 2, '两': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9,
                                '十': 10, '百': 100, '千': 1000, '万': 10000, '亿': 100000000}
    if re.findall(ur"[0-9]+", issue):
        dic_ = find_num(issue)
        for key, value in dic_.items():
            if value =='.':
                s = s+'.'
                flag=1
            elif not value.isdigit() :
                continue
            else:
                s = s+value
    else:#issue in common_used_numerals_tmp:
        i = 0
        while (i < len(issue)):#20180111
            if issue[i:i+3] in common_used_numerals_tmp:#20180111
                s = s + str(common_used_numerals_tmp[issue[i:i+3]])#20180111
            i = i + 3#20180111

    if s == '':
        return ''
    if flag:
        s = float(s)
    else:s = int(s)
    if s<18:
        s = s+2000
    elif s<100:s = s + 1900
    return str(s)


def is_chinese(uchar):

    """判断一个unicode是否是汉字"""

    if uchar >= u'/u4e00' and uchar <= u'/u9fa5':
        return True
    else:
        return False

def find_num_str_unicode(string):
    result =  0
    if type(string)==str:
        string = string.decode('utf-8')
    else:
        string = string
    if u'大结局' in string:
        result = -1
    elif string.isdigit():
        result = string
    elif re.findall(u'[0-9]|零|一|二|两|三|四|五|六|七|八|九|十|百|千', string):
        num_dict_u = {u'零': 0, u'一': 1, u'二': 2, u'两': 2, u'三': 3, u'四': 4, u'五': 5, u'六': 6, u'七': 7, u'八': 8, u'九': 9,u'十': 10, u'百': 100}
        M_u = [u'十', u'百']
        num = re.findall(u'[0-9]+|[零|一|二|两|三|四|五|六|七|八|九|十|百|千|万|]+', string)
        if num:
            rep = num[0]
            # print rep
            h = len(rep)
            t = ""
            if re.findall(u'[0-9]', rep):
                result = rep
            elif re.findall(u'[千|万]+',rep):
                result = -1
            elif u'十' not in string and u'百' not in string and h > 1:
                for i in range(h):
                    t += str(num_dict_u[rep[i]])
                    result = t
            else:
                num_ = 0
                i = 0
                while i <h:
                    if i <=h-1:
                        current = num_dict_u[rep[i]]
                        if current == u'零':
                            continue
                        if i+1 <=h-1:
                            sp = rep[i+1]
                            next = num_dict_u[rep[i+1]]
                        else:
                            sp = u'个'
                        if sp in M_u:
                            num_ = num_ + current * next;i += 2
                        else:
                            num_ = num_ + current;i+=1
                        result = num_
                    else:
                        break
        else:
            result = 1000000000
    if u"最后"in string or u"倒数" in string or u"最新" in string or u"最近" in string :
        result = (-1)*int(result)
    return int(result)

def load_dict_commmand_lable(cpath,lpath):

    cm_dict={}
    l_dict={}
    dic={}
    if cpath and lpath:
        with codecs.open(cpath,'r','utf-8') as fn:
            f = fn.readlines()
            for i in f:
                i = i.rstrip()
                i = i.split(' ')
                cm_dict[i[0]] = int(i[1])
        with codecs.open(lpath,'r','utf-8') as ln:
            lf = ln.readlines()
            for il in lf:
                il = il.rstrip()
                il = il.split(' ')
                l_dict[il[0]] = int(il[1])

    dic['labels2idx']=l_dict
    dic['words2idx'] = cm_dict
    return dic

def check_char(words):
    if words:
        if re.findall(u"\s+",words):
            words = words.split(' ')
            words = ''.join(words)

    return words


def shuffle(lol, seed):
    '''
    lol :: list of list as input
    seed :: seed the shuffling

    shuffle inplace each list in the same order
    '''
    for l in lol:
        random.seed(seed)
        random.shuffle(l)

from config_database import clients

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

        entityRelute = clients.query(name)

        # entityAql = 'FOR doc IN entity Filter doc.formatName =="%s" && doc.label == "figure" RETURN doc._id' % (name)
        # entityRelute = db.AQLQuery(entityAql, rawResults=True, batchSize=1000000)
        # conn.disconnectSession()
        # print '人物在实体集的_id:%s' % (entityRelute)
        # 从关系集合中获取人名对应关系的人物_to id
        for _id  in entityRelute:
            # personRelationAql = 'FOR doc IN personRelations Filter doc.relation == "%s" && doc._from == "%s" RETURN doc._to' % (relation_, _id)
            # # print personRelationAql
            # personRelationAqlR = db.AQLQuery(personRelationAql, rawResults=True, batchSize=1000000)
            personRelationAqlR = clients._query(relation_,_id)
            # print '从关系集合中获取人名对应关系的人物_to id :%s' % (personRelationAqlR)

            # 再从实体集合获取

            for i in personRelationAqlR:
                # entityAql = 'FOR doc IN entity Filter doc._id == "%s" RETURN doc.formatName' % i
                #
                # relute = db.AQLQuery(entityAql, rawResults=True, batchSize=1000000)
                relute = clients._query_(i)
                relName.append(relute[0])

    else:
        relName = []

    # print relute[0]
    return name, relation, relName

def words2idx_commands_labels(dic,cpath):

    cm_dict = dic['words2idx']
    l_dict = dic['labels2idx']
    cm_idx = []
    l_idx=[]
    with codecs.open(cpath,'r','utf-8') as fn:
        f = fn.readlines()
        flag=0
        for i in f:
            i = i.rstrip()
            if flag%2 == 0:
                issue = _character_separation(i)
                cm_idx.append(map(lambda x: cm_dict[x], issue))
            else:
                i = i.split(' ')
                l_idx.append(map(lambda x: l_dict[x], i))
            flag = flag+1

    # train_lex = cm_idx[0:3000]; train_ne=[];train_y=l_idx[0:3000]
    # valid_lex = cm_idx[3000:3276]; valid_ne=[]; valid_y = l_idx[3000:3276]
    # test_lex = cm_idx[3276:]; test_ne=[]; test_y = l_idx[3276:]

    shuffle([cm_idx, [], l_idx], 345)

    train_lex = cm_idx[0:9596]; train_ne = [];train_y = l_idx[0:9596]
    # valid_lex = cm_idx[5000:5100]; valid_ne = [];valid_y = l_idx[5000:5100]
    valid_lex = []; valid_ne = [];valid_y = []
    test_lex = cm_idx[9596:];test_ne = [];test_y = l_idx[9596:]
    return train_lex,train_ne,train_y,valid_lex,valid_ne,valid_y,test_lex,test_ne,test_y

def trian_test_command_labels_numeric():

    path = '/home/changhong/PycharmProjects/intention-rnn/is13-master/data/data-train-test-20171016.txt'#final_data_clean20170801.txt'
    dic = load_dict_commmand_lable('/home/changhong/PycharmProjects/intention-rnn/is13-master/data/commands.dict',
                             '/home/changhong/PycharmProjects/intention-rnn/is13-master/data/labels.dict')
    train_lex, train_ne, train_y, valid_lex, valid_ne, valid_y, test_lex, test_ne, test_y = words2idx_commands_labels(dic,
                                                                                                               path)
    return train_lex, train_ne, train_y, valid_lex, valid_ne, valid_y, test_lex, test_ne, test_y, dic


if __name__ == '__main__':

    # path = '/home/changhong/PycharmProjects/intention-rnn/is13-master/data/final_data_clean20170714.txt'
    # #
    # command_labels_dict(path,'labels')
    # command_labels_dict(path, 'commands')
    # #
    # commandPath='commands.dict'
    # labelsPath='labels.dict'
    # #
    # dic = load_dict_commmand_lable(commandPath,labelsPath)
    #
    # path = '/home/changhong/PycharmProjects/intention-rnn/is13-master/data/final_data_clean20170714.txt'
    # train_lex, train_ne, train_y, valid_lex, valid_ne, valid_y, test_lex, test_ne, test_y = words2idx_commands_labels(dic,path)


    # trian_test_command_labels_numeric()
    # fn = codecs.open('/home/changhong/PycharmProjects/intention-rnn/is13-master/data/test.csv', 'r', 'utf-8')
    # for i_ in fn:
    #     # i_ = i_.rstrip()
    #     i_='来一个AB片'
    #     print i_
    #     if isinstance(i_, unicode):
    #         i_ = character_separation_unicon(i_)
    #     elif isinstance(i_,str):
    #         i_ = character_separation(i_)
    #     print i_

    # print check_char('我要刚 ')
    # s,k = character_separation('来一部豆瓣评分9.0以上的爱情片')
    # # print s,'<>',k
    # check_num_('评分9000.0以上')
    #
    # # verfy_num('10我要')
    # num_index = re.findall(ur"[0-9]+", '1.93部豆')
    # print num_index

    # print remove_chinese('900年')
    # entityAql = 'For doc In entity Filter "%s" In doc.formatNames and doc.status == "active" RETURN doc' % (self.name)
    #
    # scoreDocs = db.AQLQuery(entityAql, rawResults=True, batchSize=10000)
    #
    # # p = [scoreDoc.get(self.get_words).encode('utf-8') for scoreDoc in scoreDocs]
    #
    # for _id in scoreDocs:
    #     print _id.get('label')

    print getRelation('邓超', '媳妇')