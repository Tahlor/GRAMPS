from __future__ import print_function
import numpy as np
import tensorflow as tf

import argparse
import time
import os
from six.moves import cPickle

from utils import TextLoader
from model import Model

import datamuser as dm

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--save_dir', type=str, default='save',
                       help='model directory to load stored checkpointed models from')
    parser.add_argument('-n', type=int, default=200,
                       help='number of words to sample')
    parser.add_argument('--prime', type=str, default=' ',
                       help='prime text')
    parser.add_argument('--pick', type=int, default=1,
                       help='1 = weighted pick, 2 = beam search pick')
    parser.add_argument('--width', type=int, default=4,
                       help='width of the beam search')
    parser.add_argument('--sample', type=int, default=1,
                       help='0 to use max at each timestep, 1 to sample at each timestep, 2 to sample on spaces')
    parser.add_argument('--count', '-c', type=int, default=1,
                       help='number of samples to print')
    parser.add_argument('--quiet', '-q', default=False, action='store_true',
                       help='suppress printing the prime text (default false)')

    args = parser.parse_args()
    sample_line_by_line(args)

def sample(args):
    with open(os.path.join(args.save_dir, 'config.pkl'), 'rb') as f:
        saved_args = cPickle.load(f)
    with open(os.path.join(args.save_dir, 'words_vocab.pkl'), 'rb') as f:
        words, vocab = cPickle.load(f)
    model = Model(saved_args, True)
    with tf.Session() as sess:
        tf.global_variables_initializer().run()
        saver = tf.train.Saver(tf.global_variables())
        ckpt = tf.train.get_checkpoint_state(args.save_dir)
        if ckpt and ckpt.model_checkpoint_path:
            saver.restore(sess, ckpt.model_checkpoint_path)


            for _ in range(args.count):
              print(model.sample(sess, words, vocab, args.n, args.prime, args.sample, args.pick, args.width, args.quiet))


def sample_line_by_line(args):
    with open(os.path.join(args.save_dir, 'config.pkl'), 'rb') as f:
        saved_args = cPickle.load(f)
    with open(os.path.join(args.save_dir, 'words_vocab.pkl'), 'rb') as f:
        words, vocab = cPickle.load(f)
    model = Model(saved_args, True)
    with tf.Session() as sess:
        tf.global_variables_initializer().run()
        saver = tf.train.Saver(tf.global_variables())
        ckpt = tf.train.get_checkpoint_state(args.save_dir)
        if ckpt and ckpt.model_checkpoint_path:
            saver.restore(sess, ckpt.model_checkpoint_path)

            lines = []
            prime = args.prime
            num_lines = 8
            words_per_sample = 6  # was args.n.  what we want is to know how long a line is
            topic = 'weed'

            # get topical words

            # related_words = list(dm.get_all_related_words([topic]))

            quiet = False  # print the first prime but not all others
            for l in range(num_lines):
                # force end word from related words, or to rhyme with last word

                # last_rhymes = dm.get_rhymes(prime.split()[-1])

                line = model.sample(sess, words, vocab, words_per_sample, prime, args.sample, args.pick, args.width, quiet)
                quiet = True

                # evaluate line, keep or not keep


                prime = line + '\n'  # next time to prime with all preceding text

            print (line)





if __name__ == '__main__':
    main()
