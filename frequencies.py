from __future__ import division
from collections import defaultdict
import re
import cPickle as pickle

with open('data/raw_onegrams.pck', 'rb') as f:
    raw_onegrams = pickle.load(f)
onegram_total = sum(raw_onegrams.values())
for word in raw_onegrams:
    raw_onegrams[word] = raw_onegrams[word] / onegram_total
# onegrams = raw_onegrams
onegrams = defaultdict(lambda: 1 / onegram_total, raw_onegrams)

with open('data/raw_bigrams.pck', 'rb') as f:
    raw_bigrams = pickle.load(f)
bigram_total = sum(raw_bigrams.values())
for pair in raw_bigrams:
    raw_bigrams[pair] = raw_bigrams[pair] / bigram_total
# bigrams = defaultdict(lambda: 1 / bigram_total, raw_bigrams)
bigrams = raw_bigrams


def following_probability(word0, word1):
    """
    Conditional probability that word1 follows word0 in a phrase
    """
    word0, word1 = word0.upper(), word1.upper()
    if word0 in raw_onegrams and (word0, word1) in bigrams:
        return bigrams[(word0, word1)] / onegrams[word0]
    else:
        return 1 / onegram_total
    # return bigrams[(word0, word1)] / onegrams[word0]


# def onegram_likelihood(phrase):
#     return product([onegrams[w.upper()] for w in phrase])


def bigram_likelihood(phrase):
    return onegrams[phrase[0].upper()] * product([following_probability(phrase[i], phrase[i + 1]) for i in range(len(phrase) - 1)])


def phrase_likelihood(phrase):
    return bigram_likelihood([p.upper() for p in phrase])


def product(arr):
    result = 1
    for x in arr:
        result *= x
    return result
