#!/usr/bin/env python3
# This is a grammar fuzzer

import random
import string
random.seed(0)
import fuzzingbook.GrammarFuzzer as GF
import fuzzingbook.GrammarCoverageFuzzer as GCF
import fuzzingbook.Grammars as G
J_G = {
        '<start>': ['<json>'],
        '<json>': ['<element>'],
        '<element>': ['<ws><value><ws>'],
        '<value>': ['<object>', '<array>', '<string>', '<number>', 'true', 'false', 'null'],
        '<object>': ['{<ws>}', '{<members>}'],
        '<members>': ['<member><symbol-2>'],
        '<member>': ['<ws><string><ws>:<element>'],
        '<array>': ['[<ws>]', '[<elements>]'],
        '<elements>': ['<element><symbol-1-1>'],
        '<string>': ['"<characters>"'],
        '<characters>': ['<character-1>'],
        '<character>': ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
            'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
            'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
            'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
            'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
            '!', '#', '$', '%', '&', "'", '(', ')', '*', '+', ',', '-', '.',
            '/', ':', ';', '<', '=', '>', '?', '@', '[', ']', '^', '_', '`',
            '{', '|', '}', '~', ' ', '\\"', '\\\\', '\\/', '<unicode>', '<escaped>'],
        '<number>': ['<int><frac><exp>'],
        '<int>': ['<digit>', '<onenine><digits>', '-<digits>', '-<onenine><digits>'],
        '<digits>': ['<digit-1>'],
        '<digit>': ['0', '<onenine>'],
        '<onenine>': ['1', '2', '3', '4', '5', '6', '7', '8', '9'],
        '<frac>': ['', '.<digits>'],
        '<exp>': ['', 'E<sign><digits>', 'e<sign><digits>'],
        '<sign>': ['', '+', '-'],
        '<ws>': ['<sp1><ws>', ''],
        '<sp1>': ['\n', '\r', '\t', '\b', '\f'],
        '<symbol>': [',<members>'],
        '<symbol-1>': [',<elements>'],
        '<symbol-2>': ['', '<symbol><symbol-2>'],
        '<symbol-1-1>': ['', '<symbol-1><symbol-1-1>'],
        '<character-1>': ['', '<character><character-1>'],
        '<digit-1>': ['<digit>', '<digit><digit-1>'],
        '<unicode>': [chr(i) for i in range(0x1F, 0x10000) if chr(i) not in string.printable],
        '<escaped>': ['\\u<hex><hex><hex><hex>'],
        '<hex>': [str(i) for i in range(10)] + list('abcdefABCDEF')
        }


import string
import json
import sys
sys.setrecursionlimit(1500)
#import resource
# Will segfault without this line.
#resource.setrlimit(resource.RLIMIT_STACK, [0x10000000, resource.RLIM_INFINITY])
#sys.setrecursionlimit(0x100000)

from importlib import import_module

import sys, os, importlib

mfile = sys.argv[1]

sys.path.append(os.path.dirname(mfile))
mfile = os.path.splitext(os.path.basename(mfile))[0]
mymodule = importlib.import_module(mfile)
sys.path.pop()

json_fuzzer = GF.GrammarFuzzer(J_G, start_symbol='<start>')

strings  = {}
estrings  = {}
import sys

def dump_and_flush(f, s):
    sys.stdout.flush()
    pickle.dump(s, f)
    f.flush()

import pickle
Max = int(os.environ.get('GFUZZ_MAX', '1000')) # takes 18 minutes for 10000
print("Max: ", Max)
import time
start_time = time.monotonic()
percentage_points = {i*100 for i in range(1,Max//100)}
with open('%s.gfuzz.pickled' % mfile, 'wb+') as f:
    for i in range(Max):
        if i in percentage_points:
            print(i/Max, time.monotonic() - start_time, file=sys.stderr)
        sys.stdout.flush()
        s = json_fuzzer.fuzz() 
        sys.stdout.flush()
        r = None
        if s in strings: continue
        try:
            r = mymodule.from_json(s)
            dump_and_flush(f, [s, ('out', r)])
            strings[s] = r

        except Exception as e:
            r = str(e)
            dump_and_flush(f, [s, ('err', r)])
            estrings[s] = e
