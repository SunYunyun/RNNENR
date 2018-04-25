#!/usr/bin/python
# -*- coding:utf-8 -*-
import codecs
f1 = codecs.open('123.txt','r','utf-8')
lines = f1.readlines()
f = codecs.open('result.txt','w','utf-8')
f2 = codecs.open('output.txt','w','utf-8')

# 字之间加空格
for line in lines:
    ss = ''
    for i in line.strip():
        print i
        ss = ss+' '+i
    f.write(ss.lstrip()+'\n')

# #去掉文件中重复的词语
# rr = []
# for line in lines:
#     if line.strip() not in rr:
#         rr.append(line.strip())
#         f.write(line.strip()+'\n')
#     else:
#         f2.write(line.strip()+'\n')

