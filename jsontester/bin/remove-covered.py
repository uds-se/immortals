#!/usr/bin/env python3
import sys
cover_mstatus = set()
for line in open(sys.argv[1]).readlines(): # coverage only
    tokens = line.strip().split(',')
    t = tokens[3].strip()
    if t.startswith('killed') or t.startswith('incompetent') or t.startswith('timeout'):
        cover_mstatus.add(tokens[0].strip())

for line in open(sys.argv[2]).readlines(): # incompetent
    tokens = line.strip().split(',')
    t = tokens[3].strip()
    if t.startswith('incompetent'):
        cover_mstatus.add(tokens[0].strip())

for line in open(sys.argv[3]).readlines():
    tokens = line.strip().split(',')
    if tokens[0] in cover_mstatus: continue # covering mutants
    if all(w == '0' for w in tokens[1:]): continue # not detected
    print(line.strip())
