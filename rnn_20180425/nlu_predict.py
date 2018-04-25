#!/usr/bin/env python
# -*- coding: utf-8 -*-
from data_utils import get_trimmed_glove_vectors, load_vocab, \
    get_processing_word
from general_utils import get_logger,print_sentence
from model import NERModel
from config import config
from data_utils import character_separation
import tensorflow as tf


class nlu():

    # load vocabs
    vocab_words = load_vocab(config.words_filename)
    vocab_tags = load_vocab(config.tags_filename)

    # get processing functions

    embeddings = get_trimmed_glove_vectors(config.trimmed_filename)

    # get logger
    # logger = get_logger(config.log_path)

    # build model
    model = NERModel(config, embeddings, ntags=len(vocab_tags),
                     logger=None)
    model.build()

    idx_to_tag = {idx: tag for tag, idx in vocab_tags.items()}
    saver = tf.train.Saver()
    sess = tf.Session()
    saver.restore(sess, config.model_output)
    # model.logger.info("This is an interactive mode, enter a sentence:")

    @staticmethod
    def rec(sentence):
        try:

            processing_word = get_processing_word(nlu.vocab_words,
                                                  lowercase=config.lowercase)
            # print character_separation(sentence)[0]

            words_raw = character_separation(sentence)[0].split(' ')
            # for word in words_raw:
            #     if type(word)==str:
            words_raw = [unicode(word, 'utf-8') for word in words_raw]
            # words_raw = [word.decode('utf-8') for word in words_raw]
                # else:
                    # words_raw = [unicode(word, 'utf-8') for word in words_raw]

            words = map(processing_word, words_raw)
            words = list(words)
            pred_ids, _ = nlu.model.predict_batch(nlu.sess, [words])
            preds = map(lambda idx: nlu.idx_to_tag[idx], list(pred_ids[0]))
            # print(list(preds))
            print_sentence(nlu.model.logger, {"x": words_raw, "y": preds})
            return list(preds)
        except EOFError:
            print("Closing session.")


# nlu.rec('请播放电视剧三生三世十里桃花')
# nlu.rec('请播放电视剧三生三世十里桃花')
# nlu.rec('请播放电视剧三生三世十里桃花')