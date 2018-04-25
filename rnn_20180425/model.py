#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import os
import tensorflow as tf
from data_utils import minibatches, pad_sequences, get_chunks,character_separation
from general_utils import Progbar, print_sentence
import logging


class NERModel(object):
    def __init__(self, config, embeddings, ntags, logger=None):
        """
        :param config: 高参
        :param embeddings: embedding层
        :param ntags: tag的数量 e.g. B-ORG, I-PER....
        :param logger: logger instance
        """
        self.config = config
        self.embeddings = embeddings
        self.ntags = ntags

        if logger is None:
            logger = logging.getLogger('logger')
            logger.setLevel(logging.DEBUG)
            logging.basicConfig(format='%(message)s', lebel=logging.DEBUG)

        self.logger = logger

    def add_placeholders(self):
        self.word_ids = tf.placeholder(tf.int32, shape=[None, None], name="word_ids")  # batch size, max length of sentence in batch
        self.sequence_lengths = tf.placeholder(tf.int32, shape=[None], name="sequence_lengths")  # shape = batch size
        # shape = (batch size, max length of sentence in batch)
        self.labels = tf.placeholder(tf.int32, shape=[None, None],
                                     name="labels")
        self.dropout = tf.placeholder(dtype=tf.float32, shape=[],
                                      name="dropout")
        self.lr = tf.placeholder(dtype=tf.float32, shape=[],
                                 name="lr")


    def get_feed_dict(self, words, labels=None, lr=None, dropout=None):
        word_ids, sequence_lengths = pad_sequences(words,0)
        feed = {
            self.word_ids: word_ids,
            self.sequence_lengths: sequence_lengths
        }
        if labels is not None:
            labels, _ = pad_sequences(labels, 0)
            feed[self.labels] = labels

        if lr is not None:
            feed[self.lr] = lr

        if dropout is not None:
            feed[self.dropout] = dropout

        return feed, sequence_lengths


    def add_word_embeddings_op(self):
        with tf.variable_scope("words"):
            _word_embeddings = tf.Variable(self.embeddings, name="_word_embeddings", dtype=tf.float32,
                                           trainable=self.config.train_embeddings)
            word_embeddings = tf.nn.embedding_lookup(_word_embeddings, self.word_ids,
                                                     name="word_embeddings")
        self.word_embeddings = tf.nn.dropout(word_embeddings, self.dropout)


    def add_logits_op(self):
        """
        Adds logits to self
        """
        with tf.variable_scope("bi-lstm"):
            lstm_cell = tf.contrib.rnn.LSTMCell(self.config.hidden_size)
            (output_fw, output_bw), _ = tf.nn.bidirectional_dynamic_rnn(lstm_cell,
                                                                        lstm_cell, self.word_embeddings,
                                                                        sequence_length=self.sequence_lengths,
                                                                        dtype=tf.float32)
            output = tf.concat([output_fw, output_bw], axis=-1)
            output = tf.nn.dropout(output, self.dropout)

        with tf.variable_scope("proj"):
            W = tf.get_variable("W", shape=[2 * self.config.hidden_size, self.ntags],
                                dtype=tf.float32)

            b = tf.get_variable("b", shape=[self.ntags], dtype=tf.float32,
                                initializer=tf.zeros_initializer())

            ntime_steps = tf.shape(output)[1]
            output = tf.reshape(output, [-1, 2 * self.config.hidden_size])
            pred = tf.matmul(output, W) + b
            self.logits = tf.reshape(pred, [-1, ntime_steps, self.ntags])


    def add_pred_op(self):
        """
        Adds labels_pred to self
        """
        if not self.config.crf:
            self.labels_pred = tf.cast(tf.argmax(self.logits, axis=-1), tf.int32)


    def add_loss_op(self):
        """
        Adds loss to self
        """
        if self.config.crf:
            log_likelihood, self.transition_params = tf.contrib.crf.crf_log_likelihood(
                self.logits, self.labels, self.sequence_lengths)
            self.loss = tf.reduce_mean(-log_likelihood)
        else:
            losses = tf.nn.sparse_softmax_cross_entropy_with_logits(logits=self.logits, labels=self.labels)
            mask = tf.sequence_mask(self.sequence_lengths)
            losses = tf.boolean_mask(losses, mask)
            self.loss = tf.reduce_mean(losses)

        # for tensorboard
        tf.summary.scalar("loss", self.loss)

    def add_train_op(self):
        """
        Add train_op to self
        """
        with tf.variable_scope("train_step"):
            optimizer = tf.train.AdamOptimizer(self.lr)
            self.train_op = optimizer.minimize(self.loss)


    def add_init_op(self):
        self.init = tf.global_variables_initializer()


    def add_summary(self, sess):
        # tensorboard stuff
        self.merged = tf.summary.merge_all()
        self.file_writer = tf.summary.FileWriter(self.config.output_path, sess.graph)

    def build(self):
        self.add_placeholders()
        self.add_word_embeddings_op()
        self.add_logits_op()
        self.add_pred_op()
        self.add_loss_op()
        self.add_train_op()
        self.add_init_op()


    def predict_batch(self, sess, words):
        """
        Args:
            sess: a tensorflow session
            words: list of sentences
        Returns:
            labels_pred: list of labels for each sentence
            sequence_length
        """
        fd, sequence_lengths = self.get_feed_dict(words, dropout=1.0)

        if self.config.crf:
            viterbi_sequences = []
            logits, transition_params = sess.run([self.logits, self.transition_params],
                                                 feed_dict=fd)
            # iterate over the sentences
            for logit, sequence_length in zip(logits, sequence_lengths):
                # keep only the valid time steps
                logit = logit[:sequence_length]
                viterbi_sequence, viterbi_score = tf.contrib.crf.viterbi_decode(
                    logit, transition_params)
                viterbi_sequences += [viterbi_sequence]

            return viterbi_sequences, sequence_lengths

        else:
            labels_pred = sess.run(self.labels_pred, feed_dict=fd)

            return labels_pred, sequence_lengths


    def run_epoch(self, sess, train, dev, tags, epoch):
        """
        Performs one complete pass over the train set and evaluate on dev
        Args:
            sess: tensorflow session
            train: dataset that yields tuple of sentences, tags
            dev: dataset
            tags: {tag: index} dictionary
            epoch: (int) number of the epoch
        """
        nbatches = (len(train) + self.config.batch_size - 1) / self.config.batch_size
        prog = Progbar(target=nbatches)
        for i, (words, labels) in enumerate(minibatches(train, self.config.batch_size)):
            fd, _ = self.get_feed_dict(words, labels, self.config.lr, self.config.dropout)

            _, train_loss, summary = sess.run([self.train_op, self.loss, self.merged], feed_dict=fd)

            prog.update(i + 1, [("train loss", train_loss)])

            # tensorboard
            if i % 10 == 0:
                self.file_writer.add_summary(summary, epoch * nbatches + i)

        acc, f1 = self.run_evaluate(sess, dev, tags)
        self.logger.info("- dev acc {:04.2f} - f1 {:04.2f}".format(100 * acc, 100 * f1))
        return acc, f1

    def run_evaluate(self, sess, test, tags):
        """
        Evaluates performance on test set
        Args:
            sess: tensorflow session
            test: dataset that yields tuple of sentences, tags
            tags: {tag: index} dictionary
        Returns:
            accuracy
            f1 score
        """
        accs = []
        correct_preds, total_correct, total_preds = 0., 0., 0.
        for words, labels in minibatches(test, self.config.batch_size):
            labels_pred, sequence_lengths = self.predict_batch(sess, words)

            for lab, lab_pred, length in zip(labels, labels_pred, sequence_lengths):
                lab = lab[:length]
                lab_pred = lab_pred[:length]

                accs += map(lambda element: element[0] == element[1], zip(lab, lab_pred))

                lab_chunks = set(get_chunks(lab, tags))
                lab_pred_chunks = set(get_chunks(lab_pred, tags))
                correct_preds += len(lab_chunks & lab_pred_chunks)
                total_preds += len(lab_pred_chunks)
                total_correct += len(lab_chunks)

        p = correct_preds / total_preds if correct_preds > 0 else 0
        r = correct_preds / total_correct if correct_preds > 0 else 0
        f1 = 2 * p * r / (p + r) if correct_preds > 0 else 0
        acc = np.mean(accs)
        return acc, f1


    def train(self, train, dev, tags):
        """
        Performs training with early stopping and lr exponential decay
        Args:
            train: dataset that yields tuple of sentences, tags
            dev: dataset
            tags: {tag: index} dictionary
        """
        best_score = 0
        saver = tf.train.Saver()
        # for early stopping
        nepoch_no_imprv = 0
        with tf.Session() as sess:
            ckpt = tf.train.get_checkpoint_state(self.config.model_output)
            # restore session
            if ckpt and ckpt.model_checkpoint_path:
                print(ckpt)
                saver.restore(sess,self.config.model_output)
            else:
                print("Begin to initialize ...")
                sess.run(self.init)
            # tensorboard
            self.add_summary(sess)
            for epoch in range(self.config.nepochs):
                self.logger.info("Epoch {:} out of {:}".format(epoch + 1, self.config.nepochs))

                acc, f1 = self.run_epoch(sess, train, dev, tags, epoch)

                # decay learning rate
                self.config.lr *= self.config.lr_decay

                # early stopping and saving best parameters
                if f1 >= best_score:
                    nepoch_no_imprv = 0
                    if not os.path.exists(self.config.model_output):
                        os.makedirs(self.config.model_output)
                    saver.save(sess, self.config.model_output)
                    best_score = f1
                    self.logger.info("- new best score!")

                else:
                    nepoch_no_imprv += 1
                    if nepoch_no_imprv >= self.config.nepoch_no_imprv:
                        self.logger.info("- early stopping {} epochs without improvement".format(
                            nepoch_no_imprv))
                        break


    def evaluate(self, test, tags):
        saver = tf.train.Saver()
        with tf.Session() as sess:
            self.logger.info("Testing model over test set")
            saver.restore(sess, self.config.model_output)
            acc, f1 = self.run_evaluate(sess, test, tags)
            self.logger.info("- test acc {:04.2f} - f1 {:04.2f}".format(100 * acc, 100 * f1))


    def interactive_shell(self, tags, processing_word):
        idx_to_tag = {idx: tag for tag, idx in tags.items()}
        saver = tf.train.Saver()
        with tf.Session() as sess:
            saver.restore(sess, self.config.model_output)
            self.logger.info("This is an interactive mode, enter a sentence:")
            while True:
                try:
                    sentence = raw_input("input> ")
                    #words_raw = sentence.strip().split(" ")  english words seperated by space
                    # words_raw = list(sentence.encode("utf-8"))

                    words_raw = character_separation(sentence)[0].split(' ')
                    words_raw = [unicode(word, 'utf-8') for word in words_raw]

                    words = map(processing_word, words_raw)
                    words = list(words)
                    #if type(words[0]) == tuple:
                    #    words = zip(*words)
                    pred_ids, _ = self.predict_batch(sess, [words])
                    preds = map(lambda idx: idx_to_tag[idx], list(pred_ids[0]))
                    print(list(preds))
                    print_sentence(self.logger, {"x": words_raw, "y": preds})
                except EOFError:
                    print("Closing session.")
                    break

    def interactive(self, tags, processing_word):
        idx_to_tag = {idx: tag for tag, idx in tags.items()}
        saver = tf.train.Saver()
        with tf.Session() as sess:
            saver.restore(sess, self.config.model_output)
            self.logger.info("This is an interactive mode, enter a sentence:")
            while True:
                try:
                    sentence = raw_input("input> ")
                    #words_raw = sentence.strip().split(" ")  english words seperated by space
                    # words_raw = list(sentence.encode("utf-8"))

                    words_raw = character_separation(sentence)[0].split(' ')
                    words_raw = [unicode(word, 'utf-8') for word in words_raw]

                    words = map(processing_word, words_raw)
                    words = list(words)
                    #if type(words[0]) == tuple:
                    #    words = zip(*words)
                    pred_ids, _ = self.predict_batch(sess, [words])
                    preds = map(lambda idx: idx_to_tag[idx], list(pred_ids[0]))
                    # print(list(preds))
                    print_sentence(self.logger, {"x": words_raw, "y": preds})
                    return list(preds)
                except EOFError:
                    print("Closing session.")
                    break