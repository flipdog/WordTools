from __future__ import division
import cPickle as pickle
import re

raw_onegrams = {}

with open('raw_data/all.num.o5.txt', 'r') as f:
    onegram_total = 0
    for i, line in enumerate(f.readlines()):
        if '!' in line or '&' in line:
            continue
        freq, word, pos, num_files = line.split(' ')
        word = word.upper()
        freq = int(freq)
        if word not in raw_onegrams:
            raw_onegrams[word] = 0
        raw_onegrams[word] += freq
        onegram_total += freq

with open('data/raw_onegrams.pck', 'wb') as f:
    pickle.dump(raw_onegrams, f)

raw_bigrams = {}

with open('raw_data/bigrams.txt', 'r') as f:
    bigram_total = 0
    for i, line in enumerate(f.readlines()):
        words, count = line.split('\t')
        count = int(count)
        if count < 5:
            continue
        if re.search(r'[^a-zA-Z0-9 -_]', words) or re.search(r'0[A-Z]+\.0', words):
            continue
        words = words.upper()
        word0, word1 = words.split(' ')
        if (word0, word1) not in raw_bigrams:
            raw_bigrams[(word0, word1)] = 0
        raw_bigrams[(word0, word1)] += count
        bigram_total += count

with open('data/raw_bigrams.pck', 'wb') as f:
    pickle.dump(raw_bigrams, f)