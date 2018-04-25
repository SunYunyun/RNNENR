#encoding:utf-8

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import re
import urllib
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
import time
import traceback


import coreControl
# from classify_to_wenfa import run_classify


class TestHTTPHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.protocal_version = 'HTTP/1.1'
        self.send_response(200)
        self.send_header("Welcome", "Contect")
        self.send_header("Content-Type", "text/html;charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        templateStr = '''
        <!DOCTYPE HTML><html>
        <meta charset="utf-8">
        <head><title>Get page</title></head>
        <body>
        <form		action="post_word"	method="post" >
        TYPE:<br>
        <input type="text"		name="TYPE"		/><br>
        VALUE:<br>
        <input type="text"		name="WORDS"	/><br>
        <input type="submit"	value="SUBMIT"	/>
        </form></body> </html>
        '''
        # self.wfile.write(templateStr)
        # peth = self.path
        # print peth
        # url =peth.split('?')[0]
        # if url == '/domain_judge':
        #     ss = peth.split('?')[1].split('=')[1]
        #     print ss
        #     start = time.time()
        #     result = run_classify.classify_result(unicode(ss))
        #     print  u'RNN：%s  %s 耗时： %s' % (unicode(ss), result, time.time() - start)
        #     self.wfile.write(result)
        # else:
        self.wfile.write(templateStr)

    def do_POST(self):
        self.protocal_version = 'HTTP/1.1'
        self.send_response(200)
        self.send_header("Welcome", "Contect")
        self.send_header("Content-type", "text/html")
        self.end_headers()
        try:
            datas = self.rfile.read(int(self.headers['content-length']))
            datas = urllib.unquote(datas).decode("utf-8", 'ignore')

            pattern = re.compile(r'TYPE=([^\&]*)\&WORDS=(.*)')
            match = pattern.match(datas)
            if match:
                group_1 = match.group(1)
                group_2 = match.group(2)
                if group_1.upper() == 'RNN':
                    start = time.time()
                    #
                    result = coreControl.CoreContro(group_2).reslutJson
                    print  u'RNN：%s  %s 耗时： %s' % (group_2, result, time.time() - start)
                    self.wfile.write(result)
                # elif group_1.upper() == 'DOMAIN':
                #     start = time.time()
                #     result = run_classify.classify_result(group_2)
                #     print  u'RNN：%s  %s 耗时： %s' % (group_2, result, time.time() - start)
                #     self.wfile.write(result)
                # elif group_1.upper() == 'CORRECTION':
                #     start = time.time()
                #     target = http2server_raw.proofcheck()
                #     character, mongodic, category = target.proofreadAndSuggest(u"%s" % group_2)
                #     result = target.result_form(character, category)
                #     t2 = threading.Thread(target=target.writeToMongo, args=(character, mongodic,))
                #     t2.setDaemon(True)
                #     t2.start()
                #
                #     print  u'CORRECTION：%s  %s 耗时： %s' % (group_2, result, time.time() - start)
                #     self.wfile.write(result)
                # elif group_1.upper() ==u'LU' or group_1.upper() =='LU':
                #     http2server_raw.GetSearcher()
                #     # test.GetSearcher()
                #     print 'lucene has updated'
                #     self.wfile.write('ok')
                else:
                    self.wfile.write('请输入正确的查询参数')
            else:
                self.wfile.write('请输入正确的查询参数')
        except Exception, e:
            print 'traceback.format_exc():\n%s' % traceback.format_exc()
            self.wfile.write('Exception')

def start_server(port):
    http_server = HTTPServer(('', int(port)), TestHTTPHandler)
    http_server.serve_forever()


if __name__ == '__main__':

    print 'begin'
    start_server(8888)


