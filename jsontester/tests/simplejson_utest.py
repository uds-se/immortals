from unittest import TestCase
from simplejson import text_type, binary_type, b, PY3, BytesIO, unichr, StringIO, PosInf, NegInf, long_type, NaN, reload_module
import simplejson as json

class TestBigintAsString(TestCase):
    # Python 2.5, at least the one that ships on Mac OS X, calculates
    # 2 ** 53 as 0! It manages to calculate 1 << 53 correctly.
    values = [(200, 200),
              ((1 << 53) - 1, 9007199254740991),
              ((1 << 53), '9007199254740992'),
              ((1 << 53) + 1, '9007199254740993'),
              (-100, -100),
              ((-1 << 53), '-9007199254740992'),
              ((-1 << 53) - 1, '-9007199254740993'),
              ((-1 << 53) + 1, -9007199254740991)]

    options = (
        {"bigint_as_string": True},
        {"int_as_string_bitcount": 53}
    )

    def test_ints(self):
        for opts in self.options:
            for val, expect in self.values:
                self.assertEqual(
                    val,
                    json.loads(json.dumps(val)))
                self.assertEqual(
                    expect,
                    json.loads(json.dumps(val, **opts)))

    def test_lists(self):
        for opts in self.options:
            for val, expect in self.values:
                val = [val, val]
                expect = [expect, expect]
                self.assertEqual(
                    val,
                    json.loads(json.dumps(val)))
                self.assertEqual(
                    expect,
                    json.loads(json.dumps(val, **opts)))

    def test_dicts(self):
        for opts in self.options:
            for val, expect in self.values:
                val = {'k': val}
                expect = {'k': expect}
                self.assertEqual(
                    val,
                    json.loads(json.dumps(val)))
                self.assertEqual(
                    expect,
                    json.loads(json.dumps(val, **opts)))

    def test_dict_keys(self):
        for opts in self.options:
            for val, _ in self.values:
                expect = {str(val): 'value'}
                val = {val: 'value'}
                self.assertEqual(
                    expect,
                    json.loads(json.dumps(val)))
                self.assertEqual(
                    expect,
                    json.loads(json.dumps(val, **opts)))
#from unittest import TestCase

import simplejson as json


class TestBitSizeIntAsString(TestCase):
    # Python 2.5, at least the one that ships on Mac OS X, calculates
    # 2 ** 31 as 0! It manages to calculate 1 << 31 correctly.
    values = [
        (200, 200),
        ((1 << 31) - 1, (1 << 31) - 1),
        ((1 << 31), str(1 << 31)),
        ((1 << 31) + 1, str((1 << 31) + 1)),
        (-100, -100),
        ((-1 << 31), str(-1 << 31)),
        ((-1 << 31) - 1, str((-1 << 31) - 1)),
        ((-1 << 31) + 1, (-1 << 31) + 1),
    ]

    def test_invalid_counts(self):
        for n in ['foo', -1, 0, 1.0]:
            self.assertRaises(
                TypeError,
                json.dumps, 0, int_as_string_bitcount=n)

    def test_ints_outside_range_fails(self):
        self.assertNotEqual(
            str(1 << 15),
            json.loads(json.dumps(1 << 15, int_as_string_bitcount=16)),
            )

    def test_ints(self):
        for val, expect in self.values:
            self.assertEqual(
                val,
                json.loads(json.dumps(val)))
            self.assertEqual(
                expect,
                json.loads(json.dumps(val, int_as_string_bitcount=31)),
                )

    def test_lists(self):
        for val, expect in self.values:
            val = [val, val]
            expect = [expect, expect]
            self.assertEqual(
                val,
                json.loads(json.dumps(val)))
            self.assertEqual(
                expect,
                json.loads(json.dumps(val, int_as_string_bitcount=31)))

    def test_dicts(self):
        for val, expect in self.values:
            val = {'k': val}
            expect = {'k': expect}
            self.assertEqual(
                val,
                json.loads(json.dumps(val)))
            self.assertEqual(
                expect,
                json.loads(json.dumps(val, int_as_string_bitcount=31)))

    def test_dict_keys(self):
        for val, _ in self.values:
            expect = {str(val): 'value'}
            val = {val: 'value'}
            self.assertEqual(
                expect,
                json.loads(json.dumps(val)))
            self.assertEqual(
                expect,
                json.loads(json.dumps(val, int_as_string_bitcount=31)))
#from unittest import TestCase
import simplejson as json

def default_iterable(obj):
    return list(obj)

class TestCheckCircular(TestCase):
    def test_circular_dict(self):
        dct = {}
        dct['a'] = dct
        self.assertRaises(ValueError, json.dumps, dct)

    def test_circular_list(self):
        lst = []
        lst.append(lst)
        self.assertRaises(ValueError, json.dumps, lst)

    def test_circular_composite(self):
        dct2 = {}
        dct2['a'] = []
        dct2['a'].append(dct2)
        self.assertRaises(ValueError, json.dumps, dct2)

    def test_circular_default(self):
        json.dumps([set()], default=default_iterable)
        self.assertRaises(TypeError, json.dumps, [set()])

    def test_circular_off_default(self):
        json.dumps([set()], default=default_iterable, check_circular=False)
        self.assertRaises(TypeError, json.dumps, [set()], check_circular=False)
import decimal
from decimal import Decimal
from unittest import TestCase
#from simplejson.compat import StringIO, reload_module

import simplejson as json

class TestDecimal(TestCase):
    NUMS = "1.0", "10.00", "1.1", "1234567890.1234567890", "500"
    def dumps(self, obj, **kw):
        sio = StringIO()
        json.dump(obj, sio, **kw)
        res = json.dumps(obj, **kw)
        self.assertEqual(res, sio.getvalue())
        return res

    def loads(self, s, **kw):
        sio = StringIO(s)
        res = json.loads(s, **kw)
        self.assertEqual(res, json.load(sio, **kw))
        return res

    def test_decimal_encode(self):
        for d in map(Decimal, self.NUMS):
            self.assertEqual(self.dumps(d, use_decimal=True), str(d))

    def test_decimal_decode(self):
        for s in self.NUMS:
            self.assertEqual(self.loads(s, parse_float=Decimal), Decimal(s))

    def test_stringify_key(self):
        for d in map(Decimal, self.NUMS):
            v = {d: d}
            self.assertEqual(
                self.loads(
                    self.dumps(v, use_decimal=True), parse_float=Decimal),
                {str(d): d})

    def test_decimal_roundtrip(self):
        for d in map(Decimal, self.NUMS):
            # The type might not be the same (int and Decimal) but they
            # should still compare equal.
            for v in [d, [d], {'': d}]:
                self.assertEqual(
                    self.loads(
                        self.dumps(v, use_decimal=True), parse_float=Decimal),
                    v)

    def test_decimal_defaults(self):
        d = Decimal('1.1')
        # use_decimal=True is the default
        self.assertRaises(TypeError, json.dumps, d, use_decimal=False)
        self.assertEqual('1.1', json.dumps(d))
        self.assertEqual('1.1', json.dumps(d, use_decimal=True))
        self.assertRaises(TypeError, json.dump, d, StringIO(),
                          use_decimal=False)
        sio = StringIO()
        json.dump(d, sio)
        self.assertEqual('1.1', sio.getvalue())
        sio = StringIO()
        json.dump(d, sio, use_decimal=True)
        self.assertEqual('1.1', sio.getvalue())

    def test_decimal_reload(self):
        # Simulate a subinterpreter that reloads the Python modules but not
        # the C code https://github.com/simplejson/simplejson/issues/34
        global Decimal
        Decimal = json.reload_module(decimal).Decimal
        #import simplejson.encoder
        json.Decimal = Decimal
        self.test_decimal_roundtrip()
import decimal
#from unittest import TestCase

#from simplejson.compat import StringIO, b, binary_type
#from simplejson import OrderedDict

class MisbehavingBytesSubtype(json.binary_type):
    def decode(self, encoding=None):
        return "bad decode"
    def __str__(self):
        return "bad __str__"
    def __bytes__(self):
        return b("bad __bytes__")

class TestDecode(TestCase):
    if not hasattr(TestCase, 'assertIs'):
        def assertIs(self, a, b):
            self.assertTrue(a is b, '%r is %r' % (a, b))

    def test_decimal(self):
        rval = json.loads('1.1', parse_float=decimal.Decimal)
        self.assertTrue(isinstance(rval, decimal.Decimal))
        self.assertEqual(rval, decimal.Decimal('1.1'))

    def test_float(self):
        rval = json.loads('1', parse_int=float)
        self.assertTrue(isinstance(rval, float))
        self.assertEqual(rval, 1.0)

    def test_decoder_optimizations(self):
        # Several optimizations were made that skip over calls to
        # the whitespace regex, so this test is designed to try and
        # exercise the uncommon cases. The array cases are already covered.
        rval = json.loads('{   "key"    :    "value"    ,  "k":"v"    }')
        self.assertEqual(rval, {"key":"value", "k":"v"})

    def test_empty_objects(self):
        s = '{}'
        self.assertEqual(json.loads(s), eval(s))
        s = '[]'
        self.assertEqual(json.loads(s), eval(s))
        s = '""'
        self.assertEqual(json.loads(s), eval(s))

    def test_object_pairs_hook(self):
        s = '{"xkd":1, "kcw":2, "art":3, "hxm":4, "qrt":5, "pad":6, "hoy":7}'
        p = [("xkd", 1), ("kcw", 2), ("art", 3), ("hxm", 4),
             ("qrt", 5), ("pad", 6), ("hoy", 7)]
        self.assertEqual(json.loads(s), eval(s))
        self.assertEqual(json.loads(s, object_pairs_hook=lambda x: x), p)
        self.assertEqual(json.load(StringIO(s),
                                   object_pairs_hook=lambda x: x), p)
        od = json.loads(s, object_pairs_hook=OrderedDict)
        self.assertEqual(od, OrderedDict(p))
        self.assertEqual(type(od), OrderedDict)
        # the object_pairs_hook takes priority over the object_hook
        self.assertEqual(json.loads(s,
                                    object_pairs_hook=OrderedDict,
                                    object_hook=lambda x: None),
                         OrderedDict(p))

    def check_keys_reuse(self, source, loads):
        rval = loads(source)
        (a, b), (c, d) = sorted(rval[0]), sorted(rval[1])
        self.assertIs(a, c)
        self.assertIs(b, d)

    def test_keys_reuse_str(self):
        s = u'[{"a_key": 1, "b_\xe9": 2}, {"a_key": 3, "b_\xe9": 4}]'.encode('utf8')
        self.check_keys_reuse(s, json.loads)

    def test_keys_reuse_unicode(self):
        s = u'[{"a_key": 1, "b_\xe9": 2}, {"a_key": 3, "b_\xe9": 4}]'
        self.check_keys_reuse(s, json.loads)

    def test_empty_strings(self):
        self.assertEqual(json.loads('""'), "")
        self.assertEqual(json.loads(u'""'), u"")
        self.assertEqual(json.loads('[""]'), [""])
        self.assertEqual(json.loads(u'[""]'), [u""])

    def test_raw_decode(self):
        cls = json.JSONDecoder
        self.assertEqual(
            ({'a': {}}, 9),
            cls().raw_decode("{\"a\": {}}"))
        # http://code.google.com/p/simplejson/issues/detail?id=85
        self.assertEqual(
            ({'a': {}}, 9),
            cls(object_pairs_hook=dict).raw_decode("{\"a\": {}}"))
        # https://github.com/simplejson/simplejson/pull/38
        self.assertEqual(
            ({'a': {}}, 11),
            cls().raw_decode(" \n{\"a\": {}}"))

    def test_bytes_decode(self):
        cls = json.JSONDecoder
        data = b('"\xe2\x82\xac"')
        self.assertEqual(cls().decode(data), u'\u20ac')
        self.assertEqual(cls(encoding='latin1').decode(data), u'\xe2\x82\xac')
        self.assertEqual(cls(encoding=None).decode(data), u'\u20ac')

        data = MisbehavingBytesSubtype(b('"\xe2\x82\xac"'))
        self.assertEqual(cls().decode(data), u'\u20ac')
        self.assertEqual(cls(encoding='latin1').decode(data), u'\xe2\x82\xac')
        self.assertEqual(cls(encoding=None).decode(data), u'\u20ac')

    def test_bounds_checking(self):
        # https://github.com/simplejson/simplejson/issues/98
        j = json.JSONDecoder()
        for i in [4, 5, 6, -1, -2, -3, -4, -5, -6]:
            self.assertRaises(ValueError, j.scan_once, '1234', i)
            self.assertRaises(ValueError, j.raw_decode, '1234', i)
        x, y = sorted(['128931233', '472389423'], key=id)
        diff = id(x) - id(y)
        self.assertRaises(ValueError, j.scan_once, y, diff)
        self.assertRaises(ValueError, j.raw_decode, y, i)
#from unittest import TestCase

import simplejson as json

class TestDefault(TestCase):
    def test_default(self):
        self.assertEqual(
            json.dumps(type, default=repr),
            json.dumps(repr(type)))
#from unittest import TestCase
#from simplejson.compat import StringIO, long_type, b, binary_type, text_type, PY3
import simplejson as json

class MisbehavingTextSubtype(text_type):
    def __str__(self):
        return "FAIL!"

class MisbehavingBytesSubtype(binary_type):
    def decode(self, encoding=None):
        return "bad decode"
    def __str__(self):
        return "bad __str__"
    def __bytes__(self):
        return b("bad __bytes__")

def as_text_type(s):
    if PY3 and isinstance(s, bytes):
        return s.decode('ascii')
    return s

def decode_iso_8859_15(b):
    return b.decode('iso-8859-15')

class TestDump(TestCase):
    def test_dump(self):
        sio = StringIO()
        json.dump({}, sio)
        self.assertEqual(sio.getvalue(), '{}')

    def test_constants(self):
        for c in [None, True, False]:
            self.assertTrue(json.loads(json.dumps(c)) is c)
            self.assertTrue(json.loads(json.dumps([c]))[0] is c)
            self.assertTrue(json.loads(json.dumps({'a': c}))['a'] is c)

    def test_stringify_key(self):
        items = [(b('bytes'), 'bytes'),
                 (1.0, '1.0'),
                 (10, '10'),
                 (True, 'true'),
                 (False, 'false'),
                 (None, 'null'),
                 (long_type(100), '100')]
        for k, expect in items:
            self.assertEqual(
                json.loads(json.dumps({k: expect})),
                {expect: expect})
            self.assertEqual(
                json.loads(json.dumps({k: expect}, sort_keys=True)),
                {expect: expect})
        self.assertRaises(TypeError, json.dumps, {json: 1})
        for v in [{}, {'other': 1}, {b('derp'): 1, 'herp': 2}]:
            for sort_keys in [False, True]:
                v0 = dict(v)
                v0[json] = 1
                v1 = dict((as_text_type(key), val) for (key, val) in v.items())
                self.assertEqual(
                    json.loads(json.dumps(v0, skipkeys=True, sort_keys=sort_keys)),
                    v1)
                self.assertEqual(
                    json.loads(json.dumps({'': v0}, skipkeys=True, sort_keys=sort_keys)),
                    {'': v1})
                self.assertEqual(
                    json.loads(json.dumps([v0], skipkeys=True, sort_keys=sort_keys)),
                    [v1])

    def test_dumps(self):
        self.assertEqual(json.dumps({}), '{}')

    def test_encode_truefalse(self):
        self.assertEqual(json.dumps(
                 {True: False, False: True}, sort_keys=True),
                 '{"false": true, "true": false}')
        self.assertEqual(
            json.dumps(
                {2: 3.0,
                 4.0: long_type(5),
                 False: 1,
                 long_type(6): True,
                 "7": 0},
                sort_keys=True),
            '{"2": 3.0, "4.0": 5, "6": true, "7": 0, "false": 1}')

    def test_ordered_dict(self):
        # http://bugs.python.org/issue6105
        items = [('one', 1), ('two', 2), ('three', 3), ('four', 4), ('five', 5)]
        s = json.dumps(json.OrderedDict(items))
        self.assertEqual(
            s,
            '{"one": 1, "two": 2, "three": 3, "four": 4, "five": 5}')

    def test_indent_unknown_type_acceptance(self):
        """
        A test against the regression mentioned at `github issue 29`_.

        The indent parameter should accept any type which pretends to be
        an instance of int or long when it comes to being multiplied by
        strings, even if it is not actually an int or long, for
        backwards compatibility.

        .. _github issue 29:
           http://github.com/simplejson/simplejson/issue/29
        """

        class AwesomeInt(object):
            """An awesome reimplementation of integers"""

            def __init__(self, *args, **kwargs):
                if len(args) > 0:
                    # [construct from literals, objects, etc.]
                    # ...

                    # Finally, if args[0] is an integer, store it
                    if isinstance(args[0], int):
                        self._int = args[0]

            # [various methods]

            def __mul__(self, other):
                # [various ways to multiply AwesomeInt objects]
                # ... finally, if the right-hand operand is not awesome enough,
                # try to do a normal integer multiplication
                if hasattr(self, '_int'):
                    return self._int * other
                else:
                    raise NotImplementedError("To do non-awesome things with"
                        " this object, please construct it from an integer!")

        s = json.dumps([0, 1, 2], indent=AwesomeInt(3))
        self.assertEqual(s, '[\n   0,\n   1,\n   2\n]')

    def test_accumulator(self):
        # the C API uses an accumulator that collects after 100,000 appends
        lst = [0] * 100000
        self.assertEqual(json.loads(json.dumps(lst)), lst)

    def test_sort_keys(self):
        # https://github.com/simplejson/simplejson/issues/106
        for num_keys in range(2, 32):
            p = dict((str(x), x) for x in range(num_keys))
            sio = StringIO()
            json.dump(p, sio, sort_keys=True)
            self.assertEqual(sio.getvalue(), json.dumps(p, sort_keys=True))
            self.assertEqual(json.loads(sio.getvalue()), p)

    def test_misbehaving_text_subtype(self):
        # https://github.com/simplejson/simplejson/issues/185
        text = "this is some text"
        self.assertEqual(
            json.dumps(MisbehavingTextSubtype(text)),
            json.dumps(text)
        )
        self.assertEqual(
            json.dumps([MisbehavingTextSubtype(text)]),
            json.dumps([text])
        )
        self.assertEqual(
            json.dumps({MisbehavingTextSubtype(text): 42}),
            json.dumps({text: 42})
        )

    def test_misbehaving_bytes_subtype(self):
        data = b("this is some data \xe2\x82\xac")
        self.assertEqual(
            json.dumps(MisbehavingBytesSubtype(data)),
            json.dumps(data)
        )
        self.assertEqual(
            json.dumps([MisbehavingBytesSubtype(data)]),
            json.dumps([data])
        )
        self.assertEqual(
            json.dumps({MisbehavingBytesSubtype(data): 42}),
            json.dumps({data: 42})
        )

    def test_bytes_toplevel(self):
        self.assertEqual(json.dumps(b('\xe2\x82\xac')), r'"\u20ac"')
        self.assertRaises(UnicodeDecodeError, json.dumps, b('\xa4'))
        self.assertEqual(json.dumps(b('\xa4'), encoding='iso-8859-1'),
                         r'"\u00a4"')
        self.assertEqual(json.dumps(b('\xa4'), encoding='iso-8859-15'),
                         r'"\u20ac"')
        if PY3:
            self.assertRaises(TypeError, json.dumps, b('\xe2\x82\xac'),
                              encoding=None)
            self.assertRaises(TypeError, json.dumps, b('\xa4'),
                              encoding=None)
            self.assertEqual(json.dumps(b('\xa4'), encoding=None,
                                        default=decode_iso_8859_15),
                            r'"\u20ac"')
        else:
            self.assertEqual(json.dumps(b('\xe2\x82\xac'), encoding=None),
                             r'"\u20ac"')
            self.assertRaises(UnicodeDecodeError, json.dumps, b('\xa4'),
                              encoding=None)
            self.assertRaises(UnicodeDecodeError, json.dumps, b('\xa4'),
                              encoding=None, default=decode_iso_8859_15)

    def test_bytes_nested(self):
        self.assertEqual(json.dumps([b('\xe2\x82\xac')]), r'["\u20ac"]')
        self.assertRaises(UnicodeDecodeError, json.dumps, [b('\xa4')])
        self.assertEqual(json.dumps([b('\xa4')], encoding='iso-8859-1'),
                         r'["\u00a4"]')
        self.assertEqual(json.dumps([b('\xa4')], encoding='iso-8859-15'),
                         r'["\u20ac"]')
        if PY3:
            self.assertRaises(TypeError, json.dumps, [b('\xe2\x82\xac')],
                              encoding=None)
            self.assertRaises(TypeError, json.dumps, [b('\xa4')],
                              encoding=None)
            self.assertEqual(json.dumps([b('\xa4')], encoding=None,
                                        default=decode_iso_8859_15),
                             r'["\u20ac"]')
        else:
            self.assertEqual(json.dumps([b('\xe2\x82\xac')], encoding=None),
                             r'["\u20ac"]')
            self.assertRaises(UnicodeDecodeError, json.dumps, [b('\xa4')],
                              encoding=None)
            self.assertRaises(UnicodeDecodeError, json.dumps, [b('\xa4')],
                              encoding=None, default=decode_iso_8859_15)

    def test_bytes_key(self):
        self.assertEqual(json.dumps({b('\xe2\x82\xac'): 42}), r'{"\u20ac": 42}')
        self.assertRaises(UnicodeDecodeError, json.dumps, {b('\xa4'): 42})
        self.assertEqual(json.dumps({b('\xa4'): 42}, encoding='iso-8859-1'),
                         r'{"\u00a4": 42}')
        self.assertEqual(json.dumps({b('\xa4'): 42}, encoding='iso-8859-15'),
                         r'{"\u20ac": 42}')
        if PY3:
            self.assertRaises(TypeError, json.dumps, {b('\xe2\x82\xac'): 42},
                              encoding=None)
            self.assertRaises(TypeError, json.dumps, {b('\xa4'): 42},
                              encoding=None)
            self.assertRaises(TypeError, json.dumps, {b('\xa4'): 42},
                              encoding=None, default=decode_iso_8859_15)
            self.assertEqual(json.dumps({b('\xa4'): 42}, encoding=None,
                                        skipkeys=True),
                             r'{}')
        else:
            self.assertEqual(json.dumps({b('\xe2\x82\xac'): 42}, encoding=None),
                             r'{"\u20ac": 42}')
            self.assertRaises(UnicodeDecodeError, json.dumps, {b('\xa4'): 42},
                              encoding=None)
            self.assertRaises(UnicodeDecodeError, json.dumps, {b('\xa4'): 42},
                              encoding=None, default=decode_iso_8859_15)
            self.assertRaises(UnicodeDecodeError, json.dumps, {b('\xa4'): 42},
                              encoding=None, skipkeys=True)
#from unittest import TestCase

#import simplejson.encoder
#from simplejson.compat import b

CASES = [
    (u'/\\"\ucafe\ubabe\uab98\ufcde\ubcda\uef4a\x08\x0c\n\r\t`1~!@#$%^&*()_+-=[]{}|;:\',./<>?', '"/\\\\\\"\\ucafe\\ubabe\\uab98\\ufcde\\ubcda\\uef4a\\b\\f\\n\\r\\t`1~!@#$%^&*()_+-=[]{}|;:\',./<>?"'),
    (u'\u0123\u4567\u89ab\ucdef\uabcd\uef4a', '"\\u0123\\u4567\\u89ab\\ucdef\\uabcd\\uef4a"'),
    (u'controls', '"controls"'),
    (u'\x08\x0c\n\r\t', '"\\b\\f\\n\\r\\t"'),
    (u'{"object with 1 member":["array with 1 element"]}', '"{\\"object with 1 member\\":[\\"array with 1 element\\"]}"'),
    (u' s p a c e d ', '" s p a c e d "'),
    (u'\U0001d120', '"\\ud834\\udd20"'),
    (u'\u03b1\u03a9', '"\\u03b1\\u03a9"'),
    (b('\xce\xb1\xce\xa9'), '"\\u03b1\\u03a9"'),
    (u'\u03b1\u03a9', '"\\u03b1\\u03a9"'),
    (b('\xce\xb1\xce\xa9'), '"\\u03b1\\u03a9"'),
    (u'\u03b1\u03a9', '"\\u03b1\\u03a9"'),
    (u'\u03b1\u03a9', '"\\u03b1\\u03a9"'),
    (u"`1~!@#$%^&*()_+-={':[,]}|;.</>?", '"`1~!@#$%^&*()_+-={\':[,]}|;.</>?"'),
    (u'\x08\x0c\n\r\t', '"\\b\\f\\n\\r\\t"'),
    (u'\u0123\u4567\u89ab\ucdef\uabcd\uef4a', '"\\u0123\\u4567\\u89ab\\ucdef\\uabcd\\uef4a"'),
]

class TestEncodeBaseStringAscii(TestCase):
    def test_py_encode_basestring_ascii(self):
        self._test_encode_basestring_ascii(json.py_encode_basestring_ascii)

    def _test_encode_basestring_ascii(self, encode_basestring_ascii):
        fname = encode_basestring_ascii.__name__
        for input_string, expect in CASES:
            result = encode_basestring_ascii(input_string)
            #self.assertEqual(result, expect,
            #    '{0!r} != {1!r} for {2}({3!r})'.format(
            #        result, expect, fname, input_string))
            self.assertEqual(result, expect,
                '%r != %r for %s(%r)' % (result, expect, fname, input_string))

    def test_sorted_dict(self):
        items = [('one', 1), ('two', 2), ('three', 3), ('four', 4), ('five', 5)]
        s = json.dumps(dict(items), sort_keys=True)
        self.assertEqual(s, '{"five": 5, "four": 4, "one": 1, "three": 3, "two": 2}')
import unittest

#import simplejson as json

class TestEncodeForHTML(unittest.TestCase):

    def setUp(self):
        self.decoder = json.JSONDecoder()
        self.encoder = json.JSONEncoderForHTML()
        self.non_ascii_encoder = json.JSONEncoderForHTML(ensure_ascii=False)

    def test_basic_encode(self):
        self.assertEqual(r'"\u0026"', self.encoder.encode('&'))
        self.assertEqual(r'"\u003c"', self.encoder.encode('<'))
        self.assertEqual(r'"\u003e"', self.encoder.encode('>'))
        self.assertEqual(r'"\u2028"', self.encoder.encode(u'\u2028'))

    def test_non_ascii_basic_encode(self):
        self.assertEqual(r'"\u0026"', self.non_ascii_encoder.encode('&'))
        self.assertEqual(r'"\u003c"', self.non_ascii_encoder.encode('<'))
        self.assertEqual(r'"\u003e"', self.non_ascii_encoder.encode('>'))
        self.assertEqual(r'"\u2028"', self.non_ascii_encoder.encode(u'\u2028'))

    def test_basic_roundtrip(self):
        for char in '&<>':
            self.assertEqual(
                char, self.decoder.decode(
                    self.encoder.encode(char)))

    def test_prevent_script_breakout(self):
        bad_string = '</script><script>alert("gotcha")</script>'
        self.assertEqual(
            r'"\u003c/script\u003e\u003cscript\u003e'
            r'alert(\"gotcha\")\u003c/script\u003e"',
            self.encoder.encode(bad_string))
        self.assertEqual(
            bad_string, self.decoder.decode(
                self.encoder.encode(bad_string)))
import sys, pickle
#from unittest import TestCase

import simplejson as json
#from simplejson.compat import text_type, b

class TestErrors(TestCase):
    def test_string_keys_error(self):
        data = [{'a': 'A', 'b': (2, 4), 'c': 3.0, ('d',): 'D tuple'}]
        try:
            json.dumps(data)
        except TypeError:
            err = sys.exc_info()[1]
        else:
            self.fail('Expected TypeError')
        self.assertEqual(str(err),
                'keys must be str, int, float, bool or None, not tuple')

    def test_not_serializable(self):
        try:
            json.dumps(json)
        except TypeError:
            err = sys.exc_info()[1]
        else:
            self.fail('Expected TypeError')
        self.assertEqual(str(err),
                'Object of type module is not JSON serializable')

    def test_decode_error(self):
        err = None
        try:
            json.loads('{}\na\nb')
        except json.JSONDecodeError:
            err = sys.exc_info()[1]
        else:
            self.fail('Expected JSONDecodeError')
        self.assertEqual(err.lineno, 2)
        self.assertEqual(err.colno, 1)
        self.assertEqual(err.endlineno, 3)
        self.assertEqual(err.endcolno, 2)

    def test_scan_error(self):
        err = None
        for t in (text_type, b):
            try:
                json.loads(t('{"asdf": "'))
            except json.JSONDecodeError:
                err = sys.exc_info()[1]
            else:
                self.fail('Expected JSONDecodeError')
            self.assertEqual(err.lineno, 1)
            self.assertEqual(err.colno, 10)

    def test_error_is_pickable(self):
        err = None
        try:
            json.loads('{}\na\nb')
        except json.JSONDecodeError:
            err = sys.exc_info()[1]
        else:
            self.fail('Expected JSONDecodeError')
        s = pickle.dumps(err)
        e = pickle.loads(s)

        self.assertEqual(err.msg, e.msg)
        self.assertEqual(err.doc, e.doc)
        self.assertEqual(err.pos, e.pos)
        self.assertEqual(err.end, e.end)
import sys
#from unittest import TestCase

import simplejson as json

# 2007-10-05
JSONDOCS = [
    # http://json.org/JSON_checker/test/fail1.json
    '"A JSON payload should be an object or array, not a string."',
    # http://json.org/JSON_checker/test/fail2.json
    '["Unclosed array"',
    # http://json.org/JSON_checker/test/fail3.json
    '{unquoted_key: "keys must be quoted"}',
    # http://json.org/JSON_checker/test/fail4.json
    '["extra comma",]',
    # http://json.org/JSON_checker/test/fail5.json
    '["double extra comma",,]',
    # http://json.org/JSON_checker/test/fail6.json
    '[   , "<-- missing value"]',
    # http://json.org/JSON_checker/test/fail7.json
    '["Comma after the close"],',
    # http://json.org/JSON_checker/test/fail8.json
    '["Extra close"]]',
    # http://json.org/JSON_checker/test/fail9.json
    '{"Extra comma": true,}',
    # http://json.org/JSON_checker/test/fail10.json
    '{"Extra value after close": true} "misplaced quoted value"',
    # http://json.org/JSON_checker/test/fail11.json
    '{"Illegal expression": 1 + 2}',
    # http://json.org/JSON_checker/test/fail12.json
    '{"Illegal invocation": alert()}',
    # http://json.org/JSON_checker/test/fail13.json
    '{"Numbers cannot have leading zeroes": 013}',
    # http://json.org/JSON_checker/test/fail14.json
    '{"Numbers cannot be hex": 0x14}',
    # http://json.org/JSON_checker/test/fail15.json
    '["Illegal backslash escape: \\x15"]',
    # http://json.org/JSON_checker/test/fail16.json
    '[\\naked]',
    # http://json.org/JSON_checker/test/fail17.json
    '["Illegal backslash escape: \\017"]',
    # http://json.org/JSON_checker/test/fail18.json
    '[[[[[[[[[[[[[[[[[[[["Too deep"]]]]]]]]]]]]]]]]]]]]',
    # http://json.org/JSON_checker/test/fail19.json
    '{"Missing colon" null}',
    # http://json.org/JSON_checker/test/fail20.json
    '{"Double colon":: null}',
    # http://json.org/JSON_checker/test/fail21.json
    '{"Comma instead of colon", null}',
    # http://json.org/JSON_checker/test/fail22.json
    '["Colon instead of comma": false]',
    # http://json.org/JSON_checker/test/fail23.json
    '["Bad value", truth]',
    # http://json.org/JSON_checker/test/fail24.json
    "['single quote']",
    # http://json.org/JSON_checker/test/fail25.json
    '["\ttab\tcharacter\tin\tstring\t"]',
    # http://json.org/JSON_checker/test/fail26.json
    '["tab\\   character\\   in\\  string\\  "]',
    # http://json.org/JSON_checker/test/fail27.json
    '["line\nbreak"]',
    # http://json.org/JSON_checker/test/fail28.json
    '["line\\\nbreak"]',
    # http://json.org/JSON_checker/test/fail29.json
    '[0e]',
    # http://json.org/JSON_checker/test/fail30.json
    '[0e+]',
    # http://json.org/JSON_checker/test/fail31.json
    '[0e+-1]',
    # http://json.org/JSON_checker/test/fail32.json
    '{"Comma instead if closing brace": true,',
    # http://json.org/JSON_checker/test/fail33.json
    '["mismatch"}',
    # http://code.google.com/p/simplejson/issues/detail?id=3
    u'["A\u001FZ control characters in string"]',
    # misc based on coverage
    '{',
    '{]',
    '{"foo": "bar"]',
    '{"foo": "bar"',
    'nul',
    'nulx',
    '-',
    '-x',
    '-e',
    '-e0',
    '-Infinite',
    '-Inf',
    'Infinit',
    'Infinite',
    'NaM',
    'NuN',
    'falsy',
    'fal',
    'trug',
    'tru',
    '1e',
    '1ex',
    '1e-',
    '1e-x',
]

SKIPS = {
    1: "why not have a string payload?",
    18: "spec doesn't specify any nesting limitations",
}

class TestFail(TestCase):
    def test_failures(self):
        for idx, doc in enumerate(JSONDOCS):
            idx = idx + 1
            if idx in SKIPS:
                json.loads(doc)
                continue
            try:
                json.loads(doc)
            except json.JSONDecodeError:
                pass
            else:
                self.fail("Expected failure for fail%d.json: %r" % (idx, doc))

    def test_array_decoder_issue46(self):
        # http://code.google.com/p/simplejson/issues/detail?id=46
        for doc in [u'[,]', '[,]']:
            try:
                json.loads(doc)
            except json.JSONDecodeError:
                e = sys.exc_info()[1]
                self.assertEqual(e.pos, 1)
                self.assertEqual(e.lineno, 1)
                self.assertEqual(e.colno, 2)
            except Exception:
                e = sys.exc_info()[1]
                self.fail("Unexpected exception raised %r %s" % (e, e))
            else:
                self.fail("Unexpected success parsing '[,]'")

    def test_truncated_input(self):
        test_cases = [
            ('', 'Expecting value', 0),
            ('[', "Expecting value or ']'", 1),
            ('[42', "Expecting ',' delimiter", 3),
            ('[42,', 'Expecting value', 4),
            ('["', 'Unterminated string starting at', 1),
            ('["spam', 'Unterminated string starting at', 1),
            ('["spam"', "Expecting ',' delimiter", 7),
            ('["spam",', 'Expecting value', 8),
            ('{', 'Expecting property name enclosed in double quotes', 1),
            ('{"', 'Unterminated string starting at', 1),
            ('{"spam', 'Unterminated string starting at', 1),
            ('{"spam"', "Expecting ':' delimiter", 7),
            ('{"spam":', 'Expecting value', 8),
            ('{"spam":42', "Expecting ',' delimiter", 10),
            ('{"spam":42,', 'Expecting property name enclosed in double quotes',
             11),
            ('"', 'Unterminated string starting at', 0),
            ('"spam', 'Unterminated string starting at', 0),
            ('[,', "Expecting value", 1),
        ]
        for data, msg, idx in test_cases:
            try:
                json.loads(data)
            except json.JSONDecodeError:
                e = sys.exc_info()[1]
                self.assertEqual(
                    e.msg[:len(msg)],
                    msg,
                    "%r doesn't start with %r for %r" % (e.msg, msg, data))
                self.assertEqual(
                    e.pos, idx,
                    "pos %r != %r for %r" % (e.pos, idx, data))
            except Exception:
                e = sys.exc_info()[1]
                self.fail("Unexpected exception raised %r %s" % (e, e))
            else:
                self.fail("Unexpected success parsing '%r'" % (data,))
import math
from unittest import TestCase
#from simplejson.compat import long_type, text_type
#import simplejson as json
#from simplejson.decoder import NaN, PosInf, NegInf

class TestFloat(TestCase):
    def test_degenerates_allow(self):
        for inf in (PosInf, NegInf):
            self.assertEqual(json.loads(json.dumps(inf)), inf)
        # Python 2.5 doesn't have math.isnan
        nan = json.loads(json.dumps(NaN))
        self.assertTrue((0 + nan) != nan)

    def test_degenerates_ignore(self):
        for f in (PosInf, NegInf, NaN):
            self.assertEqual(json.loads(json.dumps(f, ignore_nan=True)), None)

    def test_degenerates_deny(self):
        for f in (PosInf, NegInf, NaN):
            self.assertRaises(ValueError, json.dumps, f, allow_nan=False)

    def test_floats(self):
        for num in [1617161771.7650001, math.pi, math.pi**100,
                    math.pi**-100, 3.1]:
            self.assertEqual(float(json.dumps(num)), num)
            self.assertEqual(json.loads(json.dumps(num)), num)
            self.assertEqual(json.loads(text_type(json.dumps(num))), num)

    def test_ints(self):
        for num in [1, long_type(1), 1<<32, 1<<64]:
            self.assertEqual(json.dumps(num), str(num))
            self.assertEqual(int(json.dumps(num)), num)
            self.assertEqual(json.loads(json.dumps(num)), num)
            self.assertEqual(json.loads(text_type(json.dumps(num))), num)
import unittest
import simplejson as json


class ForJson(object):
    def for_json(self):
        return {'for_json': 1}


class NestedForJson(object):
    def for_json(self):
        return {'nested': ForJson()}


class ForJsonList(object):
    def for_json(self):
        return ['list']


class DictForJson(dict):
    def for_json(self):
        return {'alpha': 1}


class ListForJson(list):
    def for_json(self):
        return ['list']


class TestForJson(unittest.TestCase):
    def assertRoundTrip(self, obj, other, for_json=True):
        if for_json is None:
            # None will use the default
            s = json.dumps(obj)
        else:
            s = json.dumps(obj, for_json=for_json)
        self.assertEqual(
            json.loads(s),
            other)

    def test_for_json_encodes_stand_alone_object(self):
        self.assertRoundTrip(
            ForJson(),
            ForJson().for_json())

    def test_for_json_encodes_object_nested_in_dict(self):
        self.assertRoundTrip(
            {'hooray': ForJson()},
            {'hooray': ForJson().for_json()})

    def test_for_json_encodes_object_nested_in_list_within_dict(self):
        self.assertRoundTrip(
            {'list': [0, ForJson(), 2, 3]},
            {'list': [0, ForJson().for_json(), 2, 3]})

    def test_for_json_encodes_object_nested_within_object(self):
        self.assertRoundTrip(
            NestedForJson(),
            {'nested': {'for_json': 1}})

    def test_for_json_encodes_list(self):
        self.assertRoundTrip(
            ForJsonList(),
            ForJsonList().for_json())

    def test_for_json_encodes_list_within_object(self):
        self.assertRoundTrip(
            {'nested': ForJsonList()},
            {'nested': ForJsonList().for_json()})

    def test_for_json_encodes_dict_subclass(self):
        self.assertRoundTrip(
            DictForJson(a=1),
            DictForJson(a=1).for_json())

    def test_for_json_encodes_list_subclass(self):
        self.assertRoundTrip(
            ListForJson(['l']),
            ListForJson(['l']).for_json())

    def test_for_json_ignored_if_not_true_with_dict_subclass(self):
        for for_json in (None, False):
            self.assertRoundTrip(
                DictForJson(a=1),
                {'a': 1},
                for_json=for_json)

    def test_for_json_ignored_if_not_true_with_list_subclass(self):
        for for_json in (None, False):
            self.assertRoundTrip(
                ListForJson(['l']),
                ['l'],
                for_json=for_json)

    def test_raises_typeerror_if_for_json_not_true_with_object(self):
        self.assertRaises(TypeError, json.dumps, ForJson())
        self.assertRaises(TypeError, json.dumps, ForJson(), for_json=False)
#from unittest import TestCase
import textwrap

import simplejson as json
#from simplejson.compat import StringIO

class TestIndent(TestCase):
    def test_indent(self):
        h = [['blorpie'], ['whoops'], [], 'd-shtaeou', 'd-nthiouh',
             'i-vhbjkhnth',
             {'nifty': 87}, {'field': 'yes', 'morefield': False} ]

        expect = textwrap.dedent("""\
        [
        \t[
        \t\t"blorpie"
        \t],
        \t[
        \t\t"whoops"
        \t],
        \t[],
        \t"d-shtaeou",
        \t"d-nthiouh",
        \t"i-vhbjkhnth",
        \t{
        \t\t"nifty": 87
        \t},
        \t{
        \t\t"field": "yes",
        \t\t"morefield": false
        \t}
        ]""")


        d1 = json.dumps(h)
        d2 = json.dumps(h, indent='\t', sort_keys=True, separators=(',', ': '))
        d3 = json.dumps(h, indent='  ', sort_keys=True, separators=(',', ': '))
        d4 = json.dumps(h, indent=2, sort_keys=True, separators=(',', ': '))

        h1 = json.loads(d1)
        h2 = json.loads(d2)
        h3 = json.loads(d3)
        h4 = json.loads(d4)

        self.assertEqual(h1, h)
        self.assertEqual(h2, h)
        self.assertEqual(h3, h)
        self.assertEqual(h4, h)
        self.assertEqual(d3, expect.replace('\t', '  '))
        self.assertEqual(d4, expect.replace('\t', '  '))
        # NOTE: Python 2.4 textwrap.dedent converts tabs to spaces,
        #       so the following is expected to fail. Python 2.4 is not a
        #       supported platform in simplejson 2.1.0+.
        self.assertEqual(d2, expect)

    def test_indent0(self):
        h = {3: 1}
        def check(indent, expected):
            d1 = json.dumps(h, indent=indent)
            self.assertEqual(d1, expected)

            sio = StringIO()
            json.dump(h, sio, indent=indent)
            self.assertEqual(sio.getvalue(), expected)

        # indent=0 should emit newlines
        check(0, '{\n"3": 1\n}')
        # indent=None is more compact
        check(None, '{"3": 1}')

    def test_separators(self):
        lst = [1,2,3,4]
        expect = '[\n1,\n2,\n3,\n4\n]'
        expect_spaces = '[\n1, \n2, \n3, \n4\n]'
        # Ensure that separators still works
        self.assertEqual(
            expect_spaces,
            json.dumps(lst, indent=0, separators=(', ', ': ')))
        # Force the new defaults
        self.assertEqual(
            expect,
            json.dumps(lst, indent=0, separators=(',', ': ')))
        # Added in 2.1.4
        self.assertEqual(
            expect,
            json.dumps(lst, indent=0))
#from unittest import TestCase

import simplejson as json
from operator import itemgetter

class TestItemSortKey(TestCase):
    def test_simple_first(self):
        a = {'a': 1, 'c': 5, 'jack': 'jill', 'pick': 'axe', 'array': [1, 5, 6, 9], 'tuple': (83, 12, 3), 'crate': 'dog', 'zeak': 'oh'}
        self.assertEqual(
            '{"a": 1, "c": 5, "crate": "dog", "jack": "jill", "pick": "axe", "zeak": "oh", "array": [1, 5, 6, 9], "tuple": [83, 12, 3]}',
            json.dumps(a, item_sort_key=json.simple_first))

    def test_case(self):
        a = {'a': 1, 'c': 5, 'Jack': 'jill', 'pick': 'axe', 'Array': [1, 5, 6, 9], 'tuple': (83, 12, 3), 'crate': 'dog', 'zeak': 'oh'}
        self.assertEqual(
            '{"Array": [1, 5, 6, 9], "Jack": "jill", "a": 1, "c": 5, "crate": "dog", "pick": "axe", "tuple": [83, 12, 3], "zeak": "oh"}',
            json.dumps(a, item_sort_key=itemgetter(0)))
        self.assertEqual(
            '{"a": 1, "Array": [1, 5, 6, 9], "c": 5, "crate": "dog", "Jack": "jill", "pick": "axe", "tuple": [83, 12, 3], "zeak": "oh"}',
            json.dumps(a, item_sort_key=lambda kv: kv[0].lower()))

    def test_item_sort_key_value(self):
        # https://github.com/simplejson/simplejson/issues/173
        a = {'a': 1, 'b': 0}
        self.assertEqual(
            '{"b": 0, "a": 1}',
            json.dumps(a, item_sort_key=lambda kv: kv[1]))
import unittest
#from simplejson.compat import StringIO

import simplejson as json

def iter_dumps(obj, **kw):
    return ''.join(json.JSONEncoder(**kw).iterencode(obj))

def sio_dump(obj, **kw):
    sio = StringIO()
    json.dumps(obj, **kw)
    return sio.getvalue()

class TestIterable(unittest.TestCase):
    def test_iterable(self):
        for l in ([], [1], [1, 2], [1, 2, 3]):
            for opts in [{}, {'indent': 2}]:
                for dumps in (json.dumps, iter_dumps, sio_dump):
                    expect = dumps(l, **opts)
                    default_expect = dumps(sum(l), **opts)
                    # Default is False
                    self.assertRaises(TypeError, dumps, iter(l), **opts)
                    self.assertRaises(TypeError, dumps, iter(l), iterable_as_array=False, **opts)
                    self.assertEqual(expect, dumps(iter(l), iterable_as_array=True, **opts))
                    # Ensure that the "default" gets called
                    self.assertEqual(default_expect, dumps(iter(l), default=sum, **opts))
                    self.assertEqual(default_expect, dumps(iter(l), iterable_as_array=False, default=sum, **opts))
                    # Ensure that the "default" does not get called
                    self.assertEqual(
                        expect,
                        dumps(iter(l), iterable_as_array=True, default=sum, **opts))
import unittest
import simplejson as json
#from simplejson.compat import StringIO

try:
    from collections import namedtuple
except ImportError:
    class Value(tuple):
        def __new__(cls, *args):
            return tuple.__new__(cls, args)

        def _asdict(self):
            return {'value': self[0]}
    class Point(tuple):
        def __new__(cls, *args):
            return tuple.__new__(cls, args)

        def _asdict(self):
            return {'x': self[0], 'y': self[1]}
else:
    Value = namedtuple('Value', ['value'])
    Point = namedtuple('Point', ['x', 'y'])

class DuckValue(object):
    def __init__(self, *args):
        self.value = Value(*args)

    def _asdict(self):
        return self.value._asdict()

class DuckPoint(object):
    def __init__(self, *args):
        self.point = Point(*args)

    def _asdict(self):
        return self.point._asdict()

class DeadDuck(object):
    _asdict = None

class DeadDict(dict):
    _asdict = None

CONSTRUCTORS = [
    lambda v: v,
    lambda v: [v],
    lambda v: [{'key': v}],
]

class TestNamedTuple(unittest.TestCase):
    def test_namedtuple_dumps(self):
        for v in [Value(1), Point(1, 2), DuckValue(1), DuckPoint(1, 2)]:
            d = v._asdict()
            self.assertEqual(d, json.loads(json.dumps(v)))
            self.assertEqual(
                d,
                json.loads(json.dumps(v, namedtuple_as_object=True)))
            self.assertEqual(d, json.loads(json.dumps(v, tuple_as_array=False)))
            self.assertEqual(
                d,
                json.loads(json.dumps(v, namedtuple_as_object=True,
                                      tuple_as_array=False)))

    def test_namedtuple_dumps_false(self):
        for v in [Value(1), Point(1, 2)]:
            l = list(v)
            self.assertEqual(
                l,
                json.loads(json.dumps(v, namedtuple_as_object=False)))
            self.assertRaises(TypeError, json.dumps, v,
                tuple_as_array=False, namedtuple_as_object=False)

    def test_namedtuple_dump(self):
        for v in [Value(1), Point(1, 2), DuckValue(1), DuckPoint(1, 2)]:
            d = v._asdict()
            sio = StringIO()
            json.dump(v, sio)
            self.assertEqual(d, json.loads(sio.getvalue()))
            sio = StringIO()
            json.dump(v, sio, namedtuple_as_object=True)
            self.assertEqual(
                d,
                json.loads(sio.getvalue()))
            sio = StringIO()
            json.dump(v, sio, tuple_as_array=False)
            self.assertEqual(d, json.loads(sio.getvalue()))
            sio = StringIO()
            json.dump(v, sio, namedtuple_as_object=True,
                      tuple_as_array=False)
            self.assertEqual(
                d,
                json.loads(sio.getvalue()))

    def test_namedtuple_dump_false(self):
        for v in [Value(1), Point(1, 2)]:
            l = list(v)
            sio = StringIO()
            json.dump(v, sio, namedtuple_as_object=False)
            self.assertEqual(
                l,
                json.loads(sio.getvalue()))
            self.assertRaises(TypeError, json.dump, v, StringIO(),
                tuple_as_array=False, namedtuple_as_object=False)

    def test_asdict_not_callable_dump(self):
        for f in CONSTRUCTORS:
            self.assertRaises(TypeError,
                json.dump, f(DeadDuck()), StringIO(), namedtuple_as_object=True)
            sio = StringIO()
            json.dump(f(DeadDict()), sio, namedtuple_as_object=True)
            self.assertEqual(
                json.dumps(f({})),
                sio.getvalue())

    def test_asdict_not_callable_dumps(self):
        for f in CONSTRUCTORS:
            self.assertRaises(TypeError,
                json.dumps, f(DeadDuck()), namedtuple_as_object=True)
            self.assertEqual(
                json.dumps(f({})),
                json.dumps(f(DeadDict()), namedtuple_as_object=True))
#from unittest import TestCase

import simplejson as json

# from http://json.org/JSON_checker/test/pass1.json
JSON = r'''
[
    "JSON Test Pattern pass1",
    {"object with 1 member":["array with 1 element"]},
    {},
    [],
    -42,
    true,
    false,
    null,
    {
        "integer": 1234567890,
        "real": -9876.543210,
        "e": 0.123456789e-12,
        "E": 1.234567890E+34,
        "":  23456789012E66,
        "zero": 0,
        "one": 1,
        "space": " ",
        "quote": "\"",
        "backslash": "\\",
        "controls": "\b\f\n\r\t",
        "slash": "/ & \/",
        "alpha": "abcdefghijklmnopqrstuvwyz",
        "ALPHA": "ABCDEFGHIJKLMNOPQRSTUVWYZ",
        "digit": "0123456789",
        "special": "`1~!@#$%^&*()_+-={':[,]}|;.</>?",
        "hex": "\u0123\u4567\u89AB\uCDEF\uabcd\uef4A",
        "true": true,
        "false": false,
        "null": null,
        "array":[  ],
        "object":{  },
        "address": "50 St. James Street",
        "url": "http://www.JSON.org/",
        "comment": "// /* <!-- --",
        "# -- --> */": " ",
        " s p a c e d " :[1,2 , 3

,

4 , 5        ,          6           ,7        ],"compact": [1,2,3,4,5,6,7],
        "jsontext": "{\"object with 1 member\":[\"array with 1 element\"]}",
        "quotes": "&#34; \u0022 %22 0x22 034 &#x22;",
        "\/\\\"\uCAFE\uBABE\uAB98\uFCDE\ubcda\uef4A\b\f\n\r\t`1~!@#$%^&*()_+-=[]{}|;:',./<>?"
: "A key can be any string"
    },
    0.5 ,98.6
,
99.44
,

1066,
1e1,
0.1e1,
1e-1,
1e00,2e+00,2e-00
,"rosebud"]
'''

class TestPass1(TestCase):
    def test_parse(self):
        # test in/out equivalence and parsing
        res = json.loads(JSON)
        out = json.dumps(res)
        self.assertEqual(res, json.loads(out))
#from unittest import TestCase
import simplejson as json

# from http://json.org/JSON_checker/test/pass2.json
JSON = r'''
[[[[[[[[[[[[[[[[[[["Not too deep"]]]]]]]]]]]]]]]]]]]
'''

class TestPass2(TestCase):
    def test_parse(self):
        # test in/out equivalence and parsing
        res = json.loads(JSON)
        out = json.dumps(res)
        self.assertEqual(res, json.loads(out))
#from unittest import TestCase

import simplejson as json

# from http://json.org/JSON_checker/test/pass3.json
JSON = r'''
{
    "JSON Test Pattern pass3": {
        "The outermost value": "must be an object or array.",
        "In this test": "It is an object."
    }
}
'''

class TestPass3(TestCase):
    def test_parse(self):
        # test in/out equivalence and parsing
        res = json.loads(JSON)
        out = json.dumps(res)
        self.assertEqual(res, json.loads(out))
import unittest
import simplejson as json

dct1 = {
    'key1': 'value1'
}

dct2 = {
    'key2': 'value2',
    'd1': dct1
}

dct3 = {
    'key2': 'value2',
    'd1': json.dumps(dct1)
}

dct4 = {
    'key2': 'value2',
    'd1': json.RawJSON(json.dumps(dct1))
}


class TestRawJson(unittest.TestCase):

    def test_normal_str(self):
        self.assertNotEqual(json.dumps(dct2), json.dumps(dct3))

    def test_raw_json_str(self):
        self.assertEqual(json.dumps(dct2), json.dumps(dct4))
        self.assertEqual(dct2, json.loads(json.dumps(dct4)))

    def test_list(self):
        self.assertEqual(
            json.dumps([dct2]),
            json.dumps([json.RawJSON(json.dumps(dct2))]))
        self.assertEqual(
            [dct2],
            json.loads(json.dumps([json.RawJSON(json.dumps(dct2))])))

    def test_direct(self):
        self.assertEqual(
            json.dumps(dct2),
            json.dumps(json.RawJSON(json.dumps(dct2))))
        self.assertEqual(
            dct2,
            json.loads(json.dumps(json.RawJSON(json.dumps(dct2)))))
#from unittest import TestCase

import simplejson as json

class JSONTestObject:
    pass


class RecursiveJSONEncoder(json.JSONEncoder):
    recurse = False
    def default(self, o):
        if o is JSONTestObject:
            if self.recurse:
                return [JSONTestObject]
            else:
                return 'JSONTestObject'
        return json.JSONEncoder.default(o)


class TestRecursion(TestCase):
    def test_listrecursion(self):
        x = []
        x.append(x)
        try:
            json.dumps(x)
        except ValueError:
            pass
        else:
            self.fail("didn't raise ValueError on list recursion")
        x = []
        y = [x]
        x.append(y)
        try:
            json.dumps(x)
        except ValueError:
            pass
        else:
            self.fail("didn't raise ValueError on alternating list recursion")
        y = []
        x = [y, y]
        # ensure that the marker is cleared
        json.dumps(x)

    def test_dictrecursion(self):
        x = {}
        x["test"] = x
        try:
            json.dumps(x)
        except ValueError:
            pass
        else:
            self.fail("didn't raise ValueError on dict recursion")
        x = {}
        y = {"a": x, "b": x}
        # ensure that the marker is cleared
        json.dumps(y)

    def test_defaultrecursion(self):
        enc = RecursiveJSONEncoder()
        self.assertEqual(enc.encode(JSONTestObject), '"JSONTestObject"')
        enc.recurse = True
        try:
            enc.encode(JSONTestObject)
        except ValueError:
            pass
        else:
            self.fail("didn't raise ValueError on default recursion")
import sys
#from unittest import TestCase

#import simplejson as json
#import simplejson.decoder
#from simplejson.compat import b, PY3

class TestScanString(TestCase):
    # The bytes type is intentionally not used in most of these tests
    # under Python 3 because the decoder immediately coerces to str before
    # calling scanstring. In Python 2 we are testing the code paths
    # for both unicode and str.
    #
    # The reason this is done is because Python 3 would require
    # entirely different code paths for parsing bytes and str.
    #
    def test_py_scanstring(self):
        self._test_scanstring(json.py_scanstring)

    def _test_scanstring(self, scanstring):
        if sys.maxunicode == 65535:
            self.assertEqual(
                scanstring(u'"z\U0001d120x"', 1, None, True),
                (u'z\U0001d120x', 6))
        else:
            self.assertEqual(
                scanstring(u'"z\U0001d120x"', 1, None, True),
                (u'z\U0001d120x', 5))

        self.assertEqual(
            scanstring('"\\u007b"', 1, None, True),
            (u'{', 8))

        self.assertEqual(
            scanstring('"A JSON payload should be an object or array, not a string."', 1, None, True),
            (u'A JSON payload should be an object or array, not a string.', 60))

        self.assertEqual(
            scanstring('["Unclosed array"', 2, None, True),
            (u'Unclosed array', 17))

        self.assertEqual(
            scanstring('["extra comma",]', 2, None, True),
            (u'extra comma', 14))

        self.assertEqual(
            scanstring('["double extra comma",,]', 2, None, True),
            (u'double extra comma', 21))

        self.assertEqual(
            scanstring('["Comma after the close"],', 2, None, True),
            (u'Comma after the close', 24))

        self.assertEqual(
            scanstring('["Extra close"]]', 2, None, True),
            (u'Extra close', 14))

        self.assertEqual(
            scanstring('{"Extra comma": true,}', 2, None, True),
            (u'Extra comma', 14))

        self.assertEqual(
            scanstring('{"Extra value after close": true} "misplaced quoted value"', 2, None, True),
            (u'Extra value after close', 26))

        self.assertEqual(
            scanstring('{"Illegal expression": 1 + 2}', 2, None, True),
            (u'Illegal expression', 21))

        self.assertEqual(
            scanstring('{"Illegal invocation": alert()}', 2, None, True),
            (u'Illegal invocation', 21))

        self.assertEqual(
            scanstring('{"Numbers cannot have leading zeroes": 013}', 2, None, True),
            (u'Numbers cannot have leading zeroes', 37))

        self.assertEqual(
            scanstring('{"Numbers cannot be hex": 0x14}', 2, None, True),
            (u'Numbers cannot be hex', 24))

        self.assertEqual(
            scanstring('[[[[[[[[[[[[[[[[[[[["Too deep"]]]]]]]]]]]]]]]]]]]]', 21, None, True),
            (u'Too deep', 30))

        self.assertEqual(
            scanstring('{"Missing colon" null}', 2, None, True),
            (u'Missing colon', 16))

        self.assertEqual(
            scanstring('{"Double colon":: null}', 2, None, True),
            (u'Double colon', 15))

        self.assertEqual(
            scanstring('{"Comma instead of colon", null}', 2, None, True),
            (u'Comma instead of colon', 25))

        self.assertEqual(
            scanstring('["Colon instead of comma": false]', 2, None, True),
            (u'Colon instead of comma', 25))

        self.assertEqual(
            scanstring('["Bad value", truth]', 2, None, True),
            (u'Bad value', 12))

        for c in map(chr, range(0x00, 0x1f)):
            self.assertEqual(
                scanstring(c + '"', 0, None, False),
                (c, 2))
            self.assertRaises(
                ValueError,
                scanstring, c + '"', 0, None, True)

        self.assertRaises(ValueError, scanstring, '', 0, None, True)
        self.assertRaises(ValueError, scanstring, 'a', 0, None, True)
        self.assertRaises(ValueError, scanstring, '\\', 0, None, True)
        self.assertRaises(ValueError, scanstring, '\\u', 0, None, True)
        self.assertRaises(ValueError, scanstring, '\\u0', 0, None, True)
        self.assertRaises(ValueError, scanstring, '\\u01', 0, None, True)
        self.assertRaises(ValueError, scanstring, '\\u012', 0, None, True)
        self.assertRaises(ValueError, scanstring, '\\u0123', 0, None, True)
        if sys.maxunicode > 65535:
            self.assertRaises(ValueError,
                              scanstring, '\\ud834\\u"', 0, None, True)
            self.assertRaises(ValueError,
                              scanstring, '\\ud834\\x0123"', 0, None, True)

    def test_issue3623(self):
        self.assertRaises(ValueError, json.scanstring, "xxx", 1,
                          "xxx")
        self.assertRaises(UnicodeDecodeError,
                          json.encode_basestring_ascii, b("xx\xff"))

    def test_overflow(self):
        # Python 2.5 does not have maxsize, Python 3 does not have maxint
        maxsize = getattr(sys, 'maxsize', getattr(sys, 'maxint', None))
        assert maxsize is not None
        self.assertRaises(OverflowError, json.scanstring, "xxx",
                          maxsize + 1)

    def test_surrogates(self):
        scanstring = json.scanstring

        def assertScan(given, expect, test_utf8=True):
            givens = [given]
            if not PY3 and test_utf8:
                givens.append(given.encode('utf8'))
            for given in givens:
                (res, count) = scanstring(given, 1, None, True)
                self.assertEqual(len(given), count)
                self.assertEqual(res, expect)

        assertScan(
            u'"z\\ud834\\u0079x"',
            u'z\ud834yx')
        assertScan(
            u'"z\\ud834\\udd20x"',
            u'z\U0001d120x')
        assertScan(
            u'"z\\ud834\\ud834\\udd20x"',
            u'z\ud834\U0001d120x')
        assertScan(
            u'"z\\ud834x"',
            u'z\ud834x')
        assertScan(
            u'"z\\udd20x"',
            u'z\udd20x')
        assertScan(
            u'"z\ud834x"',
            u'z\ud834x')
        # It may look strange to join strings together, but Python is drunk.
        # https://gist.github.com/etrepum/5538443
        assertScan(
            u'"z\\ud834\udd20x12345"',
            u''.join([u'z\ud834', u'\udd20x12345']))
        assertScan(
            u'"z\ud834\\udd20x"',
            u''.join([u'z\ud834', u'\udd20x']))
        # these have different behavior given UTF8 input, because the surrogate
        # pair may be joined (in maxunicode > 65535 builds)
        assertScan(
            u''.join([u'"z\ud834', u'\udd20x"']),
            u''.join([u'z\ud834', u'\udd20x']),
            test_utf8=False)

        self.assertRaises(ValueError,
                          scanstring, u'"z\\ud83x"', 1, None, True)
        self.assertRaises(ValueError,
                          scanstring, u'"z\\ud834\\udd2x"', 1, None, True)
import textwrap
from unittest import TestCase

import simplejson as json


class TestSeparators(TestCase):
    def test_separators(self):
        h = [['blorpie'], ['whoops'], [], 'd-shtaeou', 'd-nthiouh', 'i-vhbjkhnth',
             {'nifty': 87}, {'field': 'yes', 'morefield': False} ]

        expect = textwrap.dedent("""\
        [
          [
            "blorpie"
          ] ,
          [
            "whoops"
          ] ,
          [] ,
          "d-shtaeou" ,
          "d-nthiouh" ,
          "i-vhbjkhnth" ,
          {
            "nifty" : 87
          } ,
          {
            "field" : "yes" ,
            "morefield" : false
          }
        ]""")


        d1 = json.dumps(h)
        d2 = json.dumps(h, indent='  ', sort_keys=True, separators=(' ,', ' : '))

        h1 = json.loads(d1)
        h2 = json.loads(d2)

        self.assertEqual(h1, h)
        self.assertEqual(h2, h)
        self.assertEqual(d2, expect)
#from __future__ import with_statement

import sys
import unittest
from unittest import TestCase

#import simplejson
#from simplejson import encoder, decoder, scanner
#from simplejson.compat import PY3, long_type, b



def skip_if_speedups_missing(func):
    def wrapper(*args, **kwargs):
        if hasattr(unittest, 'SkipTest'):
            raise unittest.SkipTest("C Extension not available")
        else:
            sys.stdout.write("C Extension not available")
            return
        return func(*args, **kwargs)

    return wrapper


class BadBool:
    def __bool__(self):
        1/0
    __nonzero__ = __bool__


class TestDecode(TestCase):
    @skip_if_speedups_missing
    def test_make_scanner(self):
        self.assertRaises(AttributeError, scanner.py_make_scanner, 1)

    @skip_if_speedups_missing
    def test_bad_bool_args(self):
        def test(value):
            json.JSONDecoder(strict=BadBool()).decode(value)
        self.assertRaises(ZeroDivisionError, test, '""')
        self.assertRaises(ZeroDivisionError, test, '{}')
        if not PY3:
            self.assertRaises(ZeroDivisionError, test, u'""')
            self.assertRaises(ZeroDivisionError, test, u'{}')

#from unittest import TestCase

#import simplejson
#from simplejson.compat import text_type

# Tests for issue demonstrated in https://github.com/simplejson/simplejson/issues/144
class WonkyTextSubclass(text_type):
    def __getslice__(self, start, end):
        return self.__class__('not what you wanted!')

class TestStrSubclass(TestCase):
    def test_dump_load(self):
        for s in ['', '"hello"', 'text', u'\u005c']:
            self.assertEqual(
                s,
                json.loads(json.dumps(WonkyTextSubclass(s))))

            self.assertEqual(
                s,
                json.loads(json.dumps(WonkyTextSubclass(s),
                                                  ensure_ascii=False)))
#from unittest import TestCase
#import simplejson as json

from decimal import Decimal

class AlternateInt(int):
    def __repr__(self):
        return 'invalid json'
    __str__ = __repr__


class AlternateFloat(float):
    def __repr__(self):
        return 'invalid json'
    __str__ = __repr__


# class AlternateDecimal(Decimal):
#     def __repr__(self):
#         return 'invalid json'


class TestSubclass(TestCase):
    def test_int(self):
        self.assertEqual(json.dumps(AlternateInt(1)), '1')
        self.assertEqual(json.dumps(AlternateInt(-1)), '-1')
        self.assertEqual(json.loads(json.dumps({AlternateInt(1): 1})), {'1': 1})

    def test_float(self):
        self.assertEqual(json.dumps(AlternateFloat(1.0)), '1.0')
        self.assertEqual(json.dumps(AlternateFloat(-1.0)), '-1.0')
        self.assertEqual(json.loads(json.dumps({AlternateFloat(1.0): 1})), {'1.0': 1})

    # NOTE: Decimal subclasses are not supported as-is
    # def test_decimal(self):
    #     self.assertEqual(json.dumps(AlternateDecimal('1.0')), '1.0')
    #     self.assertEqual(json.dumps(AlternateDecimal('-1.0')), '-1.0')
#from __future__ import with_statement
import os
import sys
import textwrap
import unittest
import subprocess
import tempfile
try:
    # Python 3.x
    from test.support import strip_python_stderr
except ImportError:
    # Python 2.6+
    try:
        from test.test_support import strip_python_stderr
    except ImportError:
        # Python 2.5
        import re
        def strip_python_stderr(stderr):
            return re.sub(
                r"\[\d+ refs\]\r?\n?$".encode(),
                "".encode(),
                stderr).strip()

def open_temp_file():
    if sys.version_info >= (2, 6):
        file = tempfile.NamedTemporaryFile(delete=False)
        filename = file.name
    else:
        fd, filename = tempfile.mkstemp()
        file = os.fdopen(fd, 'w+b')
    return file, filename

#from simplejson.compat import StringIO
#import simplejson as json

class TestTuples(unittest.TestCase):
    def test_tuple_array_dumps(self):
        t = (1, 2, 3)
        expect = json.dumps(list(t))
        # Default is True
        self.assertEqual(expect, json.dumps(t))
        self.assertEqual(expect, json.dumps(t, tuple_as_array=True))
        self.assertRaises(TypeError, json.dumps, t, tuple_as_array=False)
        # Ensure that the "default" does not get called
        self.assertEqual(expect, json.dumps(t, default=repr))
        self.assertEqual(expect, json.dumps(t, tuple_as_array=True,
                                            default=repr))
        # Ensure that the "default" gets called
        self.assertEqual(
            json.dumps(repr(t)),
            json.dumps(t, tuple_as_array=False, default=repr))

    def test_tuple_array_dump(self):
        t = (1, 2, 3)
        expect = json.dumps(list(t))
        # Default is True
        sio = StringIO()
        json.dump(t, sio)
        self.assertEqual(expect, sio.getvalue())
        sio = StringIO()
        json.dump(t, sio, tuple_as_array=True)
        self.assertEqual(expect, sio.getvalue())
        self.assertRaises(TypeError, json.dump, t, StringIO(),
                          tuple_as_array=False)
        # Ensure that the "default" does not get called
        sio = StringIO()
        json.dump(t, sio, default=repr)
        self.assertEqual(expect, sio.getvalue())
        sio = StringIO()
        json.dump(t, sio, tuple_as_array=True, default=repr)
        self.assertEqual(expect, sio.getvalue())
        # Ensure that the "default" gets called
        sio = StringIO()
        json.dump(t, sio, tuple_as_array=False, default=repr)
        self.assertEqual(
            json.dumps(repr(t)),
            sio.getvalue())
import sys
import codecs
from unittest import TestCase

import simplejson as json
#from simplejson.compat import unichr, text_type, b, BytesIO

class TestUnicode(TestCase):
    def test_encoding1(self):
        encoder = json.JSONEncoder(encoding='utf-8')
        u = u'\N{GREEK SMALL LETTER ALPHA}\N{GREEK CAPITAL LETTER OMEGA}'
        s = u.encode('utf-8')
        ju = encoder.encode(u)
        js = encoder.encode(s)
        self.assertEqual(ju, js)

    def test_encoding2(self):
        u = u'\N{GREEK SMALL LETTER ALPHA}\N{GREEK CAPITAL LETTER OMEGA}'
        s = u.encode('utf-8')
        ju = json.dumps(u, encoding='utf-8')
        js = json.dumps(s, encoding='utf-8')
        self.assertEqual(ju, js)

    def test_encoding3(self):
        u = u'\N{GREEK SMALL LETTER ALPHA}\N{GREEK CAPITAL LETTER OMEGA}'
        j = json.dumps(u)
        self.assertEqual(j, '"\\u03b1\\u03a9"')

    def test_encoding4(self):
        u = u'\N{GREEK SMALL LETTER ALPHA}\N{GREEK CAPITAL LETTER OMEGA}'
        j = json.dumps([u])
        self.assertEqual(j, '["\\u03b1\\u03a9"]')

    def test_encoding5(self):
        u = u'\N{GREEK SMALL LETTER ALPHA}\N{GREEK CAPITAL LETTER OMEGA}'
        j = json.dumps(u, ensure_ascii=False)
        self.assertEqual(j, u'"' + u + u'"')

    def test_encoding6(self):
        u = u'\N{GREEK SMALL LETTER ALPHA}\N{GREEK CAPITAL LETTER OMEGA}'
        j = json.dumps([u], ensure_ascii=False)
        self.assertEqual(j, u'["' + u + u'"]')

    def test_big_unicode_encode(self):
        u = u'\U0001d120'
        self.assertEqual(json.dumps(u), '"\\ud834\\udd20"')
        self.assertEqual(json.dumps(u, ensure_ascii=False), u'"\U0001d120"')

    def test_big_unicode_decode(self):
        u = u'z\U0001d120x'
        self.assertEqual(json.loads('"' + u + '"'), u)
        self.assertEqual(json.loads('"z\\ud834\\udd20x"'), u)

    def test_unicode_decode(self):
        for i in range(0, 0xd7ff):
            u = unichr(i)
            #s = '"\\u{0:04x}"'.format(i)
            s = '"\\u%04x"' % (i,)
            self.assertEqual(json.loads(s), u)

    def test_object_pairs_hook_with_unicode(self):
        s = u'{"xkd":1, "kcw":2, "art":3, "hxm":4, "qrt":5, "pad":6, "hoy":7}'
        p = [(u"xkd", 1), (u"kcw", 2), (u"art", 3), (u"hxm", 4),
             (u"qrt", 5), (u"pad", 6), (u"hoy", 7)]
        self.assertEqual(json.loads(s), eval(s))
        self.assertEqual(json.loads(s, object_pairs_hook=lambda x: x), p)
        od = json.loads(s, object_pairs_hook=json.OrderedDict)
        self.assertEqual(od, json.OrderedDict(p))
        self.assertEqual(type(od), json.OrderedDict)
        # the object_pairs_hook takes priority over the object_hook
        self.assertEqual(json.loads(s,
                                    object_pairs_hook=json.OrderedDict,
                                    object_hook=lambda x: None),
                         json.OrderedDict(p))


    def test_default_encoding(self):
        self.assertEqual(json.loads(u'{"a": "\xe9"}'.encode('utf-8')),
            {'a': u'\xe9'})

    def test_unicode_preservation(self):
        self.assertEqual(type(json.loads(u'""')), text_type)
        self.assertEqual(type(json.loads(u'"a"')), text_type)
        self.assertEqual(type(json.loads(u'["a"]')[0]), text_type)

    def test_ensure_ascii_false_returns_unicode(self):
        # http://code.google.com/p/simplejson/issues/detail?id=48
        self.assertEqual(type(json.dumps([], ensure_ascii=False)), text_type)
        self.assertEqual(type(json.dumps(0, ensure_ascii=False)), text_type)
        self.assertEqual(type(json.dumps({}, ensure_ascii=False)), text_type)
        self.assertEqual(type(json.dumps("", ensure_ascii=False)), text_type)

    def test_ensure_ascii_false_bytestring_encoding(self):
        # http://code.google.com/p/simplejson/issues/detail?id=48
        doc1 = {u'quux': b('Arr\xc3\xaat sur images')}
        doc2 = {u'quux': u'Arr\xeat sur images'}
        doc_ascii = '{"quux": "Arr\\u00eat sur images"}'
        doc_unicode = u'{"quux": "Arr\xeat sur images"}'
        self.assertEqual(json.dumps(doc1), doc_ascii)
        self.assertEqual(json.dumps(doc2), doc_ascii)
        self.assertEqual(json.dumps(doc1, ensure_ascii=False), doc_unicode)
        self.assertEqual(json.dumps(doc2, ensure_ascii=False), doc_unicode)

    def test_ensure_ascii_linebreak_encoding(self):
        # http://timelessrepo.com/json-isnt-a-javascript-subset
        s1 = u'\u2029\u2028'
        s2 = s1.encode('utf8')
        expect = '"\\u2029\\u2028"'
        expect_non_ascii = u'"\u2029\u2028"'
        self.assertEqual(json.dumps(s1), expect)
        self.assertEqual(json.dumps(s2), expect)
        self.assertEqual(json.dumps(s1, ensure_ascii=False), expect_non_ascii)
        self.assertEqual(json.dumps(s2, ensure_ascii=False), expect_non_ascii)

    def test_invalid_escape_sequences(self):
        # incomplete escape sequence
        self.assertRaises(json.JSONDecodeError, json.loads, '"\\u')
        self.assertRaises(json.JSONDecodeError, json.loads, '"\\u1')
        self.assertRaises(json.JSONDecodeError, json.loads, '"\\u12')
        self.assertRaises(json.JSONDecodeError, json.loads, '"\\u123')
        self.assertRaises(json.JSONDecodeError, json.loads, '"\\u1234')
        # invalid escape sequence
        self.assertRaises(json.JSONDecodeError, json.loads, '"\\u123x"')
        self.assertRaises(json.JSONDecodeError, json.loads, '"\\u12x4"')
        self.assertRaises(json.JSONDecodeError, json.loads, '"\\u1x34"')
        self.assertRaises(json.JSONDecodeError, json.loads, '"\\ux234"')
        if sys.maxunicode > 65535:
            # invalid escape sequence for low surrogate
            self.assertRaises(json.JSONDecodeError, json.loads, '"\\ud800\\u"')
            self.assertRaises(json.JSONDecodeError, json.loads, '"\\ud800\\u0"')
            self.assertRaises(json.JSONDecodeError, json.loads, '"\\ud800\\u00"')
            self.assertRaises(json.JSONDecodeError, json.loads, '"\\ud800\\u000"')
            self.assertRaises(json.JSONDecodeError, json.loads, '"\\ud800\\u000x"')
            self.assertRaises(json.JSONDecodeError, json.loads, '"\\ud800\\u00x0"')
            self.assertRaises(json.JSONDecodeError, json.loads, '"\\ud800\\u0x00"')
            self.assertRaises(json.JSONDecodeError, json.loads, '"\\ud800\\ux000"')

    def test_ensure_ascii_still_works(self):
        # in the ascii range, ensure that everything is the same
        for c in map(unichr, range(0, 127)):
            self.assertEqual(
                json.dumps(c, ensure_ascii=False),
                json.dumps(c))
        snowman = u'\N{SNOWMAN}'
        self.assertEqual(
            json.dumps(c, ensure_ascii=False),
            '"' + c + '"')

    def test_strip_bom(self):
        content = u"\u3053\u3093\u306b\u3061\u308f"
        json_doc = codecs.BOM_UTF8 + b(json.dumps(content))
        self.assertEqual(json.load(BytesIO(json_doc)), content)
        for doc in json_doc, json_doc.decode('utf8'):
            self.assertEqual(json.loads(doc), content)

def main():
    unittest.main()


if __name__ == "__main__":
    main()
