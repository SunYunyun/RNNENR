#encoding:utf-8

from tornado.httpserver import HTTPServer
import os
import json
import traceback

import time
import tornado.httpclient
import tornado.web
import http2server_raw

class MainHandler(tornado.web.RequestHandler):
    '''
    post请求
    '''
    def get(self):

        templateStr = '''
                <!DOCTYPE HTML><html>
                <meta charset="utf-8">
                <head><title>Get page</title></head>
                <body>
                <form		action="/post_word"	method="post" >
                TYPE:<br>
                <input type="text"		name="TYPE"		/><br>
                VALUE:<br>
                <input type="text"		name="WORDS"	/><br>
                <input type="submit"	value="SUBMIT"	/>
                </form></body> </html>
                '''
        self.write(templateStr)


    def post(self):
        # 获取参数
        #print self.request
        # print self.path_args
        try:
            type = self.get_argument("TYPE", None)
            words = self.get_argument("WORDS", None)
            #print type,words
            if words != '':
                if type == 'RNN':#'DOMAIN':
                    start = time.time()
                    #label, _, _1 = run_classify.classify_result(words)
                    result = http2server_raw.rnnIntent(words).jsonStr
                    print  u'RNN：%s  %s 耗时： %s' % (words, result, time.time() - start)
                    #self.write('Form output is :<h1>' + str(label) + '</h1>')
                    self.write(result)
                    # print 'end',time.time() - start
                else:
                    self.write('请输入正确的查询语句')
            else:
                self.write('请输入正确的查询语句')
        except Exception, e:
            print 'traceback.format_exc():\n%s' % traceback.format_exc()
            self.write('Exception')

class RnnHandler(tornado.web.RequestHandler):
    '''
    get 同步
    '''

    def get(self):

        try:
            # type = 'RNN'#self.get_argument("TYPE", None)
            # type =self.get_argument("RNN", None)
            words = self.get_argument("text", None)
            #type = 'RNN'
            #words = ''  # 我要看片子'#''我要看赵微的电影'#'我想看刘德华演的电影'#'楚乔传'我想看刘德华导演的喜剧片
            # print type,words
            if words == '':
                pass
            else:
            #if type == 'RNN':  # 'DOMAIN':
                start = time.time()
                # label, _, _1 = run_classify.classify_result(words)
                result = http2server_raw.rnnIntent(words).jsonStr
                print  u'RNN：%s  %s 耗时： %s' % (words, result, time.time() - start)
                # self.write('Form output is :<h1>' + str(label) + '</h1>')
                self.write(result)
                # print 'end',time.time() - start
                #     else:
                #         self.write('请输入正确的查询语句')
                # else:
                #     self.write('请输入正确的查询语句')
        except Exception, e:

            print 'traceback.format_exc():\n%s' % traceback.format_exc()
            self.write('Exception')

def mainAPP():
    #http://10.9.46.102:8080/semantic/analysis?userid=sunyunyun&text=
    #/semantic/analysis
    application = tornado.web.Application([(r'/post_word', MainHandler),

        (r'/semantic/analysis', RnnHandler)# r'/'   与html中的action要一致#http://10.9.46.102:8889/getrnn?RNN=RNN&WORDS=%E6%A5%9A%E4%B9%94%E4%BC%A0
    ])
    server = HTTPServer(application)

    server.listen(8888)#8080

    #tornado.ioloop.IOLoop.instance().start()
    tornado.ioloop.IOLoop.instance().start()

if __name__ == '__main__':
    #创建一个应用对象

    app =mainAPP()
