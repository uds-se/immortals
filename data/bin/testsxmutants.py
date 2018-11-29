Tests = [ #ijson
        'test_invalid',
        'test_utf8_split',
        'test_scalar',
        'test_surrogate_pairs',
        'test_lazy',
        'test_boundary_whitespace',
        'test_api',
        'test_incomplete',
        'test_basic_parse',
        'test_numbers',
        'test_strings',
        'test_boundary_lexeme'
        ]
Tests_ = [ # microjson
        'test_dict',
        'test_list',
        'test_string',
        'test_integer',
        'test_floats',
        'test_null_and_bool',
        'test_malformed'
        ]

lines = open('testsxmutants.txt').readlines()

for line in lines:
    mutant, *tests = line.strip().split()
    tests = set(tests)
    my_tests = ['1' if i in tests else '0' for i in Tests]
    #tests = set([int(t.replace('test_str_','').replace('test_err_', '')) for t in tests])
    #my_tests = ['1' if i in tests else '0' for i in range(1,2377)]
    print("%s,%s" % (mutant, ','.join(my_tests)))
