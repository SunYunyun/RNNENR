#!/usr/bin/env python
# -*- coding: utf-8 -*-

import codecs
import random

def split_train_val_test(filename, total, ratio=[0.6,0.3,0.1]):
    train_num = total * ratio[0]
    val_num = total * ratio[1]
    test_num = total * ratio[2]
    i = 0
    train = codecs.open(filename+".train", "w", encoding="utf-8")
    val = codecs.open(filename+".val", "w", encoding="utf-8")
    test = codecs.open(filename+".test", "w", encoding="utf-8")

    with codecs.open(filename, "r", encoding="utf-8") as f:
        for line in f:
            sline = line.strip().split()
            i += 1
            if i< train_num:
                cur_file = train
            elif i-train_num < val_num:
                cur_file = val
            elif i-train_num-val_num< test_num:
                cur_file = test

            for word in sline:
                tag = []
                if len(word) == 1:
                    tag = ["s"]
                else:
                    tag = ["I"] * len(word)
                    tag[0] = "B"
                    tag[-1] = "E"
                for (ch,t) in zip(word, tag):
                    cur_file.write(ch + "\t" + t + '\n')
            cur_file.write("\n")

def shuffle(lol, seed):
    for l in lol:
        random.seed(seed)
        random.shuffle(l)

def nlu_split_train_val_test(filename, total, ratio=[0.6,0.3,0.1]):
    train_num = total * ratio[0]
    val_num = total * ratio[1]
    test_num = total * ratio[2]
    i = 0
    train = codecs.open(filename + ".train", "w", encoding="utf-8")
    val = codecs.open(filename + ".val", "w", encoding="utf-8")
    test = codecs.open(filename + ".test", "w", encoding="utf-8")

    samples=[]
    lables=[]
    flag=0
    with codecs.open(filename, "r", encoding="utf-8") as f:
        for line in f:
            line = line.rstrip()
            if flag%2 == 0:
                samples.append(line)
            else:lables.append(line)
            flag = flag+1

    shuffle([samples, [], lables], 345)

    for (ch, t) in zip(samples, lables):
        i += 1
        if i < train_num:
            cur_file = train
        elif i - train_num < val_num:
            cur_file = val
        elif i - train_num - val_num < test_num:
            cur_file = test

        chs = ch.split(' ')
        ts = t.split(' ')
        for ch_s,t_s in zip(chs,ts):
            cur_file.write(ch_s + "\t" + t_s + '\n')
        cur_file.write('\n')


if __name__ == "__main__":
    # split_train_val_test("msr_training.utf8",86924)
    nlu_split_train_val_test('nlu_training.utf8',11122)