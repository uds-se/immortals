#!/usr/bin/env python3
import random
import string
import json
import gramfuzz
import microjson


def delete_random_character(s):
    """Returns s with a random character deleted"""
    if s == "":
        return s

    pos = random.randint(0, len(s) - 1)
    # print("Deleting", repr(s[pos]), "at", pos)
    return s[:pos] + s[pos + 1:]


def insert_random_character(s):
    """Returns s with a random character inserted"""
    pos = random.randint(0, len(s))
    random_character = chr(random.randrange(0, 128))
    #random_character = random.choice(string.ascii_letters + string.punctuation)
    #random_character = random.choice(list(set(string.printable) - set(['\n', '\r', '\x0c'])))
    #if random_character == "'":
    #    random_character = "\'"
    # print("Inserting", repr(random_character), "at", pos)
    return s[:pos] + random_character + s[pos:]


def flip_random_character(s):
    """Returns s with a random bit flipped in a random position"""
    if s == "":
        return s

    pos = random.randint(0, len(s) - 1)
    c = s[pos]
    bit = 1 << random.randint(0, 6)
    new_c = chr(ord(c) ^ bit)
    # print("Flipping", bit, "in", repr(c) + ", giving", repr(new_c))
    return s[:pos] + new_c + s[pos + 1:]


def mutate(s):
    """Return s with a random mutation applied"""
    mutators = [
        delete_random_character,
        insert_random_character,
        #flip_random_character
    ]
    mutator = random.choice(mutators)
    # print(mutator)
    return mutator(s)

fuzzer = gramfuzz.GramFuzzer()

fuzzer.load_grammar('./bin/grammar.py')

strings  = {}
estrings  = {}

for i in fuzzer.gen(num=100000, cat='json', max_recursion=10):
    s = str(i)
    if s in strings: continue
    try:
        r = x.microjson.from_json(i)
        strings[s] = r

        for _ in range(128):
            i = mutate(i)
            s = str(i)
            if s in strings: continue
            try:
                r = x.microjson.from_json(i)
                # ignore
                #strings[s] = r
            except x.microjson.JSONError as e:
                estrings[s] = str(e)
            except Exception as e:
                estrings[s] = e

    except x.microjson.JSONError as e:
        estrings[s] = e
    except Exception as e:
        estrings[s] = e

import pickle
def to_lst(d):
    return [(k, d[k]) for k in d]

with open('fuzz.pickled', 'wb+') as f:
    pickle.dump([to_lst(strings),to_lst(estrings)], f)

