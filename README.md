# Estimating the number of Immortal Mutants

The directory for experiments is `microjson/test/`

## User tests
Coverage obtained by user tests:

```
Name                                                                            Stmts   Miss  Cover   Missing
-------------------------------------------------------------------------------------------------------------
microjson.py                                                                      197      8    96%   66, 76-81, 196
```



Mutation results from user tests:

Number of mutants produced: 466
Killed by user tests: 271
Survived: 141
Aborted (did not compile -- subtract from total population): 43
Timeout (add to killed): 11


## Fuzz tests

Coverage obtained by fuzz tests with 10000 tests and maxrecursion=4 in `fuzz.py`

```
Name
Stmts   Miss  Cover   Missing
-------------------------------------------------------------------------------------------------------------
microjson.py
197     37    81%   48, 52, 55, 60-69, 71-81, 88, 90-91, 95, 104, 118, 132, 154, 156, 168, 193, 196, 198
```


Mutation results from fuzz tests:

Number of mutants produced (constant): 466
Killed by user tests: 197
Survived: 231
Aborted (did not compile -- subtract from total population): 33
Timeout (add to killed): 5

Immortals by manual inspection: 28
```
cat microjson/test/plog/mutate.current.log  | grep -- '-survived' | wc -l
```
Mortals by manula inspection on those that survived: 113
```
cat microjson/test/plog/mutate.current.log  | grep -- '+survived' | wc -l
```
