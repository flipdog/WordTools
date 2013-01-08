from time import time
import re
import itertools
import cPickle as pickle
import frequencies

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
        self.memoization = {} #self.load_memo()


    def load_memo(self):
        try:
            p = open('memoize.p','rb')
            memo = pickle.load(p)
            p.close()
            return memo
        except IOError:
            return None

    def dump_memo(self,memo):
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
            try:
                for key in self.word_dict[i].keys():
                    if key%val == 0:
                        lst.append(self.value_dict[key])
            except KeyError:
                pass
        return lst


    def update_sub_words(self, length, target):
        sub_dict = {}
        for i in range(length + 1):
            try:
                for key in self.word_dict[i].keys():
                    if target % key == 0:
                        sub_dict.setdefault(i, []).append(key)
                sub_dict[i].sort()
            except KeyError:
                pass
        return sub_dict

    def subset(self, length, target):
        possible_vals = self.update_sub_words(length, target)
        active_set = set([(tuple(), length)])
        while True:
            mod = False
            new_active_set = set([s for s in active_set if s[1] == 0])
            for hashes, remaining_letters in active_set:
                assert target % product(hashes) == 0
                remaining_hash = target / product(hashes)
                for i in range(1, remaining_letters + 1):
                    if i in possible_vals:
                        for val in possible_vals[i]:
                            if remaining_hash % val == 0:
                                new_hashes = tuple(sorted(hashes + (val,)))
                                new_active_set.add((new_hashes, remaining_letters - i))
                                mod = True
            active_set = new_active_set
            if not mod:
                break
        return [s[0] for s in active_set]

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

    def all_anagrams(self, word):
        word = word.upper()
        word = re.sub(r'\s', '', word)
        value = self.word_value(word)
        length = len(word)
        hash_sets = self.subset(length, value)
        anagrams = []
        for s in hash_sets:
            anagrams.append(tuple([self.value_dict[v] for v in s]))
        return anagrams

    def all_anagram_phrases(self, word):
        anagram_sets = self.all_anagrams(word)
        all_phrases = []
        for ana_set in anagram_sets:
            for sorted_ana_set in itertools.permutations(ana_set):
                phrases = [[]]
                for anas in sorted_ana_set:
                    new_phrases = []
                    for p in phrases:
                        for a in anas:
                            new_phrases.append(p + [a])
                    phrases = new_phrases
                all_phrases.extend(phrases)
        return all_phrases

    def sorted_anagram_phrases(self, word):
        phrases = self.all_anagram_phrases(word)
        return sorted(phrases, key=frequencies.phrase_likelihood, reverse=True)

def main():
    s = time()
    an = Anagrammer('raw_data/sowpods.txt', newest_letter_map)
    f = an.all_anagrams('ORANGES')
    print time()-s
    print f[:50]
    #for k in g:
    #    print k
    #writer = open('shakespeare_output.txt','w')
    #for k in g:
    #    writer.write(str(k)+'\n')
    #writer.close()
    #f.prettyTree()
    #an.dump_memo(an.memoization)
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
