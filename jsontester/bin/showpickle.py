#!/usr/bin/env python3
import pickle
def loadall(filename):
    with open(filename, "rb") as f:
        while True:
            try:
                yield pickle.load(f)
            except EOFError:
                break

import sys
for i in loadall(sys.argv[1]):
    print(repr(i))
