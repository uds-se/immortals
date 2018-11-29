lines = open('stestsxmutants.txt').readlines()

for line in lines:
    mutant, *tests = line.strip().split()
    tests = set([int(t.replace('test_str_','').replace('test_err_', '')) for t in tests])
    my_tests = ['1' if i in tests else '0' for i in range(1,18)]
    print("%s,%s" % (mutant, ','.join(my_tests)))
