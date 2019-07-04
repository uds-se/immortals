# To find dependencies of a target, use `make $target --debug=basic -n
python=python3
target=microjson
testsuite=gfuzz
test_target=$(target)_$(testsuite)
pyminifier=pyminifier
autopep8=autopep8
GFUZZ_MAX=1000

.precious: \
	$(target).utest.tsummarize \
	$(target).rfuzz.tsummarize \
	tests/$(target)_mfuzz.py \
	.$(target).mcount \
	$(target).mutate.mfuzz.log \
	$(target).mfuzz.tsummarize \
	$(target).mutate.rfuzz.log \
	$(target).mfuzz.pickled \
	$(target).mutate.utest.log

.SECONDARY:

all:
	$(MAKE) allmatrix target=microjson && touch .microjson.done
	$(MAKE) allmatrix target=simplejson && touch .simplejson.done
	$(MAKE) allmatrix target=ijson && touch .ijson.done
	$(MAKE) allmatrix target=nayajson && touch .nayajson.done

all-gfuzz: coverage-gfuzz
	$(MAKE) microjson.gfuzz.matrix
	$(MAKE) simplejson.gfuzz.matrix
	$(MAKE) ijson.gfuzz.matrix
	$(MAKE) nayajson.gfuzz.matrix

coverage-gfuzz:
	$(MAKE) microjson.coverage.gfuzz
	$(MAKE) simplejson.coverage.gfuzz
	$(MAKE) ijson.coverage.gfuzz
	$(MAKE) nayajson.coverage.gfuzz


mua: \
	$(target).utest.tlog \
	$(target).gfuzz.tlog \
	$(target).mfuzz.tlog \
	$(target).rfuzz.tlog

allmatrix: \
	$(target).utest.matrix \
	$(target).gfuzz.matrix \
	$(target).mfuzz.matrix \
	$(target).rfuzz.matrix

cleanall:
	$(MAKE) clean-microjson
	$(MAKE) clean-nayajson
	$(MAKE) clean-ijson
	$(MAKE) clean-simplejson

alltargets: targets/microjson.py targets/ijson.py targets/nayajson.py targets/simplejson.py

targets:; mkdir -p targets

targets/%.py: originals/%.py | targets
	$(pyminifier) $< > $@
	mkdir -p targets/formatted
	$(autopep8) $@ > targets/formatted/$(@F)


#(1) PICKLE
# So, what we want to do here is to generate the first set of inputs, along
# with their outputs on the original target. This set of input/output pairs
# are later used during mutation analysis.
pickled: $(target).$(testsuite).pickled
%.gfuzz.pickled: bin/gfuzz.py targets/%.py
	PYTHONPATH=lib: GFUZZ_MAX=$(GFUZZ_MAX) $(python) bin/gfuzz.py targets/$*.py

%.mfuzz.pickled: bin/mfuzz.py targets/%.py
	PYTHONPATH=lib: $(python) bin/mfuzz.py targets/$*.py

%.rfuzz.pickled: bin/rfuzz.py targets/%.py
	PYTHONPATH=lib: $(python) bin/rfuzz.py targets/$*.py

#(2) TESTGEN
# Here, we generate the test suite. The reason for generating a test suite
# rather than directly fuzzing is that we want to add a timer for each test
# case, and also, our mutation analyzer needs test suites.
testgen: tests/$(target)_$(testsuite).py
tests/%_gfuzz.py: %.gfuzz.pickled
	PYTHONPATH=targets: $(python) bin/json_test_tmpl.py $< $* > .$*_gfuzz.py
	mv .$*_gfuzz.py tests/$*_gfuzz.py

tests/%_mfuzz.py: %.mfuzz.pickled
	PYTHONPATH=targets: $(python) bin/json_test_tmpl.py $< $* > .$*_mfuzz.py
	mv .$*_mfuzz.py tests/$*_mfuzz.py

tests/%_rfuzz.py: %.rfuzz.pickled
	PYTHONPATH=targets: $(python) bin/json_test_tmpl.py $< $* > .$*_rfuzz.py
	mv .$*_rfuzz.py tests/$*_rfuzz.py

# no utest because tests/$(target)_utest.py exists

#(*) TESTEXEC
# Verification step. This is not a dependency for any other step. All that
# we are doing here is to run the generated tests.
texec: $(target).texec.$(testsuite)
%.texec.gfuzz: tests/%_gfuzz.py
	PYTHONPATH=targets:tests python3 $< -v

%.texec.mfuzz: tests/%_mfuzz.py
	PYTHONPATH=targets:tests python3 $< -v

%.texec.rfuzz: tests/%_rfuzz.py
	PYTHONPATH=targets:tests python3 $< -v

%.texec.utest: tests/%_utest.py
	PYTHONPATH=targets:tests python3 $< -v

%.texec.ctest: tests/%_ctest.py
	PYTHONPATH=targets:tests python3 $< -v

#(3) COVERAGE
coverage: $(target).coverage.$(testsuite)
%.coverage.gfuzz: tests/%_gfuzz.py %.gfuzz.pickled
	rm -rf $*.coverage.gfuzz
	COVERAGE_FILE=$*.coverage.gfuzz PYTHONPATH=targets:tests coverage run $<
	COVERAGE_FILE=$*.coverage.gfuzz coverage report -m | grep -e '\(Name\|targets\|-----\)' | tee .$*.coverage.gfuzz
	mv .$*.coverage.gfuzz $*.coverage.gfuzz

%.coverage.mfuzz: tests/%_mfuzz.py %.mfuzz.pickled
	rm -rf $*.coverage.mfuzz
	COVERAGE_FILE=$*.coverage.mfuzz PYTHONPATH=targets:tests coverage run $<
	COVERAGE_FILE=$*.coverage.mfuzz coverage report -m |  grep -e '\(Name\|targets\|-----\)' | tee .$*.coverage.mfuzz
	mv .$*.coverage.mfuzz $*.coverage.mfuzz

%.coverage.rfuzz: tests/%_rfuzz.py %.rfuzz.pickled
	rm -rf $*.coverage.rfuzz
	COVERAGE_FILE=$*.coverage.rfuzz PYTHONPATH=targets:tests coverage run $<
	COVERAGE_FILE=$*.coverage.rfuzz coverage report -m |  grep -e '\(Name\|targets\|-----\)' | tee .$*.coverage.rfuzz
	mv .$*.coverage.rfuzz $*.coverage.rfuzz

%.coverage.utest: tests/%_utest.py targets/%.py
	rm -rf $*.coverage.utest
	COVERAGE_FILE=$*.coverage.utest PYTHONPATH=targets:tests coverage run $<
	COVERAGE_FILE=$*.coverage.utest coverage report -m |  grep -e '\(Name\|targets\|-----\)' | tee .$*.coverage.utest
	mv .$*.coverage.utest $*.coverage.utest

%.coverage.ctest: tests/%_ctest.py targets/%.py
	rm -rf $*.coverage.ctest
	COVERAGE_FILE=$*.coverage.ctest PYTHONPATH=targets:tests coverage run $<
	COVERAGE_FILE=$*.coverage.ctest coverage report -m |  grep -e '\(Name\|targets\|-----\)' | tee .$*.coverage.ctest
	mv .$*.coverage.ctest $*.coverage.ctest


#(4) MUTATE
mutate: $(target).mutate.$(testsuite).log
%.mutate.gfuzz.log: targets/%.py tests/%_gfuzz.py %.gfuzz.pickled
	TARGET=$* PYTHONPATH=targets:tests:lib $(python) ./bin/mut.py --target $* --unit-test $*_gfuzz -e -m | tee .$*.mutate.gfuzz.log
	mv .$*.mutate.gfuzz.log $*.mutate.gfuzz.log

%.mutate.mfuzz.log: targets/%.py tests/%_mfuzz.py %.mfuzz.pickled
	TARGET=$* PYTHONPATH=targets:tests:lib $(python) ./bin/mut.py --target $* --unit-test $*_mfuzz -e -m | tee .$*.mutate.mfuzz.log
	mv .$*.mutate.mfuzz.log $*.mutate.mfuzz.log

%.mutate.rfuzz.log: targets/%.py tests/%_rfuzz.py %.rfuzz.pickled
	TARGET=$* PYTHONPATH=targets:tests:lib $(python) ./bin/mut.py --target $* --unit-test $*_rfuzz -e -m | tee .$*.mutate.rfuzz.log
	mv .$*.mutate.rfuzz.log $*.mutate.rfuzz.log

%.mutate.utest.log: targets/%.py tests/%_utest.py
	TARGET=$* PYTHONPATH=targets:tests:lib $(python) ./bin/mut.py --target $* --unit-test $*_utest -e -m | tee .$*.mutate.utest.log
	mv .$*.mutate.utest.log $*.mutate.utest.log

%.mutate.ctest.log: targets/%.py tests/%_ctest.py
	TARGET=$* PYTHONPATH=targets:tests:lib $(python) ./bin/mut.py --target $* --unit-test $*_ctest -e -m | tee .$*.mutate.ctest.log
	mv .$*.mutate.ctest.log $*.mutate.ctest.log

#(5) MUTATION-STATUS
mstatus: $(target).mstatus.$(testsuite).csv
%.mstatus.gfuzz.csv: %.mutate.gfuzz.log
	cat $*.mutate.gfuzz.log | sed -e 1,6d| grep -e '\(\[........s\]\|$*:.*:\)' | paste - - > .$*.gfuzz.info
	cat .$*.gfuzz.info | sed -e 's/^   - \[# *\([0-9]*\)\] \([A-Z]\{3\}\) \([^:]*:[0-9]*\) *: *.\[.*\]/\1,\2,\3,/g' > .$*.mstatus.gfuzz.csv
	mv .$*.mstatus.gfuzz.csv $*.mstatus.gfuzz.csv

%.mstatus.mfuzz.csv: %.mutate.mfuzz.log
	cat $*.mutate.mfuzz.log | sed -e 1,6d| grep -e '\(\[........s\]\|$*:.*:\)' | paste - - > .$*.mfuzz.info
	cat .$*.mfuzz.info | sed -e 's/^   - \[# *\([0-9]*\)\] \([A-Z]\{3\}\) \([^:]*:[0-9]*\) *: *.\[.*\]/\1,\2,\3,/g' > .$*.mstatus.mfuzz.csv
	mv .$*.mstatus.mfuzz.csv $*.mstatus.mfuzz.csv

%.mstatus.rfuzz.csv: %.mutate.rfuzz.log
	cat $*.mutate.rfuzz.log | sed -e 1,6d| grep -e '\(\[........s\]\|$*:.*:\)' | paste - - > .$*.rfuzz.info
	cat .$*.rfuzz.info | sed -e 's/^   - \[# *\([0-9]*\)\] \([A-Z]\{3\}\) \([^:]*:[0-9]*\) *: *.\[.*\]/\1,\2,\3,/g' > .$*.mstatus.rfuzz.csv
	mv .$*.mstatus.rfuzz.csv $*.mstatus.rfuzz.csv

%.mstatus.utest.csv: %.mutate.utest.log
	cat $*.mutate.utest.log | sed -e 1,6d| grep -e '\(\[........s\]\|$*:.*:\)' | paste - - > .$*.utest.info
	cat .$*.utest.info | sed -e 's/^   - \[# *\([0-9]*\)\] \([A-Z]\{3\}\) \([^:]*:[0-9]*\) *: *.\[.*\]/\1,\2,\3,/g' > .$*.mstatus.utest.csv
	mv .$*.mstatus.utest.csv $*.mstatus.utest.csv

%.mstatus.ctest.csv: %.mutate.ctest.log
	cat $*.mutate.ctest.log | sed -e 1,6d| grep -e '\(\[........s\]\|$*:.*:\)' | paste - - > .$*.ctest.info
	cat .$*.ctest.info | sed -e 's/^   - \[# *\([0-9]*\)\] \([A-Z]\{3\}\) \([^:]*:[0-9]*\) *: *.\[.*\]/\1,\2,\3,/g' > .$*.mstatus.ctest.csv
	mv .$*.mstatus.ctest.csv $*.mstatus.ctest.csv

#(6) TLOG
tlog: $(target).$(testsuite).tlog
n=0
%.gfuzz.tlog: %.mutate.gfuzz.log
	for i in mutants_$*/*/; do echo $$i | tee -a .$*.gfuzz.tlog; \
		(export PYTHONPATH=$$i; ( $(python) tests/$*_gfuzz.py > $$i/.gfuzz-$(n).log 2>&1; mv $$i/.gfuzz-$(n).log $$i/gfuzz-$(n).log ) & ) ; done
	mv .$*.gfuzz.tlog $*.gfuzz.tlog

%.mfuzz.tlog: %.mutate.mfuzz.log
	for i in mutants_$*/*/; do echo $$i | tee -a .$*.mfuzz.tlog; \
		(export PYTHONPATH=$$i; ( $(python) tests/$*_mfuzz.py > $$i/.mfuzz-$(n).log 2>&1; mv $$i/.mfuzz-$(n).log $$i/mfuzz-$(n).log ) & ) ; done
	mv .$*.mfuzz.tlog $*.mfuzz.tlog

%.rfuzz.tlog: %.mutate.rfuzz.log
	for i in mutants_$*/*/; do echo $$i | tee -a .$*.rfuzz.tlog; \
		(export PYTHONPATH=$$i; ( $(python) tests/$*_rfuzz.py > $$i/.rfuzz-$(n).log 2>&1; mv $$i/.rfuzz-$(n).log $$i/rfuzz-$(n).log ) & ) ; done
	mv .$*.rfuzz.tlog $*.rfuzz.tlog

%.utest.tlog: %.mutate.utest.log
	for i in mutants_$*/*/; do echo $$i | tee -a .$*.utest.tlog; \
		(export PYTHONPATH=$$i; ( $(python) tests/$*_utest.py > $$i/.utest-$(n).log 2>&1; mv $$i/.utest-$(n).log $$i/utest-$(n).log ) & ) ; done
	mv .$*.utest.tlog $*.utest.tlog

%.ctest.tlog: %.mutate.ctest.log
	for i in mutants_$*/*/; do echo $$i | tee -a .$*.ctest.tlog; \
		(export PYTHONPATH=$$i; ( $(python) tests/$*_ctest.py > $$i/.ctest-$(n).log 2>&1; mv $$i/.ctest-$(n).log $$i/ctest-$(n).log ) & ) ; done
	mv .$*.ctest.tlog $*.ctest.tlog

.tlog.%.done:
	./bin/wait.py $* $(GFUZZ_MAX)
	touch .tlog.$*.done

#(7) TSUMMARIZE
tsummarize: $(target).$(testsuite).tsummarize
%.gfuzz.tsummarize: %.gfuzz.tlog .tlog.%.done
	for i in mutants_$*/*/gfuzz-$(n).log; do \
		echo $$i; grep -a '\(FAIL:\|ERROR:\)' $$i > $$i.fail; echo $$i.fail; done
	touch $*.gfuzz.tsummarize

%.mfuzz.tsummarize: %.mfuzz.tlog .tlog.%.done
	for i in mutants_$*/*/mfuzz-$(n).log; do \
		echo $$i; grep -a '\(FAIL:\|ERROR:\)' $$i > $$i.fail; echo $$i.fail; done
	touch $*.mfuzz.tsummarize

%.rfuzz.tsummarize: %.rfuzz.tlog .tlog.%.done
	for i in mutants_$*/*/rfuzz-$(n).log; do \
		echo $$i; grep -a '\(FAIL:\|ERROR:\)' $$i > $$i.fail; echo $$i.fail; done
	touch $*.rfuzz.tsummarize

%.utest.tsummarize: %.utest.tlog .tlog.%.done
	for i in mutants_$*/*/utest-$(n).log; do \
		echo $$i; grep -a '\(FAIL:\|ERROR:\)' $$i > $$i.fail; echo $$i.fail; done
	touch $*.utest.tsummarize

%.ctest.tsummarize: %.ctest.tlog .tlog.%.done
	for i in mutants_$*/*/ctest-$(n).log; do \
		echo $$i; grep -a '\(FAIL:\|ERROR:\)' $$i > $$i.fail; echo $$i.fail; done
	touch $*.ctest.tsummarize

#(8) PREMATRIX
prematrix:	$(target).$(testsuite).prematrix
%.gfuzz.prematrix: %.gfuzz.tsummarize .%.mcount
	for i in $$(seq 1 $$(cat .$*.mcount)); do echo $$i $$(cat mutants_$*/$$i/gfuzz-$(n).log.fail \
		| sed -e 's# (.*)##g' -e 's#ERROR: ##g' -e 's#FAIL: ##g' ) ; done > .$*.gfuzz.prematrix
	mv .$*.gfuzz.prematrix $*.gfuzz.prematrix

%.mfuzz.prematrix: %.mfuzz.tsummarize .%.mcount
	for i in $$(seq 1 $$(cat .$*.mcount)); do echo $$i $$(cat mutants_$*/$$i/mfuzz-$(n).log.fail \
		| sed -e 's# (.*)##g' -e 's#ERROR: ##g' -e 's#FAIL: ##g' ) ; done > .$*.mfuzz.prematrix
	mv .$*.mfuzz.prematrix $*.mfuzz.prematrix

%.rfuzz.prematrix: %.rfuzz.tsummarize .%.mcount
	for i in $$(seq 1 $$(cat .$*.mcount)); do echo $$i $$(cat mutants_$*/$$i/rfuzz-$(n).log.fail \
		| sed -e 's# (.*)##g' -e 's#ERROR: ##g' -e 's#FAIL: ##g' ) ; done > .$*.rfuzz.prematrix
	mv .$*.rfuzz.prematrix $*.rfuzz.prematrix

%.utest.prematrix: %.utest.tsummarize .%.mcount
	for i in $$(seq 1 $$(cat .$*.mcount)); do echo $$i $$(cat mutants_$*/$$i/utest-$(n).log.fail \
		| sed -e 's# (.*)##g' -e 's#ERROR: ##g' -e 's#FAIL: ##g' ) ; done > .$*.utest.prematrix
	mv .$*.utest.prematrix $*.utest.prematrix

%.ctest.prematrix: %.ctest.tsummarize .%.mcount
	for i in $$(seq 1 $$(cat .$*.mcount)); do echo $$i $$(cat mutants_$*/$$i/ctest-$(n).log.fail \
		| sed -e 's# (.*)##g' -e 's#ERROR: ##g' -e 's#FAIL: ##g' ) ; done > .$*.ctest.prematrix
	mv .$*.ctest.prematrix $*.ctest.prematrix

.%.mcount: %.mutate.$(testsuite).log
	ls mutants_$*/ | sort -rn | head -1 > .$*.mcount

# PROCESS

microjson.%.lst: tests/microjson_%.py
	./bin/extract_tests.sh $< > .microjson.$*.lst
	mv .microjson.$*.lst microjson.$*.lst

ijson.%.lst: tests/ijson_%.py
	./bin/extract_tests.sh $< > .ijson.$*.lst
	mv .ijson.$*.lst ijson.$*.lst

nayajson.%.lst: tests/nayajson_%.py
	./bin/extract_tests.sh $< > .nayajson.$*.lst
	mv .nayajson.$*.lst nayajson.$*.lst

simplejson.%.lst: tests/simplejson_%.py
	./bin/extract_tests.sh $< > .simplejson.$*.lst
	mv .simplejson.$*.lst simplejson.$*.lst

matrix:	$(target).$(testsuite).matrix
%.gfuzz.matrix: %.gfuzz.prematrix %.gfuzz.lst
	python3 ./bin/tomatrix.py $*.gfuzz.lst $*.gfuzz.prematrix > .$*.gfuzz.matrix 
	mv .$*.gfuzz.matrix $*.gfuzz.matrix

%.mfuzz.matrix: %.mfuzz.prematrix %.mfuzz.lst
	python3 ./bin/tomatrix.py $*.mfuzz.lst $*.mfuzz.prematrix > .$*.mfuzz.matrix 
	mv .$*.mfuzz.matrix $*.mfuzz.matrix

%.rfuzz.matrix: %.rfuzz.prematrix %.rfuzz.lst
	python3 ./bin/tomatrix.py $*.rfuzz.lst $*.rfuzz.prematrix > .$*.rfuzz.matrix 
	mv .$*.rfuzz.matrix $*.rfuzz.matrix

%.utest.matrix: %.utest.prematrix %.utest.lst
	python3 ./bin/tomatrix.py $*.utest.lst $*.utest.prematrix > .$*.utest.matrix 
	mv .$*.utest.matrix $*.utest.matrix

%.ctest.matrix: %.ctest.prematrix %.ctest.lst
	python3 ./bin/tomatrix.py $*.ctest.lst $*.ctest.prematrix > .$*.ctest.matrix 
	mv .$*.ctest.matrix $*.ctest.matrix

#
# CLEAN
clean-%:
	rm -rf *.$*.*  .*$*.*



#-------------------
m:
	@echo IMPORTANT: verify Customized in the next line
	PYTHONPATH=targets:tests:lib $(python) ./bin/mut.py --help


