'''
Iterative JSON parser.

Main API:

- ``ijson.parse``: iterator returning parsing events with the object tree context,
  see ``ijson.common.parse`` for docs.

- ``ijson.items``: iterator returning Python objects found under a specified prefix,
  see ``ijson.common.items`` for docs.

Top-level ``ijson`` module exposes method from the pure Python backend. There's
also two other backends using the C library yajl in ``ijson.backends`` that have
the same API and are faster under CPython.
'''
'''
Backend independent higher level interfaces, common exceptions.
'''
import decimal
'''
Pure-python parsing backend.
'''
import decimal
import re
from codecs import getreader
from json.decoder import scanstring



class JSONError(Exception):
    '''
    Base exception for all parsing errors.
    '''
    pass


class IncompleteJSONError(JSONError):
    '''
    Raised when the parser can't read expected data from a stream.
    '''
    pass


def parse(basic_events):
    '''
    An iterator returning parsing events with the information about their location
    with the JSON object tree. Events are tuples ``(prefix, type, value)``.

    Available types and values are:

    ('null', None)
    ('boolean', <True or False>)
    ('number', <int or Decimal>)
    ('string', <unicode>)
    ('map_key', <str>)
    ('start_map', None)
    ('end_map', None)
    ('start_array', None)
    ('end_array', None)

    Prefixes represent the path to the nested elements from the root of the JSON
    document. For example, given this document::

        {
          "array": [1, 2],
          "map": {
            "key": "value"
          }
        }

    the parser would yield events:

      ('', 'start_map', None)
      ('', 'map_key', 'array')
      ('array', 'start_array', None)
      ('array.item', 'number', 1)
      ('array.item', 'number', 2)
      ('array', 'end_array', None)
      ('', 'map_key', 'map')
      ('map', 'start_map', None)
      ('map', 'map_key', 'key')
      ('map.key', 'string', u'value')
      ('map', 'end_map', None)
      ('', 'end_map', None)

    '''
    path = []
    for event, value in basic_events:
        if event == 'map_key':
            prefix = '.'.join(path[:-1])
            path[-1] = value
        elif event == 'start_map':
            prefix = '.'.join(path)
            path.append(None)
        elif event == 'end_map':
            path.pop()
            prefix = '.'.join(path)
        elif event == 'start_array':
            prefix = '.'.join(path)
            path.append('item')
        elif event == 'end_array':
            path.pop()
            prefix = '.'.join(path)
        else: # any scalar value
            prefix = '.'.join(path)

        yield prefix, event, value


class ObjectBuilder(object):
    '''
    Incrementally builds an object from JSON parser events. Events are passed
    into the `event` function that accepts two parameters: event type and
    value. The object being built is available at any time from the `value`
    attribute.

    Example::

        from StringIO import StringIO
        from ijson.parse import basic_parse
        from ijson.utils import ObjectBuilder

        builder = ObjectBuilder()
        f = StringIO('{"key": "value"})
        for event, value in basic_parse(f):
            builder.event(event, value)
        print builder.value

    '''
    def __init__(self):
        def initial_set(value):
            self.value = value
        self.containers = [initial_set]

    def event(self, event, value):
        if event == 'map_key':
            self.key = value
        elif event == 'start_map':
            map = {}
            self.containers[-1](map)
            def setter(value):
                map[self.key] = value
            self.containers.append(setter)
        elif event == 'start_array':
            array = []
            self.containers[-1](array)
            self.containers.append(array.append)
        elif event == 'end_array' or event == 'end_map':
            self.containers.pop()
        else:
            self.containers[-1](value)

def items(prefixed_events, prefix):
    '''
    An iterator returning native Python objects constructed from the events
    under a given prefix.
    '''
    prefixed_events = iter(prefixed_events)
    try:
        while True:
            current, event, value = next(prefixed_events)
            if current == prefix:
                if event in ('start_map', 'start_array'):
                    builder = ObjectBuilder()
                    end_event = event.replace('start', 'end')
                    while (current, event) != (prefix, end_event):
                        builder.event(event, value)
                        current, event, value = next(prefixed_events)
                    yield builder.value
                else:
                    yield value
    except StopIteration:
        pass


def number(str_value):
    '''
    Converts string with a numeric value into an int or a Decimal.
    Used in different backends for consistent number representation.
    '''
    number = decimal.Decimal(str_value)
    if not ('.' in str_value or 'e' in str_value or 'E' in str_value):
        number = int(number)
    return number



#b2s = lambda b: b.decode('utf-8')
bytetype = bytes


BUFSIZE = 16 * 1024
LEXEME_RE = re.compile(r'[a-z0-9eE\.\+-]+|\S')


class UnexpectedSymbol(JSONError):
    def __init__(self, symbol, pos):
        super(UnexpectedSymbol, self).__init__(
            'Unexpected symbol %r at %d' % (symbol, pos)
        )


def Lexer(f, buf_size=BUFSIZE):
    if type(f.read(0)) == bytetype:
        f = getreader('utf-8')(f)
    buf = f.read(buf_size)
    pos = 0
    discarded = 0
    while True:
        match = LEXEME_RE.search(buf, pos)
        if match:
            lexeme = match.group()
            if lexeme == '"':
                pos = match.start()
                start = pos + 1
                while True:
                    try:
                        end = buf.index('"', start)
                        escpos = end - 1
                        while buf[escpos] == '\\':
                            escpos -= 1
                        if (end - escpos) % 2 == 0:
                            start = end + 1
                        else:
                            break
                    except ValueError:
                        data = f.read(buf_size)
                        if not data:
                            raise IncompleteJSONError('Incomplete string lexeme')
                        buf += data
                yield discarded + pos, buf[pos:end + 1]
                pos = end + 1
            else:
                while match.end() == len(buf):
                    data = f.read(buf_size)
                    if not data:
                        break
                    buf += data
                    match = LEXEME_RE.search(buf, pos)
                    lexeme = match.group()
                yield discarded + match.start(), lexeme
                pos = match.end()
        else:
            data = f.read(buf_size)
            if not data:
                break
            discarded += len(buf)
            buf = data
            pos = 0


def parse_value(lexer, symbol=None, pos=0):
    try:
        if symbol is None:
            pos, symbol = next(lexer)
        if symbol == 'null':
            yield ('null', None)
        elif symbol == 'true':
            yield ('boolean', True)
        elif symbol == 'false':
            yield ('boolean', False)
        elif symbol == '[':
            for event in parse_array(lexer):
                yield event
        elif symbol == '{':
            for event in parse_object(lexer):
                yield event
        elif symbol[0] == '"':
            yield ('string', parse_string(symbol))
        else:
            try:
                yield ('number', number(symbol))
            except decimal.InvalidOperation:
                raise UnexpectedSymbol(symbol, pos)
    except StopIteration:
        raise IncompleteJSONError('Incomplete JSON data')


def parse_string(symbol):
    return scanstring(symbol, 1)[0]


def parse_array(lexer):
    yield ('start_array', None)
    try:
        pos, symbol = next(lexer)
        if symbol != ']':
            while True:
                for event in parse_value(lexer, symbol, pos):
                    yield event
                pos, symbol = next(lexer)
                if symbol == ']':
                    break
                if symbol != ',':
                    raise UnexpectedSymbol(symbol, pos)
                pos, symbol = next(lexer)
        yield ('end_array', None)
    except StopIteration:
        raise IncompleteJSONError('Incomplete JSON data')


def parse_object(lexer):
    yield ('start_map', None)
    try:
        pos, symbol = next(lexer)
        if symbol != '}':
            while True:
                if symbol[0] != '"':
                    raise UnexpectedSymbol(symbol, pos)
                yield ('map_key', parse_string(symbol))
                pos, symbol = next(lexer)
                if symbol != ':':
                    raise UnexpectedSymbol(symbol, pos)
                for event in parse_value(lexer, None, pos):
                    yield event
                pos, symbol = next(lexer)
                if symbol == '}':
                    break
                if symbol != ',':
                    raise UnexpectedSymbol(symbol, pos)
                pos, symbol = next(lexer)
        yield ('end_map', None)
    except StopIteration:
        raise IncompleteJSONError('Incomplete JSON data')


def basic_parse(file, buf_size=BUFSIZE):
    '''
    Iterator yielding unprefixed events.

    Parameters:

    - file: a readable file-like object with JSON input
    '''
    lexer = iter(Lexer(file, buf_size))
    for value in parse_value(lexer):
        yield value
    try:
        next(lexer)
    except StopIteration:
        pass
    else:
        raise JSONError('Additional data')

