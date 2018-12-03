import pickle
import ast
def create_cls(strings, estrings):
    cls_str ="""
import timeout_decorator
# std
import sys
import unittest
import pickle

def loadall(filename):
    with open(filename, "rb") as f:
        while True:
            try:
                yield pickle.load(f)
            except EOFError:
                break

T_PARSE = []
E_PARSE = []
for [s, (n, r)] in loadall('%s'):
    if n == 'out':
        T_PARSE.append((s, r))
    elif n == 'err':
        E_PARSE.append((s, r))
    else:
        assert False

# vendor
import %s as json


class TestParse(unittest.TestCase):

    %s
    #---------ERRORS------------
    %s

def main():
    unittest.main()


if __name__ == "__main__":
    main()
    """

    method_str = """
    @timeout_decorator.timeout(1)
    def test_str_%d(self):
        # %s
        js, py = T_PARSE[%d]
        r = json.from_json(js)
        self.assertEqual(r, py)
    """

    emethod_str = """
    @timeout_decorator.timeout(1)
    def test_err_%d(self):
        # %s
        js, serr = E_PARSE[%d]
        with self.assertRaises(Exception) as ctx:
            json.from_json(js)
        err = str(ctx.exception)
        self.assertEqual(err, serr)
    """

    s = "\n".join([method_str % (i, repr(s), i) for i,s in enumerate(strings)])
    e = "\n".join([emethod_str % (i, repr(e), i) for i,e in enumerate(estrings)])
    cls = cls_str % (sys.argv[1], sys.argv[2], s, e)
    return cls

import sys


def loadall(filename):
    with open(filename, "rb") as f:
        while True:
            try:
                yield pickle.load(f)
            except EOFError:
                break

T_PARSE = []
E_PARSE = []
for [s, (n, r)] in loadall(sys.argv[1]):
    if n == 'out':
        T_PARSE.append((s,r))
    elif n == 'err':
        E_PARSE.append((s, r))
    else:
        assert False

print(create_cls(T_PARSE, E_PARSE))
