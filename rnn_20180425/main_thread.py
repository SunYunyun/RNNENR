#-*- coding: UTF-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

#import http2server_raw
from http.server import BaseHTTPRequestHandler
from http.server import HTTPServer
from socketserver import ThreadingMixIn
import urllib,re
import time

import coreControl

class mySoapServer(BaseHTTPRequestHandler):
    def do_head(self):
        pass

    def do_GET(self):
        try:
            self.send_response(200, message=None)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            res = '''
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

            self.wfile.write(res.encode(encoding='utf_8', errors='strict'))

            # datas = u'TYPE=RNN&WORDS='+self.command
            datas = self.command
            pattern = re.compile(r'TYPE=([^\&]*)\&WORDS=(.*)')
            match = pattern.match(datas)
            if match:
                group_1 = match.group(1)
                group_2 = match.group(2)
                if group_1.upper() == 'RNN':
                    start = time.time()
                    result = coreControl.CoreContro(group_2).reslutJson
                    print  u'RNN：%s  %s srtart:%s end:%s 耗时： %s' % (group_2, result, start,time.time(),time.time() - start)
                    self.wfile.write(result)
                    # self.wfile.write(res.encode(encoding='utf_8', errors='strict'))
        except IOError:
            self.send_error(404, message=None)

    def do_POST(self):
        try:
            self.send_response(200, message=None)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            datas = self.rfile.read(int(self.headers['content-length']))
            datas = urllib.unquote(datas).decode("utf-8", 'ignore')
            pattern = re.compile(r'TYPE=([^\&]*)\&WORDS=(.*)')
            match = pattern.match(datas)
            if match:
                group_1 = match.group(1)
                group_2 = match.group(2)
                if group_1.upper() == 'RNN':
                    start = time.time()
                    # logg.DEBUG(group_2,'here is input string from web')

                    result = coreControl.CoreContro(group_2).reslutJson

                    print  u'RNN：%s  %s srtart:%s end:%s 耗时： %s' % (group_2, result, start, time.time(), time.time() - start)
                    self.wfile.write(result)
        except IOError:
            self.send_error(404, message=None)


class ThreadingHttpServer(ThreadingMixIn, HTTPServer):
    pass

if __name__ == '__main__':

    myServer = ThreadingHttpServer(('', 8888), mySoapServer)
    myServer.serve_forever()
    myServer.server_close()