from anagrams import Anagrammer as grammer
import itertools
xmen = ['BEAST','PROFESSOR','XAVIER','PROFESSORX','CYCLOPS','WOLVERINE','STORM','PHOENIX','JEANGREY','ICEMEAN','ARCHANGEL','HAVOK','ROGUE','GAMBIT','NIGHTCRAWLER','SHADOWCAT','MAGNETO', 'JUBILEE', 'DARWIN', 'BANSHEE', 'MIMIC']
jla = ['SUPERMAN','BATMAN','WONDERWOMAN','FLASH','GREENLANTERN','AQUAMAN','MARTAINMANHUNTER','GREENARROW','ATOM','HAWKMAN','BLACKCANARY','PHANTOMSTRANGER','ELONGATEDMAN']
states = ['Alabama','Alaska','Arizona','Arkansas','California','Colorado','Connecticut','Delaware','Florida','Georgia','Hawaii','Idaho','Illinois','Indiana','Iowa','Kansas','Kentucky','Louisiana','Maine','Maryland','Massachusetts','Michigan','Minnesota','Mississippi','Missouri','Montana','Nebraska','Nevada','New Hampshire','New Jersey','New Mexico','New York','North Carolina','North Dakota','Ohio','Oklahoma','Oregon','Pennsylvania','Rhode Island','South Carolina','South Dakota','Tennessee','Texas','Utah','Vermont','Virginia','Washington','West Virginia','Wisconsin','Wyoming']

newest_letter_map = {'A': 2, 'C': 5, 'B': 3, 'E': 11, 'D': 7, 'G': 17, 'F': 13, 'I': 23, 'H': 19, 'K': 31, 'J': 29, 'M': 41, 'L': 37, 'O': 47, 'N': 43, 'Q': 59, 'P': 53, 'S': 67, 'R': 61, 'U': 73, 'T': 71, 'W': 83, 'V': 79, 'Y': 97, 'X': 89, 'Z': 101}

an = grammer('C:/Users/flipdog/Desktop/wordtools/sowpods.txt', newest_letter_map)

def transinsertion(word, depth):
    additions = {}
    for extension in itertools.combinations_with_replacement('ABCDEFGHIJKLMNOPQRSTUVWXYZ',depth):
        extension_string = ''
        for letter in extension:
            extension_string = extension_string + letter
        trans_extend = an.all_anagrams(word+extension_string)
        if len(trans_extend) > 0:
            additions[extension_string] = trans_extend
    return additions

def transdeletion(word, depth):
    deletions = {}
    for extension in itertools.combinations_with_replacement('ABCDEFGHIJKLMNOPQRSTUVWXYZ',depth):
        extension_string = ''
        for letter in extension:
            extension_string = extension_string + letter
        word_list = list(word)
        valid = True
        for letter in extension:
            if letter in word_list:
                word_list.remove(letter)
            else:
                valid = False
        if valid:
            trans_delete = anagram(''.join(word_list),True)
            if len(trans_delete) > 0:
                deletions[extension_string] = trans_delete
    return deletions

def transreplacement(word):
    replacements = {}
    for letter in list(word):
        for replace in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
            if not replace == letter:
                temp_list = list(word)[:]
                temp_list.remove(letter)
                temp_list.append(replace)
                out = anagram(''.join(temp_list),True)
                if len(out) > 0:
                    replacements[replace] = out
    return replacements

