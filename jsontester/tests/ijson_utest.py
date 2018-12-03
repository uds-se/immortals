# -*- coding:utf-8 -*-
from __future__ import unicode_literals
import unittest
from io import BytesIO, StringIO
from decimal import Decimal
import threading
import timeout_decorator

import ijson


JSON = b'''
{
  "docs": [
    {
      "null": null,
      "boolean": false,
      "true": true,
      "integer": 0,
      "double": 0.5,
      "exponent": 1.0e+2,
      "long": 10000000000,
      "string": "\\u0441\\u0442\\u0440\\u043e\\u043a\\u0430 - \xd1\x82\xd0\xb5\xd1\x81\xd1\x82"
    },
    {
      "meta": [[1], {}]
    },
    {
      "meta": {"key": "value"}
    },
    {
      "meta": null
    }
  ]
}
'''
JSON_EVENTS = [
    ('start_map', None),
        ('map_key', 'docs'),
        ('start_array', None),
            ('start_map', None),
                ('map_key', 'null'),
                ('null', None),
                ('map_key', 'boolean'),
                ('boolean', False),
                ('map_key', 'true'),
                ('boolean', True),
                ('map_key', 'integer'),
                ('number', 0),
                ('map_key', 'double'),
                ('number', Decimal('0.5')),
                ('map_key', 'exponent'),
                ('number', 100),
                ('map_key', 'long'),
                ('number', 10000000000),
                ('map_key', 'string'),
                ('string', 'строка - тест'),
            ('end_map', None),
            ('start_map', None),
                ('map_key', 'meta'),
                ('start_array', None),
                    ('start_array', None),
                        ('number', 1),
                    ('end_array', None),
                    ('start_map', None),
                    ('end_map', None),
                ('end_array', None),
            ('end_map', None),
            ('start_map', None),
                ('map_key', 'meta'),
                ('start_map', None),
                    ('map_key', 'key'),
                    ('string', 'value'),
                ('end_map', None),
            ('end_map', None),
            ('start_map', None),
                ('map_key', 'meta'),
                ('null', None),
            ('end_map', None),
        ('end_array', None),
    ('end_map', None),
]
SCALAR_JSON = b'0'
INVALID_JSONS = [
    b'["key", "value",]',      # trailing comma
    b'["key"  "value"]',       # no comma
    b'{"key": "value",}',      # trailing comma
    b'{"key": "value" "key"}', # no comma
    b'{"key"  "value"}',       # no colon
    b'invalid',                # unknown lexeme
    b'[1, 2] dangling junk'    # dangling junk
]
YAJL1_PASSING_INVALID = INVALID_JSONS[6]
INCOMPLETE_JSONS = [
    b'',
    b'"test',
    b'[',
    b'[1',
    b'[1,',
    b'{',
    b'{"key"',
    b'{"key":',
    b'{"key": "value"',
    b'{"key": "value",',
]
STRINGS_JSON = br'''
{
    "str1": "",
    "str2": "\"",
    "str3": "\\",
    "str4": "\\\\",
    "special\t": "\b\f\n\r\t"
}
'''
NUMBERS_JSON = b'[1, 1.0, 1E2]'
SURROGATE_PAIRS_JSON = b'"\uD83D\uDCA9"'


class Parse(unittest.TestCase):
    '''
    Base class for parsing tests that is used to create test cases for each
    available backends.
    '''
    @timeout_decorator.timeout(10)
    def test_basic_parse(self):
        events = list(ijson.basic_parse(BytesIO(JSON)))
        self.assertEqual(events, JSON_EVENTS)

    @timeout_decorator.timeout(10)
    def test_basic_parse_threaded(self):
        thread = threading.Thread(target=self.test_basic_parse)
        thread.start()
        thread.join()

    @timeout_decorator.timeout(10)
    def test_scalar(self):
        events = list(ijson.basic_parse(BytesIO(SCALAR_JSON)))
        self.assertEqual(events, [('number', 0)])

    @timeout_decorator.timeout(10)
    def test_strings(self):
        events = list(ijson.basic_parse(BytesIO(STRINGS_JSON)))
        strings = [value for event, value in events if event == 'string']
        self.assertEqual(strings, ['', '"', '\\', '\\\\', '\b\f\n\r\t'])
        self.assertTrue(('map_key', 'special\t') in events)

    @timeout_decorator.timeout(10)
    def test_surrogate_pairs(self):
        event = next(ijson.basic_parse(BytesIO(SURROGATE_PAIRS_JSON)))
        parsed_string = event[1]
        self.assertEqual(parsed_string, '💩')

    @timeout_decorator.timeout(10)
    def test_numbers(self):
        events = list(ijson.basic_parse(BytesIO(NUMBERS_JSON)))
        types = [type(value) for event, value in events if event == 'number']
        self.assertEqual(types, [int, Decimal, Decimal])

    @timeout_decorator.timeout(10)
    def test_invalid(self):
        for json in INVALID_JSONS:
            # Yajl1 doesn't complain about additional data after the end
            # of a parsed object. Skipping this test.
            if self.__class__.__name__ == 'YajlParse' and json == YAJL1_PASSING_INVALID:
                continue
            with self.assertRaises(ijson.JSONError) as cm:
                list(ijson.basic_parse(BytesIO(json)))

    @timeout_decorator.timeout(10)
    def test_incomplete(self):
        for json in INCOMPLETE_JSONS:
            with self.assertRaises(ijson.IncompleteJSONError):
                list(ijson.basic_parse(BytesIO(json)))

    @timeout_decorator.timeout(10)
    def test_utf8_split(self):
        buf_size = JSON.index(b'\xd1') + 1
        try:
            events = list(ijson.basic_parse(BytesIO(JSON), buf_size=buf_size))
        except UnicodeDecodeError:
            self.fail('UnicodeDecodeError raised')

    @timeout_decorator.timeout(10)
    def test_lazy(self):
        # shouldn't fail since iterator is not exhausted
        ijson.basic_parse(BytesIO(INVALID_JSONS[0]))
        self.assertTrue(True)

    @timeout_decorator.timeout(10)
    def test_boundary_lexeme(self):
        buf_size = JSON.index(b'false') + 1
        events = list(ijson.basic_parse(BytesIO(JSON), buf_size=buf_size))
        self.assertEqual(events, JSON_EVENTS)

    @timeout_decorator.timeout(10)
    def test_boundary_whitespace(self):
        buf_size = JSON.index(b'   ') + 1
        events = list(ijson.basic_parse(BytesIO(JSON), buf_size=buf_size))
        self.assertEqual(events, JSON_EVENTS)

    #def test_api(self):
    #   self.assertTrue(list(ijson.items(BytesIO(JSON), '')))
    #   self.assertTrue(list(ijson.parse(BytesIO(JSON))))


if __name__ == '__main__':
    unittest.main()
