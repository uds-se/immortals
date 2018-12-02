# Estimating the number of Immortal Mutants for NayaJSON

The directory for experiments is `nayajson/test/`

## User tests

We had `7`  user tests

Coverage obtained by user tests:

```
Name                                                                            Stmts   Miss  Cover   Missing
-------------------------------------------------------------------------------------------------------------
nayajson.py                                                                      197      8    96%   66, 76-81, 196
```

Mutation results from user tests:

```
Number of mutants produced: 1102
Killed by user tests: 796
Survived: 289
Aborted (did not compile -- subtract from total population): 14
Timeout (add to killed): 3
```

Immortals by manual inspection: 4
```
cat nayajson/test/plog/mutate.current.log  | grep -- '-survived' | wc -l
```
Mortals by manual inspection on those that survived: 283
```
cat nayajson/test/plog/mutate.current.log  | grep -- '+survived' | wc -l
```

## Data Files

This directory contains three matrix files. They are of this format: mutants as
rows and tests as columns. A test that killed a mutant is marked as 1 and
that did not kill is marked as 0
