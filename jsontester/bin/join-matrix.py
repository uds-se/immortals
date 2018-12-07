#!/usr/bin/env python3
import sys

my_file = []
names_len = None
names = None
for fn in sys.argv[1:]:
    lines = [l.strip().split(',') for l in open(fn).readlines()]
    transposed = list(zip(*lines))
    names = transposed[0]
    if names_len:
        assert len(names) == names_len
    names_len = len(names)
    values = transposed[1:]
    my_file.extend(values)

new_file = list(zip(*my_file))
for i, line in enumerate(new_file):
    print("%s,%s" % (names[i], ",".join(line)))
