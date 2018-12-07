#!/usr/bin/env python3
import sys
cover_mstatus = set()
for line in open(sys.argv[1]).readlines():
    tokens = line.strip().split(',')
    if tokens[3].strip().startswith('killed'):
        cover_mstatus.add(tokens[0].strip())

for line in open(sys.argv[2]).readlines():
    tokens = line.strip().split(',')
    if tokens[0] in cover_mstatus: continue
    print(line.strip())
