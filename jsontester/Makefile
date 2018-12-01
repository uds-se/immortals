# To find dependencies of a target, use `make $target --debug=basic -n
python=python3
target=microjson
testsuite=gfuzz
test_target=$(target)_$(testsuite)
pyminifier=pyminifier
autopep8=autopep8

all: \
	microjson.gfuzz.tlog \
	microjson.mfuzz.tlog \
	microjson.rfuzz.tlog \
	microjson.utest.tlog \
	ijson.gfuzz.tlog \
	ijson.mfuzz.tlog \
	ijson.rfuzz.tlog \
	ijson.utest.tlog \
	nayajson.gfuzz.tlog \
	nayajson.mfuzz.tlog \
	nayajson.rfuzz.tlog \
	nayajson.utest.tlog

alltargets: targets/microjson.py targets/ijson.py targets/nayajson.py

targets:; mkdir -p targets

targets/%.py: originals/%.py | targets
	$(pyminifier) $< > $@
	mkdir -p targets/formatted
	$(autopep8) $@ > targets/formatted/$(@F)

#(1) PICKLE
pickled: $(target).$(testsuite).pickled
%.gfuzz.pickled: bin/gfuzz.py
	PYTHONPATH=lib: $(python) bin/gfuzz.py targets/$*.py

%.mfuzz.pickled: bin/mfuzz.py
	PYTHONPATH=lib: $(python) bin/mfuzz.py targets/$*.py

%.rfuzz.pickled: bin/rfuzz.py
	PYTHONPATH=lib: $(python) bin/rfuzz.py targets/$*.py

#(2) TEST
test: tests/$(target)_$(testsuite).py
tests/%_gfuzz.py: %.gfuzz.pickled
	PYTHONPATH=targets: $(python) bin/json_test_tmpl.py $< > .$*_gfuzz.py
	mv .$*_gfuzz.py tests/$*_gfuzz.py

tests/%_mfuzz.py: %.mfuzz.pickled
	PYTHONPATH=targets: $(python) bin/json_test_tmpl.py $< > .$*_mfuzz.py
	mv .$*_mfuzz.py tests/$*_mfuzz.py

tests/%_rfuzz.py: %.rfuzz.pickled
	PYTHONPATH=targets: $(python) bin/json_test_tmpl.py $< > .$*_rfuzz.py
	mv .$*_rfuzz.py tests/$*_rfuzz.py


#(*) TEXEC
texec: $(target).texec.$(testsuite)
%.texec.gfuzz: tests/%_gfuzz.py
	PYTHONPATH=targets:tests python3 $< -v

texec: $(target).texec.$(testsuite)
%.texec.mfuzz: tests/%_mfuzz.py
	PYTHONPATH=targets:tests python3 $< -v

texec: $(target).texec.$(testsuite)
%.texec.rfuzz: tests/%_rfuzz.py
	PYTHONPATH=targets:tests python3 $< -v

texec: $(target).texec.$(testsuite)
%.texec.utest: tests/%_test.py
	PYTHONPATH=targets:tests python3 $< -v


#(3) COVERAGE
coverage: $(target).coverage.$(testsuite)
%.coverage.gfuzz: tests/%_gfuzz.py
	rm -rf .coverage
	PYTHONPATH=targets:tests coverage run $<
	coverage report -m | grep -e '\(Name\|targets\|-----\)' | tee .$*.coverage.gfuzz
	mv .$*.coverage.gfuzz $*.coverage.gfuzz

%.coverage.mfuzz: tests/%_mfuzz.py
	rm -rf .coverage
	PYTHONPATH=targets coverage run $<
	coverage report -m |  grep -e '\(Name\|targets\|-----\)' | tee .$*.coverage.mfuzz
	mv .$*.coverage.mfuzz $*.coverage.mfuzz

%.coverage.rfuzz: tests/%_rfuzz.py
	rm -rf .coverage
	PYTHONPATH=targets coverage run $<
	coverage report -m |  grep -e '\(Name\|targets\|-----\)' | tee .$*.coverage.rfuzz
	mv .$*.coverage.rfuzz $*.coverage.rfuzz

%.coverage.utest: tests/%_test.py targets/nayajson.py
	rm -rf .coverage
	PYTHONPATH=targets coverage run $<
	coverage report -m |  grep -e '\(Name\|targets\|-----\)' | tee .$*.coverage.utest
	mv .$*.coverage.utest $*.coverage.utest

#(4) MUTATE
mutate: $(target).mutate.$(testsuite).log
%.mutate.gfuzz.log: targets/%.py tests/%_gfuzz.py # %.gfuzz.pickled
	TARGET=$* PYTHONPATH=targets:tests:lib $(python) ./bin/mut.py --target $* --unit-test $*_gfuzz -e -m | tee .$*.mutate.gfuzz.log
	mv .$*.mutate.gfuzz.log $*.mutate.gfuzz.log

%.mutate.mfuzz.log: targets/%.py tests/%_mfuzz.py # %.mfuzz.pickled
	TARGET=$* PYTHONPATH=targets:tests:lib $(python) ./bin/mut.py --target $* --unit-test $*_mfuzz -e -m | tee .$*.mutate.mfuzz.log
	mv .$*.mutate.mfuzz.log $*.mutate.mfuzz.log

%.mutate.rfuzz.log: targets/%.py tests/%_mfuzz.py # %.rfuzz.pickled
	TARGET=$* PYTHONPATH=targets:tests:lib $(python) ./bin/mut.py --target $* --unit-test $*_rfuzz -e -m | tee .$*.mutate.rfuzz.log
	mv .$*.mutate.rfuzz.log $*.mutate.rfuzz.log

%.mutate.utest.log: targets/%.py tests/%_mfuzz.py # %.test.pickled
	TARGET=$* PYTHONPATH=targets:tests:lib $(python) ./bin/mut.py --target $* --unit-test $*_test -e -m | tee .$*.mutate.utest.log
	mv .$*.mutate.utest.log $*.mutate.utest.log

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
		(export PYTHONPATH=$$i; ( $(python) tests/$*_test.py > $$i/.utest-$(n).log 2>&1; mv $$i/.utest-$(n).log $$i/utest-$(n).log ) & ) ; done
	mv .$*.utest.tlog $*.utest.tlog


#(7) TSUMMARIZE
tsummarize: $(target).$(testsuite).tsummarize
%.gfuzz.tsummarize: %.gfuzz.tlog
	for i in mutants_$*/*/gfuzz-$(n).log; do \
		echo $$i; grep -a '\(FAIL:\|ERROR:\)' $$i > $$i.fail; echo $$i.fail; done
	touch $*.gfuzz.tsummarize

%.mfuzz.tsummarize: %.mfuzz.tlog
	for i in mutants_$*/*/mfuzz-$(n).log; do \
		echo $$i; grep -a '\(FAIL:\|ERROR:\)' $$i > $$i.fail; echo $$i.fail; done
	touch $*.mfuzz.tsummarize

%.rfuzz.tsummarize: %.rfuzz.tlog
	for i in mutants_$*/*/rfuzz-$(n).log; do \
		echo $$i; grep -a '\(FAIL:\|ERROR:\)' $$i > $$i.fail; echo $$i.fail; done
	touch $*.rfuzz.tsummarize

%.utest.tsummarize: %.utest.tlog
	for i in mutants_$*/*/utest-$(n).log; do \
		echo $$i; grep -a '\(FAIL:\|ERROR:\)' $$i > $$i.fail; echo $$i.fail; done
	touch $*.utest.tsummarize

#(8) MATRIX
matrix:	$(target).$(testsuite).matrix
%.gfuzz.matrix: %.gfuzz.tsummarize .%.mcount
	for i in $$(seq 1 $$(cat .$(target).mcount)); do echo $$i $$(cat mutants_$*/$$i/gfuzz-$(n).log.fail \
		| sed -e 's# (.*)##g' -e 's#ERROR: ##g' -e 's#FAIL: ##g' ) ; done > .$(target).gfuzz.matrix
	mv .$(target).gfuzz.matrix $(target).gfuzz.matrix

%.mfuzz.matrix: %.mfuzz.tsummarize .%.mcount
	for i in $$(seq 1 $$(cat .$(target).mcount)); do echo $$i $$(cat mutants_$*/$$i/mfuzz-$(n).log.fail \
		| sed -e 's# (.*)##g' -e 's#ERROR: ##g' -e 's#FAIL: ##g' ) ; done > .$(target).mfuzz.matrix
	mv .$(target).mfuzz.matrix $(target).mfuzz.matrix

%.rfuzz.matrix: %.rfuzz.tsummarize .%.mcount
	for i in $$(seq 1 $$(cat .$(target).mcount)); do echo $$i $$(cat mutants_$*/$$i/rfuzz-$(n).log.fail \
		| sed -e 's# (.*)##g' -e 's#ERROR: ##g' -e 's#FAIL: ##g' ) ; done > .$(target).rfuzz.matrix
	mv .$(target).rfuzz.matrix $(target).rfuzz.matrix

%.utest.matrix: %.utest.tsummarize .%.mcount
	for i in $$(seq 1 $$(cat .$(target).mcount)); do echo $$i $$(cat mutants_$*/$$i/utest-$(n).log.fail \
		| sed -e 's# (.*)##g' -e 's#ERROR: ##g' -e 's#FAIL: ##g' ) ; done > .$(target).utest.matrix
	mv .$(target).utest.matrix $(target).utest.matrix

.%.mcount: %.mutate.$(testsuite).log
	ls mutants_$*/ | sort -rn | head -1 > .$*.mcount

# CLEAN

clean:
	rm *$(testsuite)*


#-------------------
m:
	@echo IMPORTANT: verify Customized in the next line
	PYTHONPATH=targets:tests:lib $(python) ./bin/mut.py --help


