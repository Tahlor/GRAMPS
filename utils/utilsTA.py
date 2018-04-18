# -*- coding: utf-8 -*-
import os
import codecs
import collections
from six.moves import cPickle
import numpy as np
import re
import itertools
import pickle
from gensim.summarization.summarizer import summarize

class TextLoader():
    def __init__(self, data_dir, batch_size, seq_length, encoding=None, simple_vocab = True):
        self.data_dir = data_dir
        self.batch_size = batch_size
        self.seq_length = seq_length
        self.simple_vocab = simple_vocab
        
        if not os.path.isdir(data_dir):
            input_file = data_dir
            data_dir = os.path.pardir(input_file)
        else:
            input_file = os.path.join(data_dir, "input.txt")
        
        vocab_file = os.path.join(data_dir, "vocab.pkl")
        tensor_file = os.path.join(data_dir, "data.npy")
        

        # Let's not read vocab and data from file. We many change them.
        if True or not (os.path.exists(vocab_file) and os.path.exists(tensor_file)):
            print("reading text file")
            self.preprocess(input_file, vocab_file, tensor_file, encoding)
        else:
            print("loading preprocessed files")
            self.load_preprocessed(vocab_file, tensor_file)
        self.create_batches()
        self.reset_batch_pointer()

    def clean_str(self, string):
        """
        Tokenization/string cleaning for all datasets except for SST.
        Original taken from https://github.com/yoonkim/CNN_sentence/blob/master/process_data
        """
        string = re.sub(r"\n\s*", r" | ", string)
        string = re.sub(r"[^|^가-힣A-Za-z0-9(),!?\'\`]", " ", string)
        #string = re.sub(r"\'s", " \'s", string)
        #string = re.sub(r"\'ve", " \'ve", string)
        #string = re.sub(r"n\'t", " n\'t", string)
        #string = re.sub(r"\'re", " \'re", string)
        #string = re.sub(r"\'d", " \'d", string)
        #string = re.sub(r"\'ll", " \'ll", string)
        string = re.sub(r"[0-9]+", "  ", string)
        string = re.sub(r",", " , ", string)
        string = re.sub(r"!", " ! ", string)
        #string = re.sub(r"\(", " \( ", string)
        #string = re.sub(r"\)", " \) ", string)
        string = re.sub(r";", " ; ", string)
        string = re.sub(r":", " : ", string)
        string = re.sub(r"\?", " \? ", string)
        string = re.sub(r"\s{2,}", " ", string)
        return string.strip().lower()

    def build_vocab(self, sentences):
        """
        Builds a vocabulary mapping from word to index based on the sentences.
        Returns vocabulary mapping and inverse vocabulary mapping.
        """

        # Build vocabulary
        word_counts = collections.Counter(sentences)
        # Mapping from index to word
        vocabulary_inv = [x[0] for x in word_counts.most_common()]
        vocabulary_inv = list(sorted(vocabulary_inv))
        # Mapping from word to index
        vocabulary = {x: i for i, x in enumerate(vocabulary_inv)}
        return [vocabulary, vocabulary_inv]

    def preprocess(self, input_file, vocab_file, tensor_file, encoding):
        pickle_path = input_file.replace(".txt", ".pickle")

        failed = True
        if os.path.exists(pickle_path):
            try:
                with open(pickle_path, "rb") as pkl:
                    data = pickle.load(pkl)
                    failed = False
            except:
                pass
        if failed:
            with codecs.open(input_file, "r", encoding=encoding) as f:
                data = f.read()
                
            # Dump to pickle
            with open(pickle_path, "wb") as fobj:
                pickle.dump(data,fobj)


        # Optional text cleaning or make them lower case, etc.
        if self.simple_vocab:
            data = self.clean_str(data)        

        # This is not optimized, shouldn't be too bad though
        x_text = ["\n" if i == "|" else i for i in data.split()]
        #x_text = data.split()
        self.vocab, self.words = self.build_vocab(x_text)
        self.vocab_size = len(self.words)

        with open(vocab_file, 'wb') as f:
            cPickle.dump(self.words, f)
        
        """print(data[0:500])
        # print(data1[0:500])
        print(x_text[0:500])
        print("\n" in self.vocab)
        print([x for x in self.vocab if "\n" in x])
        Stop
        """

        #The same operation like this [self.vocab[word] for word in x_text]
        # index of words as our basic data
        self.tensor = np.array(list(map(self.vocab.get, x_text)))
        # Save the data to data.npy
        np.save(tensor_file, self.tensor)

    def load_preprocessed(self, vocab_file, tensor_file):
        with open(vocab_file, 'rb') as f:
            self.words = cPickle.load(f)
        self.vocab_size = len(self.words)
        self.vocab = dict(zip(self.words, range(len(self.words))))
        self.tensor = np.load(tensor_file)
        self.num_batches = int(self.tensor.size / (self.batch_size *
                                                   self.seq_length))

    def create_batches(self):
        self.num_batches = int(self.tensor.size / (self.batch_size *
                                                   self.seq_length))
        if self.num_batches==0:
            assert False, "Not enough data. Make seq_length and batch_size small."

        self.tensor = self.tensor[:self.num_batches * self.batch_size * self.seq_length]
        xdata = self.tensor
        ydata = np.copy(self.tensor)

        ydata[:-1] = xdata[1:]
        ydata[-1] = xdata[0]

        # Find end of line mark index
        #print(self.vocab)
        #print(self.words)

        self.endline_idx = self.vocab['\n']

        # Find synonym of endline words in corpus

        # Create sequence of vocab indices (inputs, outputs)
        # Giant list - [Steps in Epoch, Batch size, Sequence size]
        
        self.x_batches = np.split(xdata.reshape(self.batch_size, -1), self.num_batches, 1)
        self.y_batches = np.split(ydata.reshape(self.batch_size, -1), self.num_batches, 1)
        self.get_last_words()

    def get_last_words(self):
        self.last_words = np.copy(self.x_batches)
        for batch in self.last_words:
            for element in batch:
                last_word = element[::-1][0]
                for n, word in enumerate(element[::-1]):
                    if word == self.endline_idx and n + 1 < len(element):
                        last_word = self.get_non_symbol(element[::-1][n+1:])
                    element[::-1][n] = last_word
                #print(element)
                #print(np.asarray(self.words)[element])
        #print(np.asarray(self.words)[self.last_words[0][0]])
        #print(np.asarray(self.x_batches).shape)

    def get_non_symbol(self, l):
        for el in l:
            if self.words[el].isalpha():
                return el

        # If not found return empty line
        return self.endline_idx

    #X is input, Y is output
    def next_batch(self):
        x, y, last_words = self.x_batches[self.pointer], self.y_batches[self.pointer], self.last_words[self.pointer]
        self.pointer += 1
        return x, y, last_words

    def reset_batch_pointer(self):
        self.pointer = 0

    def get_last_word():
        pass
        
    def get_sentiment():
        pass

    def get_summary():
        gensim.summarization.summarizer.summarize(text, ratio=0.2, word_count=None, split=False)

if __name__ == "__main__":
    path = r"D:\PyCharm Projects\word-rnn-tensorflow\data"
    data_loader = TextLoader(path, 1, 100)
    x,y,z = data_loader.next_batch()
    print(data_loader.words[x[0].astype(int)])
    print(data_loader.words[z[0]])