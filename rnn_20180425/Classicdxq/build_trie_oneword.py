# -*- coding:utf-8 -*-
# author:daixiuqiong
#date:2018-02-07

import sys
reload(sys)
sys.setdefaultencoding("utf-8")
import os
import codecs
from Bayes import BayesClass
rootdir = 'F:\\WORK_2017\\trie_bayes_class_20180129\\trie_data'

class NULL(object):
  pass

class Node:
  def __init__(self, value = NULL):
    self.value = value
    self.children = {}

class Trie(object):
  def __init__(self):
    self.root = Node()

  def insert(self, key, value = None, sep = ' '):
    elements = key if isinstance(key, list) else key.split(sep)
    # print elements
    node = self.root
    for e in elements:
      if not e: continue
      if e not in node.children:
        child = Node()
        node.children[e] = child
        node = child
      else:
        node = node.children[e]
    node.value = value

  def get(self, key, default=None, sep=' '):
    elements = key if isinstance(key, list) else key.split(sep)
    node = self.root
    for e in elements:
        if e not in node.children:
            return default
        else:
            node = node.children[e]
    return default if node.value is NULL else node.value

def BuildTree(trie,rootdir):
    tt = BayesClass()
    list1 = os.listdir(rootdir)
    for fi in list1:
        with codecs.open('%s%s' % ('trie_data\\', fi), 'r', 'utf-8') as fn:
            for f in fn:
                f_ = tt.split_data(f)
                line = f_.strip()
                if trie.get(line) != None:
                    b = trie.get(line)
                    fi_ = str(b) + " " + fi
                    trie.insert(line, fi_)
                else:
                    trie.insert(line, fi)


if __name__ == '__main__':
    import time
    trie = Trie()
    ss = buildtree(trie, rootdir)
    tt = BayesClass()
    # start_time = time.time()
    # for i in range(10000):
    print trie.get(tt.split_data(u'我想看'))
    print trie.get(u'我 想 看')
    # end_time = time.time()
    # print end_time-start_time



