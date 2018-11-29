targets/%.py: originals/%.py
	/usr/local/bin/pyminifier $< > $@
	/usr/local/bin/autopep8 $@ > targets/formatted/$(@F)

fuzz.pickled: fuzz.py
	$(python) fuzz.py

microjson_fuzz.py: fuzz.pickled
	$(python) microjson_fuzz_tmpl.py > microjson_fuzz.py

coverage.fuzz: microjson_fuzz.py
	rm -rf .coverage
	coverage run microjson_fuzz.py
	coverage report -m | tee coverage.fuzz


coverage.test: $(test_target).py
	rm -rf .coverage
	coverage run $(test_target).py
	coverage report -m | tee coverage.test

n=0
fuzz:
	for i in mutants/*/; do echo $$i; (export PYTHONPATH=$$i; $(python) microjson_fuzz.py 2>&1 | tee $$i/fuzz-$(n).log & ) ; done

target=microjson
test_target=$(target)_test

mutate:
	TARGET=$(target) PYTHONPATH=targets:tests:lib $(python) ./bin/mut.py --target $(target) --unit-test $(test_target) -e -m | tee $(target)-mutate.log

m:
	@echo IMPORTANT: verify Customized in the next line
	PYTHONPATH=targets:tests:lib $(python) ./bin/mut.py --help

mutatefuzz:
	$(python) /usr/local/bin/mut.py --target targets/$(target) --unit-test microjson_fuzz -e -m | tee mutatefuzz.log


update_test: .update_test

.update_test:
	for i in mutants/*/; do echo $$i; (export PYTHONPATH=$$i; $(python) tests/$(test_target).py 2>&1 | tee $$i/test.log ) ; done
	touch .update_test

update_testfails:
	for i in mutants/*/test.log; do echo $$i; grep -a '\(FAIL:\|ERROR:\)' $$i > $$i.fail; echo $$i.fail; done
