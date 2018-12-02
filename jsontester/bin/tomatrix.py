#!/usr/bin/env python3
import sys

all_tests = [i.strip() for i in open(sys.argv[1]).readlines()]
prematrix = sys.argv[2] #microjson.rfuzz.matrix

lines = open(prematrix).readlines()

for line in lines:
    mutant, *tests_ = line.split(' ')
    my_tests = set(tests_)
    print(mutant, ','.join([('1' if t in my_tests else '0') for t in all_tests]))

