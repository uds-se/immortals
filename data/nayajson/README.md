# Estimating the number of Immortal Mutants for NayaJSON

The directory for experiments is `nayajson/test/`

## User tests

We had `7`  user tests

Coverage obtained by user tests:

```
Name                                                                            Stmts   Miss  Cover   Missing
------------------------------------------------------------------------------------------------------------------------------
nayajson.py                                                                     460     74    84%     77, 83, 119-120, 151, 159-162, 164-167, 169-172, 174-179, 184, 189, 196, 201, 206, 213, 246-247, 283-286, 297, 339-342, 351-353, 368, 370, 380, 390, 396, 398, 402-408, 416, 418, 420, 424, 427-432, 436, 440, 444, 450, 452, 456-460, 465, 468, 470, 474, 478, 489, 499-502
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
