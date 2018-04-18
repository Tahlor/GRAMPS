import requests


def extract_words_to_set(json, ws):

    # words = []
    for d in json:
        # words.append(d['word'])
        ws.add(d['word'])
    # return words


def get_all_related_words(topics):

    word_set = set()

    for word in topics:

        # general topic request
        r = requests.get('https://api.datamuse.com/words?topics={}'.format(word))
        # print (r.json())
        extract_words_to_set(r.json(), word_set)
        # print(word_set)

        # similar meaning
        r = requests.get('https://api.datamuse.com/words?ml={}'.format(word))
        extract_words_to_set(r.json(), word_set)

        # adjectives often used
        r = requests.get('https://api.datamuse.com/words?rel_jjb={}'.format(word))
        extract_words_to_set(r.json(), word_set)

        # nouns often used
        r = requests.get('https://api.datamuse.com/words?rel_jja={}'.format(word))
        extract_words_to_set(r.json(), word_set)

        # words triggered by
        r = requests.get('https://api.datamuse.com/words?rel_trg={}'.format(word))
        extract_words_to_set(r.json(), word_set)

        # is a kind of
        r = requests.get('https://api.datamuse.com/words?rel_spc={}'.format(word))
        extract_words_to_set(r.json(), word_set)

        # is a parent class of
        r = requests.get('https://api.datamuse.com/words?rel_gen={}'.format(word))
        extract_words_to_set(r.json(), word_set)

        # comprises (car -> accelerator)
        r = requests.get('https://api.datamuse.com/words?rel_com={}'.format(word))
        extract_words_to_set(r.json(), word_set)

        # "part of"
        r = requests.get('https://api.datamuse.com/words?rel_par={}'.format(word))
        extract_words_to_set(r.json(), word_set)

        # frequent followers
        r = requests.get('https://api.datamuse.com/words?rel_bga={}'.format(word))
        extract_words_to_set(r.json(), word_set)

        # frequent predecessors
        r = requests.get('https://api.datamuse.com/words?rel_bgb={}'.format(word))
        extract_words_to_set(r.json(), word_set)

        # synonyms
        r = requests.get('https://api.datamuse.com/words?rel_syn={}'.format(word))
        extract_words_to_set(r.json(), word_set)


        #
        # # repeat with all new found words?


    return word_set


def get_rhymes(word, weak_rhymes=False):

    word_set = set()
    r = requests.get('https://api.datamuse.com/words?rel_rhy={}'.format(word))
    extract_words_to_set(r.json(), word_set)


    if weak_rhymes:
        r = requests.get('https://api.datamuse.com/words?rel_nry={}'.format(word))
        extract_words_to_set(r.json(), word_set)

    # r = requests.get('https://api.datamuse.com/words?rel_cns={}'.format(word))

    return word_set