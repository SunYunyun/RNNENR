#encoding:utf-8
#coding:utf-8
from pyArango.connection import *
class config():

    dev_address = 102

    arrangoPath = 'http://10.9.46.114:8529'
    mongo_path = '10.9.201.190'
    mongoDB='MovieKnowledgeMap'

    arrangoName = 'knowledge-graph-test'
    mongo_port = 27017
    redis_ip = '10.9.46.102'
    redis_port = 6379
    redis_db_c = 1
    redis_db_error = 15

    if dev_address == 208:

        arrangoPath = 'http://10.66.1.208:11003'
        mongo_path = '10.66.1.208'
        arrangoName = 'knowledge-graph-test'
        mongo_port = 27017
        redis_ip = '10.66.1.208'
        redis_port = 6379
        # redis_db_c = 15
        redis_db_error = 15

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
        # redis_db_c = 15
        redis_db_error = 15


class clients():
    conn = []
    if config.dev_address == 102:
        conn = Connection(arangoURL=config.arrangoPath, username='tester', password=123456)
    else:
        conn = Connection(arangoURL=config.arrangoPath)
    db = conn[config.arrangoName]

    @staticmethod
    def ec_queryResult_video(name, label):
        aql = 'For doc In entity Filter doc.label== "%s" && doc.hot==true and doc.status == "active" Return %s' % (
        name, label)
        queryResult_video = clients.db.AQLQuery(aql, rawResults=True, batchSize=1)
        return queryResult_video

    @staticmethod
    def prefixMusic():
        categoryMu={u'歌曲':'gequ ge yishougequ'}
        prefix_music = {u"我想听": "changhongxiaobai tangxiaobai hanhongxiaobai xiaobai woxiangwoxiangting "
                                "woxiangtingyinyue woxiangtinggequ woxiangting woyaoting woyaoting yaoting "
                                "xiangting woxiangchang woxiangchang "
                                "woyaochang woxiangtinggequ woxiangtingyinyue woxiangtingge"
                                "woxiang woyao fangge",
                        u"播放": "bofang xiangting", u"歌曲": "gequ ge yinle", u"来一首": "laiyishou",
                        u"唱": "woxiangchang aichang chang fang bo"}
        suffix_music = {u"歌曲": "diyishouge zheshougequ deyinle zheshouge degequ dege deyinyue degeer "
                               "dekaitou dejiewei"}
        middle_music = {u"演唱的": "yanchangde changde de"}
        return categoryMu,prefix_music,suffix_music,middle_music
    @staticmethod
    def redundentVideo():
        categorysVideo = {u'电影': 'dedianying dedianyingmei dedianmei dedianyoumei pianer dianyinga'
                            'dedianyou zhuyandedianying yandedianying dianying pian'
                            'canyudedianying deyingpian depian yingpian leidedianying dianyingban',
                     u'电视剧': 'dedianshiju dianshiju yandedianshiju juji dianshilianxuju yingshi'
                             'leidedianxing leidongman leijilupian leidedongman leidedianying riju hanju'
                             'canyudedianshiju leideshenghuojiemu meiju yingju',
                     u'综艺': 'leizongyi leidezongyi zongyijiemu',
                     u'动画': 'dongman donghua donghuapian riman', u'体育': 'tiyu tiyulei tiyujiemu', u'娱乐': 'yule'
                     }
        prefix_video = {
            u'我想看': 'tangxiaobai woxiangkan wokan woxiangkan enwoxiangkan woxiangkanhuo haoxiangkan woxiang woxiangkana '
                   'woxiangkange mawoxiangkan geiwolaiyibu woxiangkanyi enwoxiangkan', u'给我': 'geiwo bangwo',
            u'我要看': 'woyaokan oyaokan woyaodian yaokan fangyixia', u'点播': 'dianbo jianbo yanbo chazhao',
            u'来一部': 'laiyibu souyib fangyibu', u'切换至': 'qiehuanzhi qiehuanzi qiehuandao',
            u'来一': 'laiyi laige kanyi', u'播放': 'qingbofang qingbo bofang boqiu shoukan fangdianbo zhujiaoshi zhujiao',
            u'来': 'lai nai na laige naige', u'那我': 'nawo lawo', u'检索': 'jiansuo jianshuo jiasuo jiashuo',
            u'有没有': 'youmeiyou youmei kanyikan baobao', u'有': 'you kan jiebo',
            u'打开': 'dakai dakaiwode', u'电视剧': 'dianshiju dianshi dianshilianxuju yingshi yingshi',
            u'电影': 'dianying pian yingpian', u'搜索': 'sousuo', u'调': 'tiao mv fang', u'搜': 'sou',
            u'集': "zuixinyi zuixin1 zuihouyi zuijinyi zuijin1",
            u'恩': 'you en gua', u'类型': 'donghuapian donghua zongyi yingwenban yingyu'}

        suffix_video = {u'来一部': 'laiyibu laiyi nayibu nayi', u'有哪些': 'youna younaxie youlaxie youmeiyou',
                      u'有吗': 'youma youmei', u'动画片': 'donghuapian donghuaban xijupian zongyijiemu',
                      u'电视剧': 'dianshiju juji dianshilianxuju', u'的影视': 'deyingshi yingshi pianzi',
                      u'这部电影': 'zhebudianying zhebudian zhedianying zhedian zhepian nabudianying zhegedianying',
                      u'类的电视': 'leidedianxing leidongman leijilupian leidedongman leidedianying leizongyi leidezongyi '
                              'leideshenghuojiemu', u'片儿': 'pianer depianer',
                      u'类型': 'zongyi donghua dianying dongman tiyujiemu mv',
                      u'的电影': 'dedianying dedian deying dedianyingmei dedianyingma dedianyingyoumei dedianyou '
                             'deying deyingpian depian yingpian leidedianying dexijudianying paidexijudianying',
                      u'版本': 'guoyuban yingyuban guoyu yingyu gaoqingban languang gaoqing languangban nanguang '
                            'nanguangban chaogaoqing quangaoqing quangaoqingban yingwenban neidiban daluban',
                      u'的电视剧': 'dedianshiju dianshiju yandedianshiju canyudedianshiju dejuji',
                      u'拍摄': 'paishe paide canyan canyu yan biaoyan canyan zhuyan hezuo',
                      u'结尾': 'dajieju diyi dier disan disi diwu diliu diqi diba dijiu dishi zuihouyi', u'没': 'haoba mei',
                      u'集': "zuixinyi zuixin1 zuihouyi zuijinyi zuijin1 zuixin2 zuixinliang ne dao pai"}
        middle_dic = {u"演的": "zhuyande yande zuopeijiaode canyande", u"参与": "canyude hezuo banyan",
                      u"拍摄": "paisede paise daoyande daoyan zhizhuode"}
        return categorysVideo,prefix_video,suffix_video,middle_dic
    @staticmethod
    def prefixAPPTV():
        # prefix_APPTV_ = {u"我想看": "woxiangkan xiangkan woxiangwan xiangwan woxiangdakai woxiang woyaokan "
        #                           "changhongxiaobai congxiaobai biede woyao qiehuandao liuan tangxiaobai "
        #                           "bangwoxiaobai xiaobai chuangexiaobai xiaobai",
        #                   u"打开": "dakai qiehuandao kaidao tiaojiedao tiaodao tiaojiezhi tiaozhi tiaojie shangge shangshangge",
        #                   u"切换": "tiaozhuan tiao zhuan kuaitui kuaijin bofang dianbo kan sousuo fangying",
        #                   u"语气词": "qing ba tiao"}

        prefix_APPTV = {u"我想看": "woxiangkan xiangkan woxiangwan xiangwan woxiangdakai woxiang "
                             "changhongxiaobai congxiaobai biede woyao qiehuandao liuan tangxiaobai "
                             "bangwoxiaobai xiaobai chuangexiaobai xiaobai",
                     u"打开": "dakai qiehuandao kaidao tiaojiedao tiaodao tiaojiezhi tiaozhi tiaojie",
                     u"增加": "tiaogaozhi zengjiadao jiada taidaliao taidale tailiangliao tailiangle "
                            "gaoyidian zengzhi dayidiandian tiaogaodao tiaogao jiadao gaodian "
                            "dadian zailiang",
                     u"减少": "jianshaodao jianshaozhi tiaodidian tiaodidao tiaodizhi diyidian jiangdidao "
                            "tiaodi jianshao xiaodian didian zaixiao zaian shouxi",
                     u"语气词": "qing ba tiao"}

        suffix_APPTV = {u"我想看": "woxiangkan xiangkan woxiangwan xiangwan woxiangdakai woxiang "
                             "changhongxiaobai congxiaobai",
                     u"打开": "dakai qiehuandao kaidao tiaojiedao tiaodao tiaojiezhi tiaozhi tiaojie "
                            "tiaoguo nage bofangdao",
                     u"一点点": "yidiandian yidian dianer dian",
                     u"增加": "tiaogaozhi zengjiadao jiada tailiangliao "
                            "tailiangle zaida zailiang gaoyidian zengzhi dayidiandian tiaogaodao "
                            "tiaogao jiadao gaodian dadian zaigao shaoweida shaoda "
                            "fangda taixiaoliao taixiaole buxing",
                     u"减少": "jianshaodao jianshaozhi tiaodidian tiaodidao tiaodizhi diyidian "
                            "jiangdidao tiaodi jianshao xiaodian didian zaixiao zaian "
                            "taidale tailiangliao shouxi "
                            "zaidi zaixiao zaian gaoxiao",
                     u"语气词": "qing ba tiao baibai wang"}
        return prefix_APPTV,suffix_APPTV



