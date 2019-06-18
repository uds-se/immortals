#!/usr/bin/env python
import sys
with open(sys.argv[1]) as f:
    my_file = f.read()

mutants = []
for line in my_file.split("\n"):
    if not line.strip():
        continue
    name, *tests = line.strip().split(',')
    v = [int(t) for t in tests]
    mutants.append(v)
    #print("m%s" % name, sum(v))

tests = list(map(tuple, zip(*mutants)))
unique_tests = set(tests)

hm = {}
for i,t in enumerate(tests):
    if t in unique_tests:
        if t not in hm: hm[t] = []
        hm[t].append(i)

test_alias = {}
for k in hm:
    tmin = min(hm[k])
    for t in hm[k]:
        test_alias[t] = tmin

#for t in sorted(test_alias):
#    print(t, test_alias[t])
original_tests = {t for t in test_alias if t == test_alias[t]}

for m,tests in enumerate(mutants):
    print("m%d" % (m+1), sum([k for t,k in enumerate(tests) if t in original_tests]))
