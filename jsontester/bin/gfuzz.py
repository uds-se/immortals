#!/usr/bin/env python3
# This is a grammar fuzzer

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
with open('%s.gfuzz.pickled' % mfile, 'wb+') as f:
    #cov = coverage.Coverage()
    for i in fuzzer.gen(num=10000, cat='json', max_recursion=10):
        #cov.start()
        s = str(i)
        sys.stdout.flush()
        r = None
        if s in strings: continue
        try:
            r = mymodule.from_json(i)
            dump_and_flush(f, [s, ('out', r)])
            strings[s] = r

        except Exception as e:
            r = str(e)
            dump_and_flush(f, [s, ('err', r)])
            estrings[s] = e
        #cov.stop()
        #covf = cov.get_data().measured_files()[0]
        #fn, executed, notrun, missing = cov.analysis(covf)
        #print(missing)
        #sys.stdout.flush()

