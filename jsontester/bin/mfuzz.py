#!/usr/bin/env python3
import random
random.seed(0)
import string
import json
import gramfuzz
import sys
#import x.microjson
from importlib import import_module

import sys, os, importlib

mfile = sys.argv[1]

sys.path.append(os.path.dirname(mfile))
mfile = os.path.splitext(os.path.basename(mfile))[0]
mymodule = importlib.import_module(mfile)
sys.path.pop()



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
        flip_random_character
    ]
    mutator = random.choice(mutators)
    # print(mutator)
    return mutator(s)

fuzzer = gramfuzz.GramFuzzer()

fuzzer.load_grammar('./bin/jsongrammar.py')

strings  = {}
estrings  = {}
import sys

def dump_and_flush(f, s):
    sys.stdout.flush()
    pickle.dump(s, f)
    f.flush()

import pickle
#import coverage
with open('%s.mfuzz.pickled' % mfile, 'wb+') as f:
    #cov = coverage.Coverage()
    for i in fuzzer.gen(num=1000, cat='json', max_recursion=10):
        #cov.start()
        s = str(i)
        #print(repr(s))
        sys.stdout.flush()
        r = None
        if s in strings: continue
        try:
            r = mymodule.from_json(i)
            strings[s] = r

            for _ in range(10):
                i = mutate(i)
                s = str(i)
                if s in strings: continue
                try:
                    r = mymodule.from_json(i)
                    dump_and_flush(f, [s, ('out', r)])
                    # ignore
                    #strings[s] = r
                except Exception as e:
                    r = str(e)
                    dump_and_flush(f, [s, ('err', r)])
                    estrings[s] = e

        except Exception as e:
            r = str(e)
            dump_and_flush(f, [s, ('err', r)])
            estrings[s] = e
        #cov.stop()
        #covf = cov.get_data().measured_files()[0]
        #fn, executed, notrun, missing = cov.analysis(covf)
        #print(missing)
        #sys.stdout.flush()

