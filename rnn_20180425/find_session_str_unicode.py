# -*- coding: utf-8 -*-
import re
def find_num_str_unicode(string):
    if type(string)==str:
        num_dict_r = {'零': 0, '一': 1, '二': 2, '两': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9, '十': 10, '百': 100}
        M_r = ['十', '百']
        result = 0
        if '大结局'  in string:
            result = -1
        elif '最后' in string:
            result = -1
        else:
            num = re.findall(".*第(.*)[季集部].*", string)
            l=len(num[0])
            rep = num[0][0:l-2]
            h = len(rep)
            t = ''
            if re.findall('[0-9]',rep):
                if '倒数' in string :
                     result = '-'+rep
                else :
                    result = rep
            elif '十' not in string and '百' not in string and h>3:
                for i in range(h / 3):
                    t += str(num_dict_r[rep[3 * i:3 * (i + 1)]])
                    if '倒数' in string:
                        result = '-'+t
                    else:
                        result = t
            else:
                num_ = 0;i = 0
                while i <=h:
                        if i+3<=h:
                            current = num_dict_r[rep[i:i+3]]
                            if current == '零':
                                # i+=3
                                continue
                            if i+6<=h:
                                next = num_dict_r[rep[i+3:i+6]]
                            else:
                                next = '个'
                            if rep[i+3:i+6] in M_r:
                                num_ = num_ + current*next
                                i+=6
                            else:
                                num_ = num_ + current
                                i+=3
                            result = num_
                        else :
                            break
                if '倒数' in string:
                    if type(result)==str:
                        result = '-'+result
                    else:
                        result = -result
                else:
                    result = result
    else:
        num_dict_u = {u'零': 0, u'一': 1, u'二': 2, u'两': 2, u'三': 3, u'四': 4, u'五': 5, u'六': 6, u'七': 7, u'八': 8, u'九': 9,u'十': 10, u'百': 100}
        M_u = [u'十', u'百']
        result = 0
        if u'大结局' in string:
            result = -1
        elif u'最后' in string:
            result = -1
        else:
            num = re.findall(u".*第(.*)[季集部].*", string)
            rep = num[0]
            h = len(rep)
            t = ''
            if re.findall(u'[0-9]', rep):
                if u'倒数' in string:
                    result = u'-'+rep
                else:
                    result = rep
            elif u'十' not in string and u'百' not in string and h > 1:
                for i in range(h ):
                    t += str(num_dict_u[rep[i]])
                    if u'倒数' in string:
                        result= u'-'+t
                    else:
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
                if u'倒数' in string:
                    if type(result) == str:
                        result = u'-'+result
                    else:
                        result = -result
                else:
                    result = result
    return int(result)

if __name__=='__main__':
    string_r=['第一集','第十集','第十一集','第二十集','第一百二十集','第一百二十一集','第一百集','大结局','最后一集','第10集','第三二一集']
    string_u = [u'第一集', u'第十集', u'第十一集', u'第二十集', u'第一百二十集', u'第一百二十一集', u'第一百集', u'大结局', u'最后一集', u'第10集',u'第三二一集']
    for i in range(len(string_r)):
        result = find_num_str_unicode(string_r[i])
        result2 = find_num_str_unicode('倒数'+string_r[i])
        print result,result2
    for i in range(len(string_u)):
        result = find_num_str_unicode(string_u[i])
        result2 = find_num_str_unicode(u'倒数' + string_u[i])
        print result, result2