#!/usr/bin/env python3
import pickle
def loadall(filename):
    with open(filename, "rb") as f:
        while True:
            try:
                yield pickle.load(f)
            except EOFError:
                break


def dump_and_flush(f, s):
    sys.stdout.flush()
    pickle.dump(s, f)
    f.flush()

import sys
with open('%s._' % sys.argv[1], 'wb+') as f:
    for i in loadall(sys.argv[1]):
        dump_and_flush(f, i[0])
