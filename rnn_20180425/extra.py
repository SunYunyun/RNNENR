# -*- coding: utf-8 -*-
import re
def find_extra(text,data_extra):
    extra=""
    rep = []
    for j in data_extra:
        if j in text:
            rep.append(j)
    l = len(rep)
    if l>1:
        # if 'TV' in rep and 'TV版' in rep:
        #     rep.remove('TV')
        if '蓝光真高清' in rep:
            if '蓝光' in rep:rep.remove('蓝光')
            if '高清' in rep:rep.remove('高清')
            if '超高清' in rep: rep.remove('超高清')
        if '超高清' in rep:
            if '高清' in rep: rep.remove('高清')
        if '全高清' in rep:
            if '高清' in rep: rep.remove('高清')
        if '超高清' in rep and '全高清' in rep and '高清' in rep:
            rep.remove('超高清')
            rep.remove('全高清')
        if '删减版' in rep and '未删减版' in rep:
            rep.remove('删减版')
        for i in rep:  # 20180117 d
            for j in rep:
                if i in j and j != i:
                    rep.remove(i)
        # while k < l-1:
        #     if len(rep[k])<len(rep[k+1]):
        #         extra = rep[k+1]
        #     else:
        #         extra = rep[k]
        #     k+=1

        extra = find_location(text, rep)

    elif rep:
        extra = rep[0]
    return extra

def find_location(text,extra):

    loc={}

    for i in extra:
        loc[i] = text.index(i)
    l = sorted(loc.items(), lambda x, y: cmp(x[1], y[1]))
    l = [i[0] for i in l]
    return ''.join(l)

def find_num(text):

    extra = ""
    data_extra=['合集','四川话版','4k','4K','完美版', '电视剧版', '导演剪辑版', '未剪辑版', '动画版', '未删减版', '导演版', '电视版', '极清版', '原版', '原版TV', '原版MV',  '央视版', '字幕版',
     '剧场版', '现场版', '精华版', '精简版', '精编版', '精选版', '网络版', '纪念版', '高清版', '黄金版', '完整版', '真人版', '配音版', '话剧版', '特别版', '纯享版',
     '最终版', '官方版', '国际版', 'TVB版', '另类结局版', '少儿版', '删减版', '试看版', '人教版', '英文原声版', '原声版', '高曙光版', '最新版', '越剧版', '50集版','粉丝悠享版',
     '35集版', '免费版', '日播版', '明星版', '周播版', '独享版', '升级版', '周末版', '周间版', '真实版', '预热版', '首播版', '全国版', '中配版', '客厅版', '动漫版合辑',
     '水墨版', 'Q版', '多语言版', '重制版', '二维版', '三维版', 'OVA版', '加长版', '娱乐版', '现实版', '标清版', '日配版', '儿歌版', '先行版', '低配版', '搞笑版','精选辑',
     '3D版', '互动版块', '春节贺岁版', '剪辑版',  '大合集', 'MV集', '精选集', '全集', '锦集', '上集', '下集', '总篇', '番外篇', '周边合集', '高甜合集','粉丝特约版',
     '精彩合集', '特别篇', '总篇集', '短篇集', '总集篇', '完结篇', '预热篇', '春节篇', '番外', '精选', '小剧场', '原声', '精彩周边', '3D', '合辑','流畅','干货版','杜比',
     '蓝光真高清', '特辑', '儿歌KTV', 'TV', '预告片', '新版', '舞蹈版', '现场舞蹈版', '企业版', '续集', '上部', '中部', '下部', '电影版', '集锦', 'DVD版','恶搞版',
     'DVC版',   '干货精简版', '特别集','老版','最老版', '全集','试播版', '古装版', '卡通版', '终极版', '英版', '美版', '日版', '韩版', '泰版', 'cut版', 'TV版','重剪版',
     'ova', 'oad', 'CUT版', 'tv版', 'OVA', 'OAD','流畅','极速','蓝光','全高清','超高清','1080P','720P','高清','浙江版','潮汕版',]
    if '集版' in text:
        num=re.findall("[0-9]+",text)
        h = len(num)
        if h>1:
            extra = "%s集版" % (num[h-1])
        else:
            extra = "%s集版" % (num[0])
    else:

        extra = find_extra(text, data_extra)
    if extra == 'TV' and "MTV" in text:
        extra=''
    result = text.replace(extra,"")
    # result = result.decode('utf-8')#20180102 d
    if result !='':
        if result[-1] == '的':
            result = result[:-1]
    ss_len = text.index(extra)+len(extra)

    if text[ss_len:ss_len+3]=='的':
        result = result.replace('的','')
    # if extra in ['720P','720p']:
    #     extra = '高清'
    # elif extra in ['1080P','1080p']:
    #     extra = '超清'
    return extra,result

if __name__=="__main__":
    text = "雷神2的预告片"
    extra,result = find_num(text)
    # print extra,'----',result
