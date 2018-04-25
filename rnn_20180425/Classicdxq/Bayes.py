# -*- coding: utf-8 -*-
#! /usr/bin/python


import jieba
from numpy import *
import pandas as pd


#贝叶斯分类
class BayesClass:
    #对文本完全分词
    def all_cat(self,sentence):
      # sentence：训练数据
      # spritall：列表，包含全分词的所有词
      spritall = []
      length = len(sentence)
      for i in range(length):
          for j in range(length, i+1, -1):
              str = sentence[i: j]
              spritall.append(str)
      return spritall
    def split_data(self,x_input):
        ss = ''
        for word in x_input:
            ss = ss + ' ' + word
        x_input = ss.lstrip()
        return x_input

    #读取数据
    def data_load(self,filename):
        #filename:文件名
        #data_dict：训练数据结巴分词
        # data_label：训练数据的标签
        data = pd.read_excel(filename, header=0)
        data['data'] = data['data'].apply(lambda x: jieba.lcut(x))  # 调用结巴分词
        data_dict = data['data']
        data_label = data['lable']
        return data_dict, data_label

    #构建字典
    def createVoctorList(self,dataSet):
        #dataSet：训练数据整合后的结果
        #voctorSet：字典,dataSet去重
        voctorSet = []
        for word_document in dataSet:
            for i in word_document:
                if i not in voctorSet:
                    voctorSet.append(i)
        return voctorSet

    #构建词向量
    def createVoctorList_1(self,vocabList, inputSet):
        #vocabList：字典
        #inputSet:训练数据
        #retVocabList：词向量
      retVocabList = [0] * len(vocabList)
      for word in inputSet:
          if word in vocabList:
              retVocabList[vocabList.index(word)] = 1
      return retVocabList

    #贝叶斯分类
    def Bayes_model(self,filename):
        #x_input：用户输入
        #filename：训练数据文件
        #label：标签
        trainMat = []
        listOPosts, listClasses = self.data_load(filename)
        myVocabList = self.createVoctorList(listOPosts)
        for postinDoc in listOPosts:
            trainMat.append(self.createVoctorList_1(myVocabList, postinDoc))

        trainMatrix = array(trainMat)
        trainCatergory = array(listClasses)

        n1 = 0
        n2 = 0
        n3 = 0
        n4 = 0
        for number in trainCatergory:
            if number == 0:
                n1 = n1 + 1
            elif number == 1:
                n2 = n2 + 1
            elif number == 2:
                n3 = n3 + 1
            else:
                n4 = n4 + 1

        numTrainDoc = len(trainMatrix)
        numWords = len(trainMatrix[0])
        pA0sive = n1 / float(numTrainDoc)
        pA1sive = n2 / float(numTrainDoc)
        pA2sive = n3 / float(numTrainDoc)
        pA3sive = n4 / float(numTrainDoc)

        p0Num = ones(numWords)
        p1Num = ones(numWords)
        p2Num = ones(numWords)
        p3Num = ones(numWords)

        p0Denom = 2.0
        p1Denom = 2.0
        p2Denom = 2.0
        p3Denom = 2.0

        for i in range(numTrainDoc):
            if trainCatergory[i] == 1:
                p1Num += trainMatrix[i]
                p1Denom += sum(trainMatrix[i])
            elif trainCatergory[i] == 0:
                p0Num += trainMatrix[i]
                p0Denom += sum(trainMatrix[i])
            elif trainCatergory[i] == 2:
                p2Num += trainMatrix[i]
                p2Denom += sum(trainMatrix[i])
            else:
                p3Num += trainMatrix[i]
                p3Denom += sum(trainMatrix[i])

        p1Vect = log(p1Num / p1Denom)  # 处于精度的考虑
        p0Vect = log(p0Num / p0Denom)
        p2Vect = log(2 * p2Num / p2Denom)
        p3Vect = log(3 * p3Num / p3Denom)
        return myVocabList,p1Vect,p2Vect,p0Vect

    def BayesClass(self,x_input,myVocabList,p1Vect,p2Vect,p0Vect):
        spritall = []
        spritall_1 = []
        for one_word in x_input.split(' ')[0]:
            spritall_1.append(one_word)
        flag = False
        length = len(x_input)
        for i in range(length):
            for j in range(length, i + 1, -1):
                str = x_input[i: j]
                spritall.append(str)
        thisDoc = array(self.createVoctorList_1(myVocabList, spritall))
        p1 = sum(thisDoc * p1Vect) + log(0.1)
        p2 = sum(thisDoc * p2Vect) + log(0.01)
        p0 = sum(thisDoc * p0Vect) + log(0.99)
        maxp = max(p1, p2, p0)
        if maxp == p1:
            label = 'VIDEO'
        elif maxp == p2:
            label = 'MUSIC'
        else:
            label = 'BAIKE'
        return label
if __name__=="__main__":
    tt = BayesClass()
    text = u'我想看天气'
    # print all_cut(text)
    print (tt.all_cat(text))