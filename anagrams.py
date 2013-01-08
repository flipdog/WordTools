


from time import time
import re
import itertools
import math
from Tree import Tree
import cPickle as pickle
import os

newest_letter_map = {'A': 2, 'C': 5, 'B': 3, 'E': 11, 'D': 7, 'G': 17, 'F': 13, 'I': 23, 'H': 19, 'K': 31, 'J': 29, 'M': 41, 'L': 37, 'O': 47, 'N': 43, 'Q': 59, 'P': 53, 'S': 67, 'R': 61, 'U': 73, 'T': 71, 'W': 83, 'V': 79, 'Y': 97, 'X': 89, 'Z': 101}

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
        

    def update_sub_words(self,length,target):
        sub_dict = {}
        for i in range(length+1):
            try:
                for key in self.word_dict[i].keys():
                    if target%key == 0:
                        try:
                            sub_dict[i].append(key)
                        except KeyError:
                            sub_dict[i] = []
                            sub_dict[i].append(key)
                sub_dict[i].sort()
            except KeyError:
                pass
        return sub_dict

    # find all sets of hash keys that can make the target key
    def subset(self,length,target):
        active_dict = self.update_sub_words(length,target) # <0.04s every time
        self.count = 0
        return self.subset_recursive(length,target,1,active_dict,1)

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
        self.count +=1
        if passed_key == current_target:
            if remaining == 0:
                return Tree(self.value_dict[passed_key])
            return None
        if passed_key > current_target or remaining == 0:
            return None
        reduced_target = current_target / passed_key
        try:
            mem = self.memoization[reduced_target]
            if mem == None:
                return None
            out = self.tree_copy(mem)
            out.setCargo(self.value_dict[passed_key])
            return out
        except KeyError:
            pass
        branch = []
        for size in range(2,remaining+1):
            try:
                for key in active_dict[size][:]:
                    if key <= reduced_target and reduced_target%key == 0:
                        if(remaining-size > size-1 or remaining-size == 0):
                            x = self.subset_recursive(remaining-size,reduced_target,key,self.key_copy(active_dict),depth+1)
                            if not  x == None:
                                branch.append(x)
                            active_dict[size].remove(key)
                    if key > reduced_target:
                        break
            except KeyError:
                pass
        if len(branch) > 0:
            try:
                output = Tree(self.value_dict[passed_key],branch)
            except KeyError:
                output = Tree('',branch)
        else:
            output = None
        self.memoization[reduced_target] = output
        return output


    def key_copy(self,inp_dict):
        out = {}
        for k,v in inp_dict.iteritems():
            try:
                out[k] = v[:]
            except TypeError:
                out[k] = v
        return out

    def traverse_tree(self,inp_tree):
        self.complete_sets = []
        self.traverse_tree_recursive(inp_tree,list())
        return self.complete_sets

    def traverse_tree_recursive(self,inp_tree,partial):
        if not inp_tree.isRoot():
            partial.append(inp_tree.getCargo())
        if inp_tree.isBranch():
            self.complete_sets.append(tuple(partial))
            return
        for child in inp_tree.getChildren():
            self.traverse_tree_recursive(child,partial[:])
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
            return false
        for letter in word1:
            letters[letter] += 1
        for letter in word2:
            letters[letter] -= 1
        for letter in letters.keys():
            if not letters[letter] == 0:
                return False
        return True

    
    def all_anagrams(self,word):
        word = word.upper()
        word = re.sub(r'\s', '', word)
        value = self.word_value(word)
        length = len(word)
        an_tree = self.subset(length,value)
        an_list = self.traverse_tree(an_tree)
        return an_list



def main():
    s = time()
    f = an.all_anagrams('ORANGEJUICEBOXES')
    print len(f)
    #for k in g:
    #    print k
    #writer = open('shakespeare_output.txt','w')
    #for k in g:
    #    writer.write(str(k)+'\n')
    #writer.close()
    #f.prettyTree()
    print time()-s
    #an.dump_memo(an.memoization)
    return

#import cProfile
#cProfile.run('main()')

an = Anagrammer('C:/Users/flipdog/Desktop/wordtools/bjflavors.txt', newest_letter_map)
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
