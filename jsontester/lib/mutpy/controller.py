import random
import copy
import sys
import unittest
from mutpy import views, utils, coverage, codegen


class TestsFailAtOriginal(Exception):

    def __init__(self, result=None):
        self.result = result


class MutationScore:

    def __init__(self):
        self.killed_mutants = 0
        self.timeout_mutants = 0
        self.incompetent_mutants = 0
        self.survived_mutants = 0
        self.covered_nodes = 0
        self.all_nodes = 0

    def count(self):
        bottom = self.all_mutants - self.incompetent_mutants
        return (((self.killed_mutants + self.timeout_mutants) / bottom) * 100) if bottom else 0

    def inc_killed(self):
        self.killed_mutants += 1

    def inc_timeout(self):
        self.timeout_mutants += 1

    def inc_incompetent(self):
        self.incompetent_mutants += 1

    def inc_survived(self):
        self.survived_mutants += 1

    def update_coverage(self, covered_nodes, all_nodes):
        self.covered_nodes += covered_nodes
        self.all_nodes += all_nodes

    @property
    def all_mutants(self):
        return self.killed_mutants + self.timeout_mutants + self.incompetent_mutants + self.survived_mutants


class MutationController(views.ViewNotifier):

    def __init__(self, target_loader, test_loader, views, mutant_generator,
                 timeout_factor=5, disable_stdout=False, mutate_covered=False, mutation_number=None):
        super().__init__(views)
        self.target_loader = target_loader
        self.test_loader = test_loader
        self.mutant_generator = mutant_generator
        self.timeout_factor = timeout_factor
        self.stdout_manager = utils.StdoutManager(disable_stdout)
        self.mutate_covered = mutate_covered
        self.mutation_number = mutation_number
        self.store_init_modules()

    def run(self):
        self.notify_initialize(self.target_loader.names, self.test_loader.names)
        try:
            timer = utils.Timer()
            self.run_mutation_process()
            self.notify_end(self.score, timer.stop())
        except TestsFailAtOriginal as error:
            self.notify_original_tests_fail(error.result)
            sys.exit(-1)
        except utils.ModulesLoaderException as error:
            self.notify_cant_load(error.name, error.exception)
            sys.exit(-2)

    def run_mutation_process(self):
        try:
            test_modules, total_duration, number_of_tests = self.load_and_check_tests()

            self.notify_passed(test_modules, number_of_tests)
            self.notify_start()

            self.score = MutationScore()

            for target_module, to_mutate in self.target_loader.load([module for module, *_ in test_modules]):
                self.mutate_module(target_module, to_mutate, total_duration)
        except KeyboardInterrupt:
            pass

    def load_and_check_tests(self):
        test_modules = []
        number_of_tests = 0
        total_duration = 0
        for test_module, target_test in self.test_loader.load():
            result, duration = self.run_test(test_module, target_test)
            if result.wasSuccessful():
                test_modules.append((test_module, target_test, duration))
            else:
                raise TestsFailAtOriginal(result)
            number_of_tests += result.testsRun
            total_duration += duration

        return test_modules, total_duration, number_of_tests

    def run_test(self, test_module, target_test):
        suite = self.get_test_suite(test_module, target_test)
        result = unittest.TestResult()
        timer = utils.Timer()
        with self.stdout_manager:
            suite.run(result)
        return result, timer.stop()

    def get_test_suite(self, test_module, target_test):
        if target_test:
            return unittest.TestLoader().loadTestsFromName(target_test, test_module)
        else:
            return unittest.TestLoader().loadTestsFromModule(test_module)

    @utils.TimeRegister
    def mutate_module(self, target_module, to_mutate, total_duration):
        target_ast = self.create_target_ast(target_module)
        target_src = codegen.to_source(target_ast)
        coverage_injector, coverage_result = self.inject_coverage(target_ast, target_module)

        if coverage_injector:
            self.score.update_coverage(*coverage_injector.get_result())
        for mutations, mutant_ast in self.mutant_generator.mutate(target_ast, to_mutate, coverage_injector,
                                                                  module=target_module):
            mutation_number = self.score.all_mutants + 1
            if self.mutation_number and self.mutation_number != mutation_number:
                self.score.inc_incompetent()
                continue
            self.notify_mutation(mutation_number, mutations, (target_module.__name__, target_src), mutant_ast)
            #x self.notify_mutation(mutation_number, mutations, target_module.__name__, mutant_ast)
            mutant_module = self.create_mutant_module(target_module, mutant_ast)
            if mutant_module:
                self.run_tests_with_mutant(total_duration, mutant_module, mutations, coverage_result)
            else:
                self.score.inc_incompetent()

    def inject_coverage(self, target_ast, target_module):
        if not self.mutate_covered:
            return None, None
        coverage_injector = coverage.CoverageInjector()
        coverage_module = coverage_injector.inject(target_ast, target_module.__name__)
        suite = self.create_test_suite(coverage_module)
        coverage_result = coverage.CoverageTestResult(coverage_injector=coverage_injector)
        with self.stdout_manager:
            suite.run(coverage_result)
        return coverage_injector, coverage_result

    @utils.TimeRegister
    def create_target_ast(self, target_module):
        with open(target_module.__file__) as target_file:
            return utils.create_ast(target_file.read())

    @utils.TimeRegister
    def create_mutant_module(self, target_module, mutant_ast):
        try:
            with self.stdout_manager:
                return utils.create_module(
                    ast_node=mutant_ast,
                    module_name=target_module.__name__
                )
        except BaseException as exception:
            self.notify_incompetent(0, exception, tests_run=0)
            return None

    def create_test_suite(self, mutant_module):
        suite = unittest.TestSuite()
        utils.InjectImporter(mutant_module).install()
        self.remove_loaded_modules()
        for test_module, target_test in self.test_loader.load():
            suite.addTests(self.get_test_suite(test_module, target_test))
        utils.InjectImporter.uninstall()
        return suite

    def mark_not_covered_tests_as_skip(self, mutations, coverage_result, suite):
        mutated_nodes = {mutation.node.marker for mutation in mutations}

        def iter_tests(tests):
            try:
                for test in tests:
                    iter_tests(test)
            except TypeError:
                add_skip(tests)

        def add_skip(test):
            if mutated_nodes.isdisjoint(coverage_result.test_covered_nodes[repr(test)]):
                test_method = getattr(test, test._testMethodName)
                setattr(test, test._testMethodName, unittest.skip('not covered')(test_method))

        iter_tests(suite)

    @utils.TimeRegister
    def run_tests_with_mutant(self, total_duration, mutant_module, mutations, coverage_result):
        suite = self.create_test_suite(mutant_module)
        if coverage_result:
            self.mark_not_covered_tests_as_skip(mutations, coverage_result, suite)
        timer = utils.Timer()
        result = self.run_mutation_test_runner(suite, total_duration)
        timer.stop()
        self.update_score_and_notify_views(result, timer.duration)

    def run_mutation_test_runner(self, suite, total_duration):
        live_time = self.timeout_factor * (total_duration if total_duration > 1 else 1)
        test_runner_class = utils.get_mutation_test_runner_class()
        test_runner = test_runner_class(suite=suite)
        with self.stdout_manager:
            test_runner.start()
            result = test_runner.get_result(live_time)
            test_runner.terminate()
        return result

    def update_score_and_notify_views(self, result, mutant_duration):
        if not result:
            self.update_timeout_mutant(mutant_duration)
        elif result.is_incompetent:
            self.update_incompetent_mutant(result, mutant_duration)
        elif result.is_survived:
            self.update_survived_mutant(result, mutant_duration)
        else:
            self.update_killed_mutant(result, mutant_duration)

    def update_timeout_mutant(self, duration):
        self.notify_timeout(duration)
        self.score.inc_timeout()

    def update_incompetent_mutant(self, result, duration):
        self.notify_incompetent(duration, result.exception, result.tests_run)
        self.score.inc_incompetent()

    def update_survived_mutant(self, result, duration):
        self.notify_survived(duration, result.tests_run)
        self.score.inc_survived()

    def update_killed_mutant(self, result, duration):
        self.notify_killed(duration, result.killer, result.exception_traceback, result.tests_run)
        self.score.inc_killed()

    def store_init_modules(self):
        test_runner_class = utils.get_mutation_test_runner_class()
        test_runner = test_runner_class(suite=unittest.TestSuite())
        test_runner.start()
        self.init_modules = list(sys.modules.keys())

    def remove_loaded_modules(self):
        for module in list(sys.modules.keys()):
            if module not in self.init_modules:
                del sys.modules[module]


class HOMStrategy:

    def __init__(self, order=2):
        self.order = order

    def remove_bad_mutations(self, mutations_to_apply, available_mutations, allow_same_operators=True):
        for mutation_to_apply in mutations_to_apply:
            for available_mutation in available_mutations[:]:
                if mutation_to_apply.node == available_mutation.node or \
                   mutation_to_apply.node in available_mutation.node.children or \
                   available_mutation.node in mutation_to_apply.node.children or \
                   (not allow_same_operators and mutation_to_apply.operator == available_mutation.operator):
                    available_mutations.remove(available_mutation)


class FirstToLastHOMStrategy(HOMStrategy):
    name = 'FIRST_TO_LAST'

    def generate(self, mutations):
        mutations = mutations[:]
        while mutations:
            mutations_to_apply = []
            index = 0
            available_mutations = mutations[:]
            while len(mutations_to_apply) < self.order and available_mutations:
                try:
                    mutation = available_mutations.pop(index)
                    mutations_to_apply.append(mutation)
                    mutations.remove(mutation)
                    index = 0 if index == -1 else -1
                except IndexError:
                    break
                self.remove_bad_mutations(mutations_to_apply, available_mutations)
            yield mutations_to_apply


class EachChoiceHOMStrategy(HOMStrategy):
    name = 'EACH_CHOICE'

    def generate(self, mutations):
        mutations = mutations[:]
        while mutations:
            mutations_to_apply = []
            available_mutations = mutations[:]
            while len(mutations_to_apply) < self.order and available_mutations:
                try:
                    mutation = available_mutations.pop(0)
                    mutations_to_apply.append(mutation)
                    mutations.remove(mutation)
                except IndexError:
                    break
                self.remove_bad_mutations(mutations_to_apply, available_mutations)
            yield mutations_to_apply


class BetweenOperatorsHOMStrategy(HOMStrategy):
    name = 'BETWEEN_OPERATORS'

    def generate(self, mutations):
        usage = {mutation: 0 for mutation in mutations}
        not_used = mutations[:]
        while not_used:
            mutations_to_apply = []
            available_mutations = mutations[:]
            available_mutations.sort(key=lambda x: usage[x])
            while len(mutations_to_apply) < self.order and available_mutations:
                mutation = available_mutations.pop(0)
                mutations_to_apply.append(mutation)
                if not usage[mutation]:
                    not_used.remove(mutation)
                usage[mutation] += 1
                self.remove_bad_mutations(mutations_to_apply, available_mutations, allow_same_operators=False)
            yield mutations_to_apply


class RandomHOMStrategy(HOMStrategy):
    name = 'RANDOM'

    def __init__(self, *args, shuffler=random.shuffle, **kwargs):
        super().__init__(*args, **kwargs)
        self.shuffler = shuffler

    def generate(self, mutations):
        mutations = mutations[:]
        self.shuffler(mutations)
        while mutations:
            mutations_to_apply = []
            available_mutations = mutations[:]
            while len(mutations_to_apply) < self.order and available_mutations:
                try:
                    mutation = available_mutations.pop(0)
                    mutations_to_apply.append(mutation)
                    mutations.remove(mutation)
                except IndexError:
                    break
                self.remove_bad_mutations(mutations_to_apply, available_mutations)
            yield mutations_to_apply


hom_strategies = [
    BetweenOperatorsHOMStrategy,
    EachChoiceHOMStrategy,
    FirstToLastHOMStrategy,
    RandomHOMStrategy,
]


class FirstOrderMutator:

    def __init__(self, operators, percentage=100):
        self.operators = operators
        self.sampler = utils.RandomSampler(percentage)

    def mutate(self, target_ast, to_mutate=None, coverage_injector=None, module=None):
        for op in utils.sort_operators(self.operators):
            for mutation, mutant in op().mutate(target_ast, to_mutate, self.sampler, coverage_injector, module=module):
                yield [mutation], mutant


class HighOrderMutator(FirstOrderMutator):

    def __init__(self, *args, hom_strategy=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.hom_strategy = hom_strategy or FirstToLastHOMStrategy(order=2)

    def mutate(self, target_ast, to_mutate=None, coverage_injector=None, module=None):
        mutations = self.generate_all_mutations(coverage_injector, module, target_ast, to_mutate)
        for mutations_to_apply in self.hom_strategy.generate(mutations):
            generators = []
            applied_mutations = []
            mutant = target_ast
            for mutation in mutations_to_apply:
                generator = mutation.operator().mutate(
                    mutant,
                    to_mutate=to_mutate,
                    sampler=self.sampler,
                    coverage_injector=coverage_injector,
                    module=module,
                    only_mutation=mutation,
                )
                try:
                    new_mutation, mutant = generator.__next__()
                except StopIteration:
                    assert False, 'no mutations!'
                applied_mutations.append(new_mutation)
                generators.append(generator)
            yield applied_mutations, mutant
            self.finish_generators(generators)

    def generate_all_mutations(self, coverage_injector, module, target_ast, to_mutate):
        mutations = []
        for op in utils.sort_operators(self.operators):
            for mutation, _ in op().mutate(target_ast, to_mutate, None, coverage_injector, module=module):
                mutations.append(mutation)
        return mutations

    def finish_generators(self, generators):
        for generator in reversed(generators):
            try:
                generator.__next__()
            except StopIteration:
                continue
            assert False, 'too many mutations!'
