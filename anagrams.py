from time import time
import re
import itertools
import cPickle as pickle
from Tree import Tree
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

    # find all sets of hash keys that can make the target key
    def subset(self,length,target):
        active_dict = self.update_sub_words(length, target) # <0.04s every time
        self.count = 0
        return self.subset_recursive(length, target, 1, active_dict, 1)

    def key_copy(self,inp_dict):
        out = {}
        for k,v in inp_dict.iteritems():
            try:
                out[k] = v[:]
            except TypeError:
                out[k] = v
        return out

    # recursive helper for the previous function
    def subset_recursive(self,remaining,current_target,passed_key,active_dict,depth):
        self.count += 1
        if passed_key == current_target:
            if remaining == 0:
                return Tree(passed_key)
            return None
        if passed_key > current_target or remaining == 0:
            return None
        reduced_target = current_target / passed_key
        if reduced_target in self.memoization:
            mem = self.memoization[reduced_target]
            if mem == None:
                return None
            out = self.tree_copy(mem)
            out.setCargo(passed_key)
            return out
        branch = []
        for size in range(2, remaining + 1):
            if size in active_dict and (remaining - size > size - 1 or remaining - size == 0):
                for key in active_dict[size][:]:
                    if reduced_target % key == 0:
                        x = self.subset_recursive(remaining - size,
                                                  reduced_target,
                                                  key,
                                                  self.key_copy(active_dict),
                                                  depth + 1)
                        if x is not None:
                            branch.append(x)
                        # active_dict[size].remove(key)
                    if key > reduced_target:
                        break
        if len(branch) > 0:
                output = Tree(passed_key, branch)
        else:
            output = None
        self.memoization[reduced_target] = output
        return output

    def traverse_tree(self, inp_tree, cargo_fun=lambda x: x):
        self.complete_sets = []
        self.traverse_tree_recursive(inp_tree, list(), cargo_fun)
        return self.complete_sets

    def traverse_tree_recursive(self, inp_tree, partial, cargo_fun):
        if not inp_tree.isRoot():
            # partial.append(self.value_dict[inp_tree.getCargo()])
            partial.append(cargo_fun(inp_tree.getCargo()))
        if inp_tree.isBranch():
            self.complete_sets.append(tuple(partial))
            return
        for child in inp_tree.getChildren():
            self.traverse_tree_recursive(child, partial[:], cargo_fun)
        return

    def tree_copy(self,src_tree):
        new_tree = Tree(src_tree.data)
        for child in src_tree.getChildren():
            c = self.tree_copy(child)
            new_tree.addChild(c)
        return new_tree

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

    def create_an_tree(self, word):
        word = word.upper()
        word = re.sub(r'\s', '', word)
        value = self.word_value(word)
        length = len(word)
        an_tree = self.subset(length, value)
        return an_tree

    def all_anagrams(self, word):
        an_tree = self.create_an_tree(word)
        an_list = self.traverse_tree(an_tree, lambda x: self.value_dict[x])
        return an_list

    def create_phrase_tree(self, an_tree):
        if an_tree.isRoot():
            assert an_tree.getCargo() == 1, "Tree must start with value=1 at root"
            an_tree.setCargo('')
        return self.create_phrase_tree_recursive(an_tree)

    def create_phrase_tree_recursive(self, an_tree):
        old_children = an_tree.getChildren()
        new_children = []
        for c in old_children:
            for word in self.value_dict[c.getCargo()]:
                new_tree = self.create_phrase_tree_recursive(Tree(word, c.getChildren()))
                new_children.append(new_tree)
        return Tree(an_tree.getCargo(), new_children)

    def all_anagram_phrases(self, word):
        an_tree = self.create_an_tree(word)
        phrase_tree = self.create_phrase_tree(an_tree)
        return self.traverse_tree(phrase_tree)

    def sorted_anagram_phrases(self, word):
        phrases = self.all_anagram_phrases(word)
        return sorted(phrases, key=frequencies.phrase_likelihood, reverse=True)

def main():
    word = 'ORANGEJUICEBOX'
    # word = 'ORANGES'
    an = Anagrammer('raw_data/2of12inf.txt', newest_letter_map)
    s = time()
    t = an.create_an_tree(word)
    f = an.traverse_tree(t)
    # print f
    print len(f)
    print time()-s

    # print list(an.all_anagram_phrases(word))
    # pt = an.create_phrase_tree(t)
    # print [c.data for c in pt.getChildren()]
    print an.sorted_anagram_phrases(word)[:10]
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
