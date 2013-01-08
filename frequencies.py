from __future__ import division
from collections import defaultdict
import re

raw_onegrams = defaultdict(lambda: 0)

with open('raw_data/all.num.o5.txt', 'r') as f:
    total = 0
    for i, line in enumerate(f.readlines()):
        if '!' in line or '&' in line:
            continue
        freq, word, pos, num_files = line.split(' ')
        word = word.upper()
        freq = int(freq)
        raw_onegrams[word] += freq
        total += freq

for word in raw_onegrams:
    raw_onegrams[word] = raw_onegrams[word] / total

onegrams = defaultdict(lambda: 1 / total, raw_onegrams)

raw_bigrams = defaultdict(lambda: 0)

with open('raw_data/bigrams.txt', 'r') as f:
    total = 0
    for i, line in enumerate(f.readlines()):
        words, count = line.split('\t')
        count = int(count)
        if count < 5:
            continue
        if re.search(r'[^a-zA-Z0-9 -_]', words) or re.search(r'0[A-Z]+\.0', words):
            continue
        words = words.upper()
        word0, word1 = words.split(' ')
        raw_bigrams[(word0, word1)] += count
        total += count
        # if i % 10000 == 0:
        #     print i, "/", "5612484"

for pair in raw_bigrams:
    raw_bigrams[pair] = raw_bigrams[pair] / total

bigrams = defaultdict(lambda: 1 / total, raw_bigrams)


def following_probability(word0, word1):
    """
    Conditional probability that word1 follows word0 in a phrase
    """
    return bigrams[(word0, word1)] / onegrams[word0]


def onegram_likelihood(phrase):
    return product([onegrams[w] for w in phrase])


def bigram_likelihood(phrase):
    return onegrams[phrase[0]] * product([following_probability(phrase[i], phrase[i + 1]) for i in range(len(phrase) - 1)])


def product(arr):
    result = 1
    for x in arr:
        result *= x
    return result
