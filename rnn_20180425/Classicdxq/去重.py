# -*- coding: utf-8 -*-
#! /usr/bin/python
import codecs

def check(filename1,filename2):
    f1 = codecs.open(filename1,'r','utf-8')
    f2 = codecs.open(filename2,'w','utf-8')
    lines = f1.readlines()
    data = []
    for line in lines:
        if line not in data:
            data.append(line)
            f2.write(line)
    f1.close()
    f2.close()
    return data
data = check('data1.txt','data2.txt')