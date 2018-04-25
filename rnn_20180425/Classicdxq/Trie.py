# -*- coding: utf-8 -*-
#! /usr/bin/python

#前缀树
class TrieTree(object):

  def __init__(self):
    self.tree = {}
    self.origin=''
    self.tag = ''
    self.child=self.tree

#构建前缀树
  def add(self, word,tag):
    #word:特征
    #tag：标签
    tree = self.tree
    for char in word:
      if char in tree:
        tree = tree[char]
      else:
        tree[char] = {}
        tree = tree[char]
    tree['exist'] = True
    tree['tag'] = tag
    tree['origin'] = word
    # print tag,'-->',word
#前缀树查询
  def search(self, word):
    #word:词
    tree = self.tree
    for char in word:
      if char in tree:
        tree = tree[char]
      else:
        return False
    if "exist" in tree and tree["exist"] == True:
      self.origin = tree['origin']
      self.tag = tree['tag']
      return True
    else:
      return False
