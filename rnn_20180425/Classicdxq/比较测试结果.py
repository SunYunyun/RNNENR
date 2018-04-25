# -*- coding: utf-8 -*-
#! /usr/bin/python
import codecs
data_in = open('domain_30.txt').readlines()
data_out = open('domain_31.txt').readlines()
f3 = codecs.open('domain_3.txt','w','utf-8')
result_in = []
result_out =[]
label = ''
for line in data_in:
    result_in.append(line.strip().split(','))
for line1 in data_out:
     ss = line1.replace('[','').replace(']','').replace("'",'').strip().split(',')
     if len(ss)==2:
        ss[1] = ss[1].strip()
     result_out.append(ss)
# print result_in
# print result_out
for i in range(len(result_out)):
    for j in result_out[i]:
        if j in result_in[i]:
           label = '0'
           break
        else:
            label = '1'
    print label

#
    f3.write(str(label)+'\n')
f3.close()