from time import time
import re
import itertools
import cPickle as pickle
from Tree import Tree
import frequencies
import sys

newest_letter_map = {'A': 2, 'C': 5, 'B': 3, 'E': 11, 'D': 7, 'G': 17, 'F': 13, 'I': 23, 'H': 19, 'K': 31, 'J': 29, 'M': 41, 'L': 37, 'O': 47, 'N': 43, 'Q': 59, 'P': 53, 'S': 67, 'R': 61, 'U': 73, 'T': 71, 'W': 83, 'V': 79, 'Y': 97, 'X': 89, 'Z': 101}


def product(arr):
    result = 1
    for x in arr:
        result *= x
    return result


class Anagrammer():
    def __init__(self, dictionary_file, letter_map):
        self.count = 0
        self.letter_map = letter_map
        self.word_dict = {}
        self.value_dict = {}
        self.read_dictionary(dictionary_file)
        self.memoization = {}  # self.load_memo()

    def load_memo(self):
        try:
            p = open('memoize.p', 'rb')
            memo = pickle.load(p)
            p.close()
            return memo
        except IOError:
            return None

    def dump_memo(self,memo):
        print foo
        try:
            p = open('memoize.p','wb')
            pickle.dump(memo,p)
            return True
        except IOError:
            return False

    def read_dictionary(self, FILE_NAME):
        reader = open(FILE_NAME,'r')
        for line in reader:
            self.create_entry(line.strip())
        reader.close()

    def words_containing(self,word):
        val = self.word_value(word)
        subs = []
        for i in range(len(word),25):
            try:
                for key in self.word_dict[i].keys():
                    for sec in self.value_dict[key]:
                        if word in sec:
                            subs.append(sec)
                subs.sort()
            except KeyError:
                pass
        return subs

    def create_entry(self, word):
        word = word.upper().strip()
        word = re.sub(r'\s', '', word)
        if not len(word) in self.word_dict.keys():
            self.word_dict[len(word)] = {}
        value = self.word_value(word)
        try:
            self.word_dict[len(word)][value].append(word)
        except KeyError:
            self.word_dict[len(word)][value] = []
            self.word_dict[len(word)][value].append(word)
        try:
            self.value_dict[value].append(word)
        except KeyError:
            self.value_dict[value] = []
            self.value_dict[value].append(word)

    def word_value(self, word):
        word = word.upper()
        word = re.sub(r'\s', '', word)
        value = 1
        for letter in word:
            value = value * self.letter_map[letter]
        return value

    def sub_words_reverse(self,word):
        length = len(word)
        val = self.word_value(word)
        lst = []
        for i in range(length,25):
            if i in self.word_dict:
                for key in self.word_dict[i]:
                    if key%val == 0:
                        lst.append(self.value_dict[key])
        return lst

    def update_sub_words(self, length, target):
        sub_dict = {}
        for i in range(length + 1):
            if i in self.word_dict:
                for key in self.word_dict[i]:
                    if target % key == 0:
                        sub_dict.setdefault(i, []).append(key)
                if i in sub_dict:
                    sub_dict[i].sort()
        return sub_dict

    # check if two words are anagrams - theoretically optimized
    # time is n+n+26 with usually small n
    # effectively constant time <100
    def is_anagram(self, word1, word2):
        letters = {'A': 0, 'C': 0, 'B': 0, 'E': 0, 'D': 0, 'G': 0, 'F': 0, 'I': 0, 'H': 0, 'K': 0, 'J': 0, 'M': 0, 'L': 0, 'O': 0, 'N': 0, 'Q': 0, 'P': 0, 'S': 0, 'R': 0, 'U': 0, 'T': 0, 'W': 0, 'V': 0, 'Y': 0, 'X': 0, 'Z': 0}
        if not len(word1) == len(word2):
            return False
        for letter in word1:
            letters[letter] += 1
        for letter in word2:
            letters[letter] -= 1
        for letter in letters.keys():
            if not letters[letter] == 0:
                return False
        return True

    def sorted_anagram_phrases(self, word, beam_width=1000):
        phrases = self.phrase_tree(word, beam_width)
        return sorted(phrases, key=frequencies.phrase_likelihood, reverse=True)

    def phrase_tree(self, word, beam_width=1000):
        self.memoization = {}
        word = word.upper()
        word = re.sub(r'\s', '', word)
        target = self.word_value(word)
        length = len(word)
        active_dict = self.update_sub_words(length, target)
        root_tree = Tree(('', target, length))
        active_set = [root_tree]
        finished_set = []
        while len(active_set) > 0:
            new_layer = []
            for t in active_set:
                word, reduced_target, remaining_letters = t.getCargo()
                # print "expanding:", [x[0] for x in t.getAllCargoes()], reduced_target
                if remaining_letters == 0:
                    finished_set.append([c[0] for c in t.getAllCargoes()[1:]])
                elif reduced_target in self.memoization:
                    # print "cache hit:", [x.data[0] for x in self.memoization[reduced_target]]
                    continue
                else:
                    for size in range(2, remaining_letters + 1):
                        if size in active_dict:
                            for key in active_dict[size]:
                                if reduced_target % key == 0:
                                    new_children = [Tree((w, reduced_target / key, remaining_letters - size)) for w in self.value_dict[key]]
                                    t.addChildren(new_children)
                                    new_layer.extend(new_children)
                    self.memoization[reduced_target] = t.getChildren()
                # print "children after expansion:", [x.data[0] for x in t.getChildren()]
                # self.prune_upward(t, length)
            new_layer.sort(key=lambda t: frequencies.phrase_likelihood([c[0] for c in t.getAllCargoes()[1:]]), reverse=True)
            active_set = new_layer[:beam_width]
        return finished_set


def main():
    # word = 'ORANGEJUICEBOXES'
    word = sys.argv[1]
    if len(sys.argv) > 2:
        beam_width = int(sys.argv[2])
    else:
        beam_width = 10000
    # word = 'WILLIAMSHAKESPEARE'
    an = Anagrammer('raw_data/2of12inf.txt', newest_letter_map)

    s = time()
    print an.sorted_anagram_phrases(word, beam_width=beam_width)[:30]
    print time() - s
    return

if __name__ == '__main__':
    main()

#import cProfile
#cProfile.run('main()')

# an = Anagrammer('C:/Users/flipdog/Desktop/wordtools/bjflavors.txt', newest_letter_map)
#main()
"""
cities = []
reader = open('worldcitiespop.txt','r')
for line in reader:
    cap = line.strip().upper().split(',')
    cities.append(cap[1])
reader.close()


def contains_city(word):
    for city in cities:
        if city in word:
            print city
"""
def transdeletion(word):
    word = word.upper().strip()
    word = re.sub(r'\s', '', word)
    for i in range(len(word)):
        n_word = word[:i]+word[i+1:]
        try:
            print an.value_dict[an.word_value(n_word)], word[i]
        except KeyError:
            pass

def transinsertion(word):
    additions = {}
    for extension in itertools.combinations_with_replacement('ABCDEFGHIJKLMNOPQRSTUVWXYZ',1):
        extension_string = ''
        trans_extend = []
        for letter in extension:
            extension_string = extension_string + letter
        try:
            trans_extend = an.value_dict[an.word_value(word+extension_string)]
        except:
            pass
        if len(trans_extend) > 0:
            additions[extension_string] = trans_extend
    return additions

def doubletrans(word):
    word = word.upper().strip()
    word = re.sub(r'\s', '', word)
    for extension in itertools.combinations_with_replacement('ABCDEFGHIJKLMNOPQRSTUVWXYZ',1):
        extension_string = ''
        trans_extend = []
        for letter in extension:
            extension_string = extension_string + letter
        transdeletion(word)
