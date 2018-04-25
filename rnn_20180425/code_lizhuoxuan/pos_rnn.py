# coding: utf-8

import sys
reload(sys)
sys.setdefaultencoding('utf8')

import json as js
import numpy as np
import tensorflow as tf
from tensorflow.contrib import rnn,crf

# stringa="我想看<跟<的电影"

class POS():


    f=open("save/variables.txt","r")
    variables=js.load(f)
    f.close()
    w2v_model=variables["w2v_model"]
    transfer_matrix=variables["transfer_matrix"]
    digit_to_label=variables["digit_to_label"]
    num_label=variables["num_label"]
    max_len=variables["max_len"]

    batch_input = tf.placeholder(tf.float32, [None, max_len * 50])
    w=tf.Variable(tf.random_normal([64,num_label]))
    b=tf.Variable(tf.random_normal([num_label]))
    xs_forward=tf.reshape(tf.transpose(tf.reshape(batch_input,[-1,max_len,50]),[1,0,2]),[-1,50])
    xs_reverse=tf.reshape(tf.transpose(tf.reshape(tf.reverse(batch_input,[0]),[-1,max_len,50]),[1,0,2]),[-1,50])
    hsplit_forward=tf.split(xs_forward,max_len,0)
    hsplit_reverse=tf.split(xs_reverse,max_len,0)
    with tf.variable_scope("lstm_forward",reuse=None) as scope:
        cell_forward=tf.nn.rnn_cell.BasicLSTMCell(32,forget_bias=1.0,state_is_tuple=False)
        cell_forward_dropped=tf.nn.rnn_cell.DropoutWrapper(cell_forward,output_keep_prob=1.0)
        out_forward,_=rnn.static_rnn(cell_forward_dropped,hsplit_forward,dtype=tf.float32)

    with tf.variable_scope("lstm_reverse",reuse=None) as scope:
        cell_reverse=tf.nn.rnn_cell.BasicLSTMCell(32,forget_bias=1.0,state_is_tuple=False)
        cell_reverse_dropped=tf.nn.rnn_cell.DropoutWrapper(cell_reverse,output_keep_prob=1.0)
        out_reverse,_=rnn.static_rnn(cell_reverse_dropped,hsplit_reverse,dtype=tf.float32)

    out=tf.concat([out_forward,tf.reverse(out_reverse,[0])],2)

    crf_input=tf.transpose(tf.reshape(tf.add(tf.matmul(tf.reshape(out,[-1,64]),w),b),[max_len,-1,num_label]),[1,0,2])


    @staticmethod
    def pos_rnn(string):

        if type(string)!='unicode':

            string=unicode(string)

        # 输入处理
        # 我想看刘德华和他老婆的电影  ---》 [‘’，‘’，‘’，‘’，‘’，‘’]
        sentence=[]

        for word in string.strip():

            if len(sentence)<POS.max_len-2:

                if word not in POS.w2v_model:
                    sentence.append(u"的")

                else:
                    sentence.append(word)

        sentence.insert(0,"fl-s")
        sentence.append("fl-e")

        while len(sentence)<POS.max_len:
            sentence.append("fl-o")

        # embedding
        vec_sentence=[]

        for word in sentence:
            vec_sentence = np.hstack((vec_sentence, POS.w2v_model[word]))

        crf_input = POS.crf_input


        # 加载model （bi-lstm crf）
        saver=tf.train.Saver(max_to_keep=1)
        config=tf.ConfigProto(gpu_options=tf.GPUOptions(allow_growth=True),log_device_placement=False)
        sess=tf.Session(config=config)
        saver.restore(sess,"save/mix_model-1000")

        # crf输入的实值
        transfer_sentence=sess.run(crf_input,feed_dict={POS.batch_input:[vec_sentence]})

        # 输出
        crf_out,crf_score=crf.viterbi_decode(transfer_sentence[0],POS.transfer_matrix)

        labels=[]

        for label_digit in crf_out:

            if POS.digit_to_label[str(label_digit)]=="fl-e":

                break

            if POS.digit_to_label[str(label_digit)]!="fl-s":

                labels.append(POS.digit_to_label[str(label_digit)].encode("utf-8"))

        sess.close()

        return labels


if __name__ == '__main__':

    s = ['我想看周杰伦的电影','我想看刘德华的电影','我想看马德华的他妈妈的电影','我想看>跟<的电影']

    for i in s:
        print POS.pos_rnn(i)