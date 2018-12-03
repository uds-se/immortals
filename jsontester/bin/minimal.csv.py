#!/usr/bin/env python3
import sys

lines = [l.strip().split(',') for l in sys.stdin.readlines()]

# remove head

xlines = list(zip(*lines))
head = xlines[0]
unique = list(set(xlines[1:]))
csv = list(zip(*([head] + unique)))

for c in csv:
    print(','.join(c))
