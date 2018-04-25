#encoding:utf-8
import re


def find_jishu(string):
    org_string = string
    data = re.findall(u"(第([0-9]|零|一|两|二|三|四|五|六|七|八|九|十|百|千|万)*(季|集|期|部))", string)
    data_jishu = data[0][0]
    idx = org_string.index(data_jishu)
    split_str = org_string[idx - 2:idx]
    if split_str == u"倒数":
        data_jishu = split_str + data_jishu
    else:
        data_jishu = data_jishu
    string = string.replace(data_jishu, "")
    return data_jishu, string


def find_zuihou(string):
    res = re.findall(u"(最后([0-9]|零|一|两|二|三|四|五|六|七|八|九|十|百|千|万)*(集|季|期|部))", string)
    data_zuihou = res[0][0]
    string = string.replace(data_zuihou, "")
    return data_zuihou, string


def find_daoshu(string):
    res = re.findall(u"(倒数([0-9]+|[零|一|两|二|三|四|五|六|七|八|九|十|百|千|万]+)*(集|季|期|部))", string)
    data_daoshu = res[0][0]
    string = string.replace(data_daoshu, "")
    return data_daoshu, string


def find_zuixin(string):
    res = re.findall(u"(最新([0-9]|零|一|两|二|三|四|五|六|七|八|九|十|百|千|万)*(集|季|期|部))", string)
    data_zuixin = res[0][0]
    string = string.replace(data_zuixin, "")
    return data_zuixin, string


def find_zuijin(string):
    res = re.findall(u"(最近([0-9]|零|一|两|二|三|四|五|六|七|八|九|十|百|千|万)*(集|季|期|部))", string)
    data_zuijin = res[0][0]
    string = string.replace(data_zuijin, "")
    return data_zuijin, string


def find_last(string):
    res = re.findall(u"(([0-9]+|[零|一|两|二|三|四|五|六|七|八|九|十|百|千|万]+)*(集|季|期|部))", string)
    data_last = res[-1][0]
    string = string.replace(data_last, "")
    return data_last, string


# def find_jishu_2(string):  # 20171225
#     org_string = string
#     data_jishu = ""
#     data = re.findall(u"(第([0-9]+|零|一|两|二|三|四|五|六|七|八|九|十|百|千|万|十万|百万)+)", string)
#     data_jishu = data[0][0]
#     idx = org_string.index(data_jishu)
#     split_str = org_string[idx - 2:idx]
#     if split_str == u"倒数":
#         data_jishu = split_str + data_jishu
#     else:
#         data_jishu = data_jishu
#     string = string.replace(data_jishu, "")
#     return data_jishu, string


def find_name(string):

    data_result = []
    if u"倒数" in string and string[string.index(u"倒数") + 1] != u"第":
        if re.findall(u"(倒数([0-9]+|[零|一|两|二|三|四|五|六|七|八|九|十|百|千|万]+)*(集|季|部|期))", string):
            T = True
        else:
            T = False
        while T is True:
            data_daoshu, string = find_daoshu(string)
            data_result.append(data_daoshu)
            if re.findall(u"(倒数([0-9]+|[零|一|两|二|三|四|五|六|七|八|九|十|百|千|万]+)*(集|季|部|期))", string):
                T = True
            else:
                break
    # elif u"最近更新" in string and string[string.index(u"最近更新") + 1]  is  u"的":
    elif u"最近更新的" in string:
        res = re.findall(u"(最近更新的([0-9]|零|一|两|二|三|四|五|六|七|八|九|十|百|千|万)*(季|集|期|部))", string)
        if res:
            ss = res[0][0]
            data_result.append(ss)
            string = string.replace(ss, "")
    elif u"最近更新" in string:
        res = re.findall(u"(最近更新([0-9]|零|一|两|二|三|四|五|六|七|八|九|十|百|千|万)*(季|集|期|部))", string)
        if res:
            ss = res[0][0]
            data_result.append(ss)
            string = string.replace(ss, "")
    if re.findall(u"(第([0-9]|零|一|两|二|三|四|五|六|七|八|九|十|百|千|万)*(季|集|期|部))", string):
        T = True
    else:
        T = False
    while T is True:
        data_jishu, string = find_jishu(string)
        data_result.append(data_jishu)
        if re.findall(u"(第([0-9]|零|一|两|二|三|四|五|六|七|八|九|十|百|千|万)*(季|集|期|部))", string):
            T = True
        else:
            break
    # if re.findall(u"(第([0-9]|零|一|两|二|三|四|五|六|七|八|九|十|百|千|万|十万|百万))", string):  # 20171225
    #     T = True
    # else:
    #     T = False
    # while T == True:
    #     data_jishu_2, string = find_jishu_2(string)
    #     data_result.append(data_jishu_2)
    #     if re.findall(u"(第([0-9]|零|一|两|二|三|四|五|六|七|八|九|十|百|千|万|十万|百万))", string):
    #         T = True
    #     else:
    #         break

    if re.findall(u"(最后([0-9]|零|一|两|二|三|四|五|六|七|八|九|十|百|千|万)*(集|季|部|期))", string):
        T = True
    else:
        T = False
    while T is True:
        data_zuihou, string = find_zuihou(string)
        data_result.append(data_zuihou)
        if re.findall(u"(最后([0-9]|零|一|两|二|三|四|五|六|七|八|九|十|百|千|万)*(集|季|部|期))", string):
            T = True
        else:
            break
    if re.findall(u"(最新([0-9]|零|一|两|二|三|四|五|六|七|八|九|十|百|千|万)*(季|集|期|部))", string):
        T = True
    else:
        T = False
    while T is True:
        data_zuixin, string = find_zuixin(string)
        data_result.append(data_zuixin)
        if re.findall(u"(最新([0-9]|零|一|两|二|三|四|五|六|七|八|九|十|百|千|万)*(季|集|期|部))", string):
            T = True
        else:
            break
    if u"最近" in string and u"更新" not in string:
        if re.findall(u"(最近([0-9]|零|一|两|二|三|四|五|六|七|八|九|十|百|千|万)*(季|集|期|部))", string):
            T = True
        else:
            T = False
        while T is True:
            data_zuijin, string = find_zuijin(string)
            data_result.append(data_zuijin)
            if re.findall(u"(最近([0-9]|零|一|两|二|三|四|五|六|七|八|九|十|百|千|万)*(季|集|期|部))", string):
                T = True
            else:
                break

    if re.findall(u"(([0-9]+|[零|一|两|二|三|四|五|六|七|八|九|十|百|千|万]+)*(季|集|期))", string):
        T = True
    else:
        T = False
    while T is True:
        data_last, string = find_last(string)
        data_result.append(data_last)
        if re.findall(u"(([0-9]+|[零|一|两|二|三|四|五|六|七|八|九|十|百|千|万]+)*(季|集|期))", string):
            T = True
        else:
            break

    session = ''
    esipod = ''

    for tmi in data_result:  ##--20171214
        if u'第' in tmi and u'季' not in tmi and u'部' not in tmi and u'集' not in tmi and u"期" not in tmi:  # 20171225 d
            esipod = tmi
        elif u'季' in tmi or u'部' in tmi:
            session = tmi
        elif u'集' in tmi or u"期" in tmi:
            if u'第' in tmi:
                if tmi.count(u'十') == 2:
                    sp = tmi.index(u'十')
                    if tmi[sp + 2] == u'十':
                        tt = tmi[sp - 1:sp + 1]
                        esipod = tmi.replace(tt, '', 1)
                    else:
                        tt = tmi[sp - 1:sp + 2]
                        esipod = tmi.replace(tt, '', 1)
                else:
                    esipod = tmi
            else:
                if tmi.count(u'十') == 1 and not re.findall(ur'[最近更新的后倒数第]', tmi):
                    aa = tmi.index(u'十')
                    if aa == 1 or aa == 0:
                        esipod = tmi
                    else:
                        session = tmi[0]
                        esipod = tmi.replace(session, '', 1)
                elif tmi.count(u'十') == 2:
                    sp = tmi.index(u'十')
                    if sp == 0:
                        tt = tmi[sp:sp + 2]
                        esipod = tmi.replace(tt, '', 1)
                    elif tmi[sp + 2] == u'十':
                        tt = tmi[sp - 1:sp + 1]
                        esipod = tmi.replace(tt, '', 1)
                    else:
                        tt = tmi[sp - 1:sp + 2]
                        esipod = tmi.replace(tt, '', 1)
                elif len(
                        tmi) == 4 and u'十' not in tmi and session == '' and '最近' not in tmi and '最新' not in tmi and '倒数' not in tmi and '最后' not in tmi:
                    session = tmi[0]
                    esipod = tmi[1:]
                else:
                    esipod = tmi  # --20171215

    if session is "" and string != '':  # 20171229 d
        last = string[-1]
        if re.findall(u"([0-9].*|[零|一|两|二|三|四|五|六|七|八|九|十|百|千|万].*)", last):
            end = re.findall(u"([0-9].*|[零|一|两|二|三|四|五|六|七|八|九|十|百|千|万].*)", string)
            h = len(end)
            if h >= 1:
                rep = end[h - 1]
                if len(rep) is 1:
                    session = rep
                    string = string.replace(rep, "")
                # elif len(rep) == 2:  # 20171227 d
                #     esipod = rep
                #     string = string.replace(rep, "")
        elif re.findall(u"[0-9]", last):
            end = re.findall('[0-9]+', string)
            h = len(end)
            if h >= 1:
                rep = end[h - 1]
                if len(rep) == 1:
                    session = rep
                    string = string.replace(rep, "")
                elif len(rep) == 2:  # 20171227 d
                    esipod = rep
                    string = string.replace(rep, "")
    if string != '':  # 20171229 d
        if string[-1] == u'的':
            string = string.replace(u'的', "")  # 20171225

    return data_result, session, esipod, string

# def find_result(string):
#     res = re.findall(u'(([第最后近更新的倒数]*([0-9零一两二三四五六七八九十百千万]+)[季集期部]*))', string)
#     data_last = res[-1][0]
#     string = string.replace(data_last, "")
#     return data_last,string
#
# def find_name(string):
#     data_result=[]
#     if re.findall(u'(([第最后近更新的倒数]*([0-9零一两二三四五六七八九十百千万]+)[季集期部]*))', string):
#         T = True
#     else:
#         T = False
#     while T == True:
#         data_jishu, string = find_result(string)
#         data_result.append(data_jishu)
#         if re.findall(u'(([0-9零一两二三四五六七八九十百千万]+)[季集期部]+)', string):
#             T = True
#         else:
#             break
#     session = ''
#     esipod = ''
#     for tmi in data_result:
#         if u'第' in tmi and u'季' not in tmi and u'部' not in tmi and u'集' not in tmi and u"期" not in tmi:
#             esipod = tmi
#         elif u'季' in tmi or u'部' in tmi:
#             session = tmi
#         elif u'集' in tmi or u"期" in tmi:
#             if u'第' in tmi:
#                 if tmi.count(u'十') == 2:
#                     sp = tmi.index(u'十')
#                     if tmi[sp + 2] == u'十':
#                         tt = tmi[sp - 1:sp + 1]
#                         esipod = tmi.replace(tt, '', 1)
#                     else:
#                         tt = tmi[sp - 1:sp + 2]
#                         esipod = tmi.replace(tt, '', 1)
#                 else:
#                     esipod = tmi
#             else:
#                 if tmi.count(u'十') == 1:
#                     aa = tmi.index(u'十')
#                     if aa == 1 or aa == 0:
#                         esipod = tmi
#                     else:
#                         session = tmi[0]
#                         esipod = tmi.replace(session, '', 1)
#                 elif tmi.count(u'十') == 2:
#                     sp = tmi.index(u'十')
#
#                     if sp == 0:
#                         tt = tmi[sp:sp + 2]
#                         esipod = tmi.replace(tt, '', 1)
#                     elif tmi[sp + 2] == u'十':
#                         tt = tmi[sp - 1:sp + 1]
#                         esipod = tmi.replace(tt, '', 1)
#                     else:
#                         tt = tmi[sp - 1:sp + 2]
#                         esipod = tmi.replace(tt, '', 1)
#                 elif len(tmi) == 4 and u'十' not in tmi and session == '' and u'最近' not in tmi and u'最新' not in tmi and u'倒数' not in tmi and u'最后' not in tmi:
#                     session = tmi[0]
#                     esipod = tmi[1:]
#                 else:
#                     esipod = tmi
#         else:
#             if tmi[0]==u'的':
#                 tmi = tmi.replace(u'的','')
#                 string = string + u'的'
#             h = len(tmi)
#             if h == 1:
#                 session = tmi
#                 string = string.replace(tmi, "")
#             elif h == 2:
#                 esipod = tmi
#                 string = string.replace(tmi, "")
#             else:
#                 string = string+tmi
#     if string != "":
#         if string[-1] == u'的':
#             string = string.replace(u'的', '')
#     return data_result,session, esipod, string
#
# def find_session_epsiod(string):
#     if type(string) == str:
#         string = string.decode("utf-8")
#     else:
#         string = string
#     data_result,session, esipod, string = find_name(string)
#     return data_result,session, esipod, string

def numberTranform(txt):

    '''
    function:将语句中含阿拉伯数字0-9转换为零到九 1013 只用这一个目前
    :param txt:
    :return:
    '''
    numberDict = {u'0': u'零', u'1': u'一', u'2': u'二', u'3': u'三', u'4': u'四', u'5': u'五', u'6': u'六',
                  u'7': u'七', u'8': u'八', u'9': u'九'}

    if isinstance(txt, str):
        txt = txt.decode('utf-8')

    txt = list(txt)
    for i in txt:
        if i in numberDict:
            txt[txt.index(i)] = numberDict.get(i)
    relute = ''.join(txt)
    return relute