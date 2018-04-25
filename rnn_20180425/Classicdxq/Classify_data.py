# -*- coding: utf-8 -*-
#! /usr/bin/python
import codecs
from Redis_two import GetFilmName
from Trie import TrieTree
from Bayes import BayesClass
from build_trie_oneword import Trie
import sys

import  os
import dict_data

#redis 参数
host = dict_data.radis_data['host']
port = dict_data.radis_data['port']
redis_index = dict_data.radis_data['redis_index']
cc_redis = GetFilmName(host, port, redis_index)
# 贝叶斯
tt_bayes = BayesClass()

# 前缀树_old

rootdir_1 = dict_data.trie_dir['rootdir_1']
rootdir_2 = dict_data.trie_dir['rootdir_2']
rootdir_3 = dict_data.trie_dir['rootdir_3']
rootdir_4 = dict_data.trie_dir['rootdir_4']
rootdir_5 = dict_data.trie_dir['rootdir_5']
rootdir = dict_data.trie_dir['rootdir']


# 处理type
class Buildtrie():
	def Trie(self,rootdir_1,rootdir_2,rootdir_3,rootdir_4,rootdir_5):
		t_1 = TrieTree()
		list_1 = os.listdir(rootdir_1)
		for fi in list_1:
			with codecs.open('%s%s' % ('trie_1_talking\\', fi), 'r', 'utf-8') as fn:
				for f in fn:
					line = f.rstrip()
					t_1.add(line, fi)
		t_2 = TrieTree()
		list_2 = os.listdir(rootdir_2)
		for fi in list_2:
			with codecs.open('%s%s' % ('trie_2_operation\\', fi), 'r', 'utf-8') as fn:
				for f in fn:
					line = f.rstrip()
					t_2.add(line, fi)
		t_3 = TrieTree()
		list_3 = os.listdir(rootdir_3)
		for fi in list_3:
			with codecs.open('%s%s' % ('trie_3_video\\', fi), 'r', 'utf-8') as fn:
				for f in fn:
					line = f.rstrip()
					t_3.add(line, fi)
		t_4 = TrieTree()
		list_4 = os.listdir(rootdir_4)
		for fi in list_4:
			with codecs.open('%s%s' % ('trie_4_music\\', fi), 'r', 'utf-8') as fn:
				for f in fn:
					line = f.rstrip()
					t_4.add(line, fi)
		t_5 = TrieTree()
		list_5 = os.listdir(rootdir_5)
		for fi in list_5:
			with codecs.open('%s%s' % ('trie_5_sport\\', fi), 'r', 'utf-8') as fn:
				for f in fn:
					line = f.rstrip()
					t_5.add(line, fi)
		return t_5,t_4,t_3,t_2,t_1

# 前缀树_oneword：合并后的前缀树。但是是以字为节点的
	def Trie_oneword(self,rootdir):
		trie = Trie()
		rootdir = "%s%s%s" % (sys.path[0]+'/Classicdxq', '/', rootdir)
		tt = BayesClass()
		list1 = os.listdir(rootdir)
		for fi in list1:
			with codecs.open('%s%s' % (rootdir, fi), 'r', 'utf-8') as fn:
				for f in fn:
					f_ = tt.split_data(f)
					line = f_.strip()
					if trie.get(line) != None:
						b = trie.get(line)
						fi_ = str(b) + " " + fi
						trie.insert(line, fi_)
					else:
						trie.insert(line, fi)
		return trie

#前缀树trie_word:合并后的前缀树，但是是以词为节点的
	def Trie_word(self,rootdir):
		trie_ = TrieTree()
		list = os.listdir(rootdir)
		for fi in list:
			with codecs.open('%s%s' % ('trie_data\\', fi), 'r', 'utf-8') as fn:
				for f in fn:
					# line = f.rstrip().replace(' ', '')
					a, b = trie_.search(f), trie_.tag
					if a == True:
						fi_ = b + " " + fi
						trie_.add(f, fi_)
					else:
						trie_.add(f, fi)




