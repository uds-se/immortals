#!/usr/bin/env python3
import sys

if len(sys.argv) < 2:
    lines = [l.strip().split(',') for l in sys.stdin.readlines()]
else:
    lines = [l.strip().split(',') for l in open(sys.argv[1]).readlines()]

for line in lines:
    print("%s,%s" %(line[0], '1' if any(i == '1' for i in line) else '0'))
