#encoding:utf-8
'''
中控
添加台词场景剧情  20180417 syy
VR景点识别代码合并 20180423 syy


'''
import taiScenes
import http2server_raw
from ScenicLizhuoxuan423 import scenic_area #
from Classicdxq import trie_bys_getname_20180412
import json
shortScenes = ['你的名字是三叶','张一曼疯了','张一曼自杀了','张一曼自杀','哭出来就好了','赝品是个好东西','做你想做的吧','平安无事','阿甘一直奔跑',
                     '阿甘和珍妮结婚','老布上吊自杀','不疯魔不成活','小癞子上吊自杀','ONLYYOU','点烟辨冤','巨怪出现','巨浪来袭',
               'V救了伊芙','飞船穿越虫洞','抽象开始','情绪哪能辞职','莱莉被吓醒','妮娜产生幻觉','蝙蝠侠救瑞秋','陈海被撞','丁义珍出逃',
        '陈清泉落网','姥姥同意迁坟','建立撒西路','孩子不是爱好','复制人怀孕了','海上弹钢琴','牛顿第三定律','你是我幽灵','看不见听不见','子弹给我中校',
               '没听到没看到','明理方能成人','早上好公主','没用就抛弃掉','人们忘性大','楚门不见了','上帝就在雨中','活着真对不起','我是农民儿子',
               '你名字是三叶','做你想做吧']



class CoreContro(object):

    def __init__(self, txt):

        self.txt = txt
        #self.lenTxt ,self.proQuery = self.preDatapross(self.txt)
        #self.unicodeTran = self.unicodeTran(self.txt)
        self.lenTxt = self.preDatapross(self.txt)
        #self.domianClassic = trie_bys_getname_20180412.Classify(self.unicodeTran) #领域分类

        #self.proQuery = ''
        self.reslutJson = {}
        self.main_function()


    def unicodeTran(self,txt):
        '''
        编码转换

        :param txt: 输入语句
        :return:
        '''

        if isinstance(txt, unicode):
            return txt
        else:
           return txt.decode('utf-8')


    def preDatapross(self,query):
        '''
        去掉我想看等长大于7时不走台词
        :return:
        '''
        part = ['我想看', '我要看', '播放', '观看', '台词', '剧情']
        query = query.replace('。','').replace(' ','').replace('，','').replace('！', '').replace('？', '')\
            .replace(',', '').replace('：', '').replace('"', '').replace('\'', '').upper()#！ ？

        for word in part:
            if query.find(word) != -1:
                query = query.replace(word, '')
                break
        #print query


        #处理短台词剧情  20180417 wan onlyyou
        if query in shortScenes:
            return 10#,query
        # elif '影片' in query:
        #     return 1#,query

        #return len(query.decode("utf-8")), query
        return len(query.decode("utf-8"))

    def domainClassic(self,txt):

        # 领域分类
        return trie_bys_getname_20180412.Classify(txt)

    def scenicLizhuoxuan(self, txt):


        #VR景区结果封装
        data = {}
        semantic = {}
        scenicJson = {}
        scenicDict = scenic_area.ScenicAreaEntityExtraction.scenic_area_entity_extraction(txt)
        if scenicDict.get('scenic_name'):
            semantic['name'] = scenicDict['scenic_name']
            data['domain'] = "VR"
            data['intent'] = 'queryScenic'
            data['semantic'] = semantic
            scenicJson['code'] = 200
            scenicJson['flag'] = 1
            scenicJson['data'] = data
        return json.dumps(scenicJson, ensure_ascii=False)



            


    def main_function(self):

        if self.lenTxt >= 7:

            #print '111',self.proQuery
            #k = taiScenes418.TaiSi(self.proQuery).scoreJson
            k = taiScenes.TaiSi(self.txt).scoreJson
            #print k
            if k:
                self.reslutJson = k

            else:
                #台词剧情识别失败-如果领域分类为VR景点且只有一个领域识别结果 走景点识别代码（若识别失败走RNN）
                domianLst = self.domainClassic(self.unicodeTran(self.txt))
                if len(domianLst) == 1 and domianLst[0] == 'SCENICAREA':
                    scenic_area = self.scenicLizhuoxuan(self.unicodeTran(self.txt))
                    if scenic_area:
                        self.reslutJson = scenic_area
                else:
                    self.reslutJson = http2server_raw.rnnIntent(self.txt).jsonStr
            # if k == {}:
            #     http2server_raw.rnnIntent(self.txt)
            # else:
        else:#去除我想看等字数小于7的
            #self.reslutJson = http2server_raw.rnnIntent(self.txt).jsonStr
            domianLst = self.domainClassic(self.unicodeTran(self.txt))
            if len(domianLst) == 1 and domianLst[0] == 'SCENICAREA':
                scenic_area = self.scenicLizhuoxuan(self.unicodeTran(self.txt))
                if scenic_area:
                    self.reslutJson = scenic_area
            else:
                self.reslutJson = http2server_raw.rnnIntent(self.txt).jsonStr
        print self.reslutJson

if __name__ == '__main__':
    import time
    import cProfile
    s = time.time()
    obj = CoreContro('''我要看张一曼自杀了''')
    #cProfile.run("CoreContro('''我要看张一曼自杀了''')",sort=1)
    print time.time() - s
    # print obj.reslutJson
    # f = open(r'taisi4181.txt', 'r')
    # for i in f.readlines():
    #     obj = CoreContro('我想看'+i.strip('\r\n'))

    # f.close()
