#!/usr/bin/env python3
import sys

if len(sys.argv) < 2:
    lines = [l.strip().split(',') for l in sys.stdin.readlines()]
else:
    lines = [l.strip().split(',') for l in open(sys.argv[1]).readlines()]

for line in lines:
    mutant, *rest = line
    if all(i == '0' for i in rest): continue
    print(','.join(line))

