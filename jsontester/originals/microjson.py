import math
import io
import types
__pychecker__ = 'no-returnvalues'
WS = set([' ', '\t', '\r', '\n', '\b', '\f'])
DIGITS = set([str(i)for i in range(0, 10)])
NUMSTART = DIGITS.union(['.', '-', '+'])
NUMCHARS = NUMSTART.union(['e', 'E'])
ESC_MAP = {'n': '\n', 't': '\t', 'r': '\r', 'b': '\b', 'f': '\f'}
REV_ESC_MAP = dict([(_v, _k)for _k, _v in list(ESC_MAP.items())]+[('"', '"')])
E_BYTES = 'input string must be type str containing ASCII or UTF-8 bytes'
E_MALF = 'malformed JSON data'
E_TRUNC = 'truncated JSON data'
E_BOOL = 'expected boolean'
E_NULL = 'expected null'
E_LITEM = 'expected list item'
E_DKEY = 'expected key'
E_COLON = 'missing colon after key'
E_EMPTY = 'found empty string, not valid JSON data'
E_BADESC = 'bad escape character found'
E_UNSUPP = 'unsupported type "%s" cannot be JSON-encoded'
E_BADFLOAT = 'cannot emit floating point value "%s"'
NEG_INF = float('-inf')
POS_INF = float('inf')


class JSONError(Exception):
    def __init__(self, msg, stm=None, pos=0):
        if stm:
            msg += ' at position %d, "%s"' % (pos, repr(stm.substr(pos, 32)))
        Exception.__init__(self, msg)


class JSONStream(object):
    def __init__(self, data):
        self._stm = io.StringIO(data)

    @property
    def pos(self):
        return self._stm.tell()

    @property
    def len(self):
        return len(self._stm.getvalue())

    def getvalue(self):
        return self._stm.getvalue()

    def skipspaces(self):
        self._skip(lambda c: c not in WS)

    def _skip(self, stopcond):
        while True:
            c = self.peek()
            if stopcond(c)or c == '':
                break
            next(self)

    def __next__(self, size=1):
        return self._stm.read(size)

    def next_ord(self):
        return ord(next(self))

    def peek(self):
        if self.pos == self.len:
            return ''
        return self.getvalue()[self.pos]

    def substr(self, pos, length):
        return self.getvalue()[pos:pos+length]


def _decode_utf8(c0, stm):
    c0 = ord(c0)
    r = 0xFFFD
    nc = stm.next_ord
    if(c0 & 0xE0) == 0xC0:
        r = ((c0 & 0x1F) << 6)+(nc() & 0x3F)
    elif(c0 & 0xF0) == 0xE0:
        r = ((c0 & 0x0F) << 12)+((nc() & 0x3F) << 6)+(nc() & 0x3F)
    elif(c0 & 0xF8) == 0xF0:
        r = ((c0 & 0x07) << 18)+((nc() & 0x3F) << 12) + \
            ((nc() & 0x3F) << 6)+(nc() & 0x3F)
    return chr(r)


def decode_escape(c, stm):
    v = ESC_MAP.get(c, None)
    if v is not None:
        return v
    elif c != 'u':
        return c
    sv = 12
    r = 0
    for _ in range(0, 4):
        r |= int(next(stm), 16) << sv
        sv -= 4
    return chr(r)


def _from_json_string(stm):
    next(stm)
    r = []
    while True:
        c = next(stm)
        if c == '':
            raise JSONError(E_TRUNC, stm, stm.pos-1)
        elif c == '\\':
            c = next(stm)
            r.append(decode_escape(c, stm))
        elif c == '"':
            return ''.join(r)
        elif c > '\x7f':
            r.append(_decode_utf8(c, stm))
        else:
            r.append(c)


def _from_json_fixed(stm, expected, value, errmsg):
    off = len(expected)
    pos = stm.pos
    if stm.substr(pos, off) == expected:
        next(stm, off)
        return value
    raise JSONError(errmsg, stm, pos)


def _from_json_number(stm):
    is_float = 0
    saw_exp = 0
    pos = stm.pos
    while True:
        c = stm.peek()
        if c not in NUMCHARS:
            break
        elif c == '-' and not saw_exp:
            pass
        elif c in('.', 'e', 'E'):
            is_float = 1
            if c in('e', 'E'):
                saw_exp = 1
        next(stm)
    s = stm.substr(pos, stm.pos-pos)
    if is_float:
        return float(s)
    return int(s)


def _from_json_list(stm):
    next(stm)
    result = []
    pos = stm.pos
    while True:
        stm.skipspaces()
        c = stm.peek()
        if c == '':
            raise JSONError(E_TRUNC, stm, pos)
        elif c == ']':
            next(stm)
            return result
        elif c == ',':
            next(stm)
            result.append(_from_json_raw(stm))
            continue
        elif not result:
            result.append(_from_json_raw(stm))
            continue
        else:
            raise JSONError(E_MALF, stm, stm.pos)


def _from_json_dict(stm):
    next(stm)
    result = {}
    expect_key = 0
    pos = stm.pos
    while True:
        stm.skipspaces()
        c = stm.peek()
        if c == '':
            raise JSONError(E_TRUNC, stm, pos)
        if expect_key and c in('}', ','):
            raise JSONError(E_DKEY, stm, stm.pos)
        if c in('}', ','):
            next(stm)
            if c == '}':
                return result
            expect_key = 1
            continue
        elif c == '"':
            key = _from_json_string(stm)
            stm.skipspaces()
            c = next(stm)
            if c != ':':
                raise JSONError(E_COLON, stm, stm.pos)
            stm.skipspaces()
            val = _from_json_raw(stm)
            result[key] = val
            expect_key = 0
            continue
        raise JSONError(E_MALF, stm, stm.pos)


def _from_json_raw(stm):
    while True:
        stm.skipspaces()
        c = stm.peek()
        if c == '"':
            return _from_json_string(stm)
        elif c == '{':
            return _from_json_dict(stm)
        elif c == '[':
            return _from_json_list(stm)
        elif c == 't':
            return _from_json_fixed(stm, 'true', True, E_BOOL)
        elif c == 'f':
            return _from_json_fixed(stm, 'false', False, E_BOOL)
        elif c == 'n':
            return _from_json_fixed(stm, 'null', None, E_NULL)
        elif c in NUMSTART:
            return _from_json_number(stm)
        raise JSONError(E_MALF, stm, stm.pos)


def from_json(data):
    if not isinstance(data, str):
        raise JSONError(E_BYTES)
    if not data:
        return None
    stm = JSONStream(data)
    return _from_json_raw(stm)


decode = from_json
