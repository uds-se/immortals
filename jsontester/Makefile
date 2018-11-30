python=python3
target=microjson
test_target=$(target)_test
pyminifier=pyminifier
autopep8=autopep8

alltargets: targets/microjson.py targets/ijson.py

targets:; mkdir -p targets

targets/%.py: originals/%.py | targets
	$(pyminifier) $< > $@
	mkdir -p targets/formatted
	$(autopep8) $@ > targets/formatted/$(@F)

pickled: $(target).fuzz.pickled

#(1)
%.gfuzz.pickled: bin/gfuzz.py
	PYTHONPATH=lib: $(python) bin/gfuzz.py targets/$*.py

#(2)
tests/microjson_gfuzz.py: microjson.gfuzz.pickled
	PYTHONPATH=targets: $(python) bin/microjson_test_tmpl.py $< > .microjson_gfuzz.py
	mv .microjson_gfuzz.py tests/microjson_gfuzz.py

%.coverage.gfuzz: tests/%_gfuzz.py
	rm -rf .coverage
	PYTHONPATH=targets:tests coverage run $<
	coverage report -m | grep -e '\(Name\|targets\|-----\)' | tee .$*.coverage.gfuzz
	mv .$*.coverage.gfuzz $*.coverage.gfuzz


coverage.test: tests/$(test_target).py
	rm -rf .coverage
	PYTHONPATH=originals coverage run tests/$(test_target).py
	coverage report -m | tee coverage.test

n=0
fuzz:
	for i in mutants/*/; do echo $$i; (export PYTHONPATH=$$i; $(python) microjson_fuzz.py 2>&1 | tee $$i/fuzz-$(n).log & ) ; done

mutate: $(taget)-mutate.log

$(taget)-mutate.log: targets/$(target).py
	TARGET=$(target) PYTHONPATH=targets:tests:lib $(python) ./bin/mut.py --target $(target) --unit-test $(test_target) -e -m | tee $(target)-mutate.log


status: status-$(target).csv

status-$(target).csv: $(taget)-mutate.log
	cat $(target)-mutate.log | sed -e 1,6d| grep -e '\(\[........s\]\|$(target):.*:\)' | paste - - > status-$(target).info
	cat status-$(target).info | sed -e 's/^   - \[# *\([0-9]*\)\] \([A-Z]\{3\}\) \([^:]*:[0-9]*\) *: *.\[.*\]/\1,\2,\3,/g' > status-$(target).csv

m:
	@echo IMPORTANT: verify Customized in the next line
	PYTHONPATH=targets:tests:lib $(python) ./bin/mut.py --help

mutatefuzz:
	TARGET=$(target) PYTHONPATH=.:targets:tests:lib $(python) ./bin/mut.py --target $(target) --unit-test microjson_gfuzz -e -m | tee mutategfuzz.log


update_test: .update_test

.update_test:
	for i in mutants_$(target)/*/; do echo $$i; (export PYTHONPATH=$$i; $(python) tests/$(test_target).py 2>&1 | tee $$i/test.log ) ; done
	touch .update_test

update_testfails:
	for i in mutants_$(target)/*/test.log; do echo $$i; grep -a '\(FAIL:\|ERROR:\)' $$i > $$i.fail; echo $$i.fail; done


x:
	for i in $$(seq 1 274); do echo $$i $$(cat ijsonmutants/$$i/test.log.fail | sed -e 's# (.*)##g' -e 's#ERROR: ##g' -e 's#FAIL: ##g' ) ; done > failed_tests
