python=python3
target=microjson
testsuite=gfuzz
test_target=$(target)_$(testsuite)
pyminifier=pyminifier
autopep8=autopep8

alltargets: targets/microjson.py targets/ijson.py

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

#(2) TEST
test: tests/$(target)_$(testsuite).py
tests/%_gfuzz.py: %.gfuzz.pickled
	PYTHONPATH=targets: $(python) bin/json_test_tmpl.py $< > .$*_gfuzz.py
	mv .$*_gfuzz.py tests/$*_gfuzz.py

tests/%_mfuzz.py: %.mfuzz.pickled
	PYTHONPATH=targets: $(python) bin/json_test_tmpl.py $< > .$*_mfuzz.py
	mv .$*_mfuzz.py tests/$*_mfuzz.py

#(*) TEXEC
texec: $(target).texec.$(testsuite)
%.texec.gfuzz: tests/%_gfuzz.py
	PYTHONPATH=targets:tests python3 $< -v

%.coverage.mfuzz: tests/%_mfuzz.py
	rm -rf .coverage
	PYTHONPATH=targets coverage run $<
	coverage report -m |  grep -e '\(Name\|targets\|-----\)' | tee .$*.coverage.mfuzz
	mv .$*.coverage.mfuzz $*.coverage.mfuzz

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

#(4) MUTATE
mutate: $(target).mutate.$(testsuite).log
%.mutate.gfuzz.log: targets/%.py tests/%_gfuzz.py # %.gfuzz.pickled
	TARGET=$* PYTHONPATH=targets:tests:lib $(python) ./bin/mut.py --target $* --unit-test $*_gfuzz -e -m | tee .$*.mutate.gfuzz.log
	mv .$*.mutate.gfuzz.log $*.mutate.gfuzz.log

#(5) MUTATION-STATUS
mstatus: $(target).mstatus.$(testsuite).csv
%.mstatus.gfuzz.csv: %.mutate.gfuzz.log
	cat $*.mutate.gfuzz.log | sed -e 1,6d| grep -e '\(\[........s\]\|$*:.*:\)' | paste - - > .$*.gfuzz.info
	cat .$*.gfuzz.info | sed -e 's/^   - \[# *\([0-9]*\)\] \([A-Z]\{3\}\) \([^:]*:[0-9]*\) *: *.\[.*\]/\1,\2,\3,/g' > .$*.mstatus.gfuzz.csv
	mv .$*.mstatus.gfuzz.csv $*.mstatus.gfuzz.csv

#(6) TLOG
tlog: $(target).$(testsuite).tlog
n=0
%.gfuzz.tlog: %.mutate.gfuzz.log
	for i in mutants_$*/*/; do echo $$i | tee -a .$*.gfuzz.tlog; (export PYTHONPATH=$$i; ( $(python) tests/$*_gfuzz.py > $$i/.gfuzz-$(n).log 2>&1; mv $$i/.gfuzz-$(n).log $$i/gfuzz-$(n).log ) & ) ; done
	mv .$*.gfuzz.tlog $*.gfuzz.tlog

#(7) TSUMMARIZE
tsummarize: $(target).$(testsuite).tsummarize
%.gfuzz.tsummarize: %.gfuzz.tlog
	for i in mutants_$*/*/gfuzz-$(n).log; do echo $$i; grep -a '\(FAIL:\|ERROR:\)' $$i > $$i.fail; echo $$i.fail; done

clean:
	rm *$(testsuite)*
#-------------------
m:
	@echo IMPORTANT: verify Customized in the next line
	PYTHONPATH=targets:tests:lib $(python) ./bin/mut.py --help

update_test: .update_test

.update_test:
	for i in mutants_$(target)/*/; do echo $$i; (export PYTHONPATH=$$i; $(python) tests/$(test_target).py 2>&1 | tee $$i/test.log ) ; done
	touch .update_test

update_testfails:
	for i in mutants_$(target)/*/test.log; do echo $$i; grep -a '\(FAIL:\|ERROR:\)' $$i > $$i.fail; echo $$i.fail; done


x:
	for i in $$(seq 1 274); do echo $$i $$(cat ijsonmutants/$$i/test.log.fail | sed -e 's# (.*)##g' -e 's#ERROR: ##g' -e 's#FAIL: ##g' ) ; done > failed_tests
