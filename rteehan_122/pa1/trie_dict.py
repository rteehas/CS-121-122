# CS122: Auto-completing keyboard using Tries
#
# usage: python trie_dict.py <dictionary filename>
# I collaborated with Jon Hori, Salman Arif, and Andrew Chuang
# Ryan Teehan

import os
import sys
from sys import exit
import tty
import termios
import fcntl
import string

import trie_shell

def create_trie_node():
    '''
    This creates a node for the trie

    Returns:
        node: dictionary
    '''
    node = {'count': 0, 'is_word': False}
    return node

def add_word(word, trie):
    '''
    Adds a word to the trie

    Inputs:
        word: string
        trie: dictionary

    Returns:
        nothing
    '''
    if len(word) == 1:
        if word in trie:
            trie[word]['is_word'] = True
            trie[word]['count'] += 1
        else:
            trie[word] = create_trie_node()
            trie[word]['is_word'] = True
            trie[word]['count'] += 1
    elif len(word) > 1:
        if word[0] in trie:
            trie[word[0]]['count'] += 1
            new_trie = trie[word[0]]
        else:
            trie[word[0]] = create_trie_node()
            trie[word[0]]['count'] += 1
            new_trie = trie[word[0]]
        new_word = word[1:]
        add_word(new_word, new_trie)

def is_word(word, trie):
    '''
    Determines whether a string is a word in the trie

    Inputs:
        word: string
        trie: dictionary

    Returns:
        boolean
    '''
    if len(word) == 1:
        if word in trie:
            return trie[word]['is_word']    
        if word not in trie:
            return False
    if len(word) > 1:
        if word[0] in trie:
            new_trie = trie[word[0]]
            new_word = word[1:]
            return is_word(new_word, new_trie)
        else:
            return False

def num_completions(word, trie):
    '''
    Determines how many ways a given string can be completed

    Inputs:
        word: string
        trie: dictionary

    Returns:
        int
    '''
    if len(word) == 1:
        if word in trie:
            return trie[word]['count']
        if word not in trie:
            return 0
    if len(word) > 1:
        if word[0] in trie:
            new_trie = trie[word[0]]
            new_word = word[1:]
            return num_completions(new_word, new_trie)
        if word[0] not in trie:
            return 0

def find_spot(word, trie):
    '''
    Moves to the place in a trie that corresponds to the word

    Inputs:
        word: string
        trie: dictionary

    Returns:
        dictionary
    '''
    if len(word) == 1:
        if word in trie:
            return trie[word]
        if word not in trie:
            return {}
    if len(word) > 1:
        if word[0] in trie:
            new_trie = trie[word[0]]
            new_word = word[1:]
            return find_spot(new_word, new_trie)
        else:
            return {}

def get_completions(word, trie):
    '''
    Gets the list of completions for a given prefix

    Inputs:
        word: string
        trie: dictionary

    Returns:
        completion_list: list of strings
    '''
    remaining_trie = find_spot(word, trie)
    # selects strings that are words and have no other completions
    if is_word(word, trie) == True and num_completions(word, trie) == 1:
        return ['']
    elif not remaining_trie and word != '':
        return []
    else:
        completion_list = []
        if is_word(word, trie):
            completion_list.append('')
        if word != '':
            for k in remaining_trie:
                x = get_completions(word + k, trie)
                for j in x:
                    y = k + j
                    completion_list.append(y)
        # separates the case of an empty string so that we can return
        # all the words in the trie
        if word == '':
            for k in trie:
                x = get_completions(word + k, trie)
                for j in x:
                    y = k + j
                    completion_list.append(y)
        return completion_list


if __name__ == "__main__":
    trie_shell.go("trie_dict")

