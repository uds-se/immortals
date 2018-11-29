import ast
import re
import copy
import functools
from mutpy import utils


class MutationResign(Exception):
    pass


class Mutation:

    def __init__(self, operator, node, visitor=None):
        self.operator = operator
        self.node = node
        self.visitor = visitor


def copy_node(mutate):
    def f(self, node):
        copied_node = copy.deepcopy(node, memo={
            id(node.parent): node.parent,
        })
        return mutate(self, copied_node)
    return f


class MutationOperator:

    def mutate(self, node, to_mutate=None, sampler=None, coverage_injector=None, module=None, only_mutation=None):
        self.to_mutate = to_mutate
        self.sampler = sampler
        self.only_mutation = only_mutation
        self.coverage_injector = coverage_injector
        self.module = module
        for new_node in self.visit(node):
            yield Mutation(operator=self.__class__, node=self.current_node, visitor=self.visitor), new_node

    def visit(self, node):
        if self.has_notmutate(node) or (self.coverage_injector and not self.coverage_injector.is_covered(node)):
            return
        if self.only_mutation and self.only_mutation.node != node and self.only_mutation.node not in node.children:
            return
        self.fix_lineno(node)
        visitors = self.find_visitors(node)
        if visitors:
            for visitor in visitors:
                try:
                    if self.sampler and not self.sampler.is_mutation_time():
                        raise MutationResign
                    if self.only_mutation and \
                            (self.only_mutation.node != node or self.only_mutation.visitor != visitor.__name__):
                        raise MutationResign
                    new_node = visitor(node)
                    self.visitor = visitor.__name__
                    self.current_node = node
                    self.fix_node_internals(node, new_node)
                    ast.fix_missing_locations(new_node)
                    yield new_node
                except MutationResign:
                    pass
                finally:
                    for new_node in self.generic_visit(node):
                        yield new_node
        else:
            for new_node in self.generic_visit(node):
                yield new_node

    def generic_visit(self, node):
        for field, old_value in ast.iter_fields(node):
            if isinstance(old_value, list):
                generator = self.generic_visit_list(old_value)
            elif isinstance(old_value, ast.AST):
                generator = self.generic_visit_real_node(node, field, old_value)
            else:
                generator = []

            for _ in generator:
                yield node

    def generic_visit_list(self, old_value):
        old_values_copy = old_value[:]
        for position, value in enumerate(old_values_copy):
            if isinstance(value, ast.AST):
                for new_value in self.visit(value):
                    if not isinstance(new_value, ast.AST):
                        old_value[position:position+1] = new_value
                    elif value is None:
                        del old_value[position]
                    else:
                        old_value[position] = new_value

                    yield
                    old_value[:] = old_values_copy

    def generic_visit_real_node(self, node, field, old_value):
        for new_node in self.visit(old_value):
            if new_node is None:
                delattr(node, field)
            else:
                setattr(node, field, new_node)
            yield
            setattr(node, field, old_value)

    def has_notmutate(self, node):
        try:
            for decorator in node.decorator_list:
                if decorator.id == utils.notmutate.__name__:
                    return True
            return False
        except AttributeError:
            return False

    def fix_lineno(self, node):
        if not hasattr(node, 'lineno') and getattr(node, 'parent', None) is not None and hasattr(node.parent, 'lineno'):
            node.lineno = node.parent.lineno

    def fix_node_internals(self, old_node, new_node):
        if not hasattr(new_node, 'parent'):
            new_node.children = old_node.children
            new_node.parent = old_node.parent
        if hasattr(old_node, 'marker'):
            new_node.marker = old_node.marker

    def find_visitors(self, node):
        method_prefix = 'mutate_' + node.__class__.__name__
        return self.getattrs_like(method_prefix)

    def getattrs_like(ob, attr_like):
        pattern = re.compile(attr_like + "($|(_\w+)+$)")
        return [getattr(ob, attr) for attr in dir(ob) if pattern.match(attr)]

    @classmethod
    def name(cls):
        return ''.join([c for c in cls.__name__ if str.isupper(c)])

    @classmethod
    def long_name(cls):
        return ' '.join(map(str.lower, (re.split('([A-Z][a-z]*)', cls.__name__)[1::2])))


class AbstractUnaryOperatorDeletion(MutationOperator):

    def mutate_UnaryOp(self, node):
        if isinstance(node.op, self.get_operator_type()):
            return node.operand
        raise MutationResign()


class ArithmeticOperatorDeletion(AbstractUnaryOperatorDeletion):

    def get_operator_type(self):
        return ast.UAdd, ast.USub


class AbstractArithmeticOperatorReplacement(MutationOperator):

    def should_mutate(self, node):
        raise NotImplementedError()

    def mutate_Add(self, node):
        if self.should_mutate(node):
            return ast.Sub()
        raise MutationResign()

    def mutate_Sub(self, node):
        if self.should_mutate(node):
            return ast.Add()
        raise MutationResign()

    def mutate_Mult_to_Div(self, node):
        if self.should_mutate(node):
            return ast.Div()
        raise MutationResign()

    def mutate_Mult_to_FloorDiv(self, node):
        if self.should_mutate(node):
            return ast.FloorDiv()
        raise MutationResign()

    def mutate_Mult_to_Pow(self, node):
        if self.should_mutate(node):
            return ast.Pow()
        raise MutationResign()

    def mutate_Div_to_Mult(self, node):
        if self.should_mutate(node):
            return ast.Mult()
        raise MutationResign()

    def mutate_Div_to_FloorDiv(self, node):
        if self.should_mutate(node):
            return ast.FloorDiv()
        raise MutationResign()

    def mutate_FloorDiv_to_Div(self, node):
        if self.should_mutate(node):
            return ast.Div()
        raise MutationResign()

    def mutate_FloorDiv_to_Mult(self, node):
        if self.should_mutate(node):
            return ast.Mult()
        raise MutationResign()

    def mutate_Mod(self, node):
        if self.should_mutate(node):
            return ast.Mult()
        raise MutationResign()

    def mutate_Pow(self, node):
        if self.should_mutate(node):
            return ast.Mult()
        raise MutationResign()


class ArithmeticOperatorReplacement(AbstractArithmeticOperatorReplacement):

    def should_mutate(self, node):
        return not isinstance(node.parent, ast.AugAssign)

    def mutate_USub(self, node):
        return ast.UAdd()

    def mutate_UAdd(self, node):
        return ast.USub()


class AssignmentOperatorReplacement(AbstractArithmeticOperatorReplacement):

    def should_mutate(self, node):
        return isinstance(node.parent, ast.AugAssign)

    @classmethod
    def name(cls):
        return 'ASR'


class BreakContinueReplacement(MutationOperator):

    def mutate_Break(self, node):
        return ast.Continue()

    def mutate_Continue(self, node):
        return ast.Break()


class ConditionalOperatorDeletion(AbstractUnaryOperatorDeletion):

    def get_operator_type(self):
        return ast.Not

    def mutate_NotIn(self, node):
        return ast.In()


class ConditionalOperatorInsertion(MutationOperator):

    def negate_test(self, node):
        not_node = ast.UnaryOp(op=ast.Not(), operand=node.test)
        node.test = not_node
        return node

    @copy_node
    def mutate_While(self, node):
        return self.negate_test(node)

    @copy_node
    def mutate_If(self, node):
        return self.negate_test(node)

    def mutate_In(self, node):
        return ast.NotIn()


class ConstantReplacement(MutationOperator):
    FIRST_CONST_STRING = 'mutpy'
    SECOND_CONST_STRING = 'python'

    def mutate_Num(self, node):
        return ast.Num(n=node.n + 1)

    def mutate_Str(self, node):
        if utils.is_docstring(node):
            raise MutationResign()

        if node.s != self.FIRST_CONST_STRING:
            return ast.Str(s=self.FIRST_CONST_STRING)
        else:
            return ast.Str(s=self.SECOND_CONST_STRING)

    def mutate_Str_empty(self, node):
        if not node.s or utils.is_docstring(node):
            raise MutationResign()

        return ast.Str(s='')

    @classmethod
    def name(cls):
        return 'CRP'


class DecoratorDeletion(MutationOperator):

    @copy_node
    def mutate_FunctionDef(self, node):
        if node.decorator_list:
            node.decorator_list = []
            return node
        else:
            raise MutationResign()

    @classmethod
    def name(cls):
        return 'DDL'


class ExceptionHandlerDeletion(MutationOperator):

    def mutate_ExceptHandler(self, node):
        if node.body and isinstance(node.body[0], ast.Raise):
            raise MutationResign()
        return ast.ExceptHandler(type=node.type, name=node.name, body=[ast.Raise()])


class ExceptionSwallowing(MutationOperator):

    def mutate_ExceptHandler(self, node):
        if len(node.body) == 1 and isinstance(node.body[0], ast.Pass):
            raise MutationResign()
        return ast.ExceptHandler(type=node.type, name=node.name, body=[ast.Pass()])

    @classmethod
    def name(cls):
        return 'EXS'


class AbstractOverriddenElementModification(MutationOperator):

    def is_overridden(self, node, name=None):
        if not isinstance(node.parent, ast.ClassDef):
            raise MutationResign()
        if not name:
            name = node.name
        parent = node.parent
        parent_names = []
        while parent:
            if not isinstance(parent, ast.Module):
                parent_names.append(parent.name)
            if not isinstance(parent, ast.ClassDef) and not isinstance(parent, ast.Module):
                raise MutationResign()
            parent = parent.parent
        getattr_rec = lambda obj, attr: functools.reduce(getattr, attr, obj)
        try:
            klass = getattr_rec(self.module, reversed(parent_names))
        except AttributeError:
            raise MutationResign()
        for base_klass in type.mro(klass)[1:-1]:
            if hasattr(base_klass, name):
                return True
        return False


class HidingVariableDeletion(AbstractOverriddenElementModification):

    def mutate_Assign(self, node):
        if len(node.targets) > 1:
            raise MutationResign()
        if isinstance(node.targets[0], ast.Name) and self.is_overridden(node, name=node.targets[0].id):
            return ast.Pass()
        elif isinstance(node.targets[0], ast.Tuple) and isinstance(node.value, ast.Tuple):
            return self.mutate_unpack(node)
        else:
            raise MutationResign()

    def mutate_unpack(self, node):
        target = node.targets[0]
        value = node.value
        new_targets = []
        new_values = []
        for target_element, value_element in zip(target.elts, value.elts):
            if not self.is_overridden(node, getattr(target_element, 'id', None)):
                new_targets.append(target_element)
                new_values.append(value_element)
        if len(new_targets) == len(target.elts):
            raise MutationResign()
        if not new_targets:
            return ast.Pass()
        elif len(new_targets) == 1:
            node.targets = new_targets
            node.value = new_values[0]
            return node
        else:
            target.elts = new_targets
            value.elts = new_values
            return node

    @classmethod
    def name(cls):
        return 'IHD'


class LogicalConnectorReplacement(MutationOperator):

    def mutate_And(self, node):
        return ast.Or()

    def mutate_Or(self, node):
        return ast.And()


class LogicalOperatorDeletion(AbstractUnaryOperatorDeletion):

    def get_operator_type(self):
        return ast.Invert


class LogicalOperatorReplacement(MutationOperator):

    def mutate_BitAnd(self, node):
        return ast.BitOr()

    def mutate_BitOr(self, node):
        return ast.BitAnd()

    def mutate_BitXor(self, node):
        return ast.BitAnd()

    def mutate_LShift(self, node):
        return ast.RShift()

    def mutate_RShift(self, node):
        return ast.LShift()


class AbstractSuperCallingModification(MutationOperator):

    def is_super_call(self, node, stmt):
        return isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call) and \
            isinstance(stmt.value.func, ast.Attribute) and isinstance(stmt.value.func.value, ast.Call) and \
            isinstance(stmt.value.func.value.func, ast.Name) and stmt.value.func.value.func.id == 'super' and \
            stmt.value.func.attr == node.name

    def should_mutate(self, node):
        return isinstance(node.parent, ast.ClassDef)

    def get_super_call(self, node):
        for index, stmt in enumerate(node.body):
            if self.is_super_call(node, stmt):
                break
        else:
            return None, None
        return index, stmt


class OverriddenMethodCallingPositionChange(AbstractSuperCallingModification):

    def should_mutate(self, node):
        return super().should_mutate(node) and len(node.body) > 1

    @copy_node
    def mutate_FunctionDef(self, node):
        if not self.should_mutate(node):
            raise MutationResign()
        index, stmt = self.get_super_call(node)
        if index is None:
            raise MutationResign()
        super_call = node.body[index]
        del node.body[index]
        if index == 0:
            node.body.append(super_call)
        else:
            node.body.insert(0, super_call)
        return node

    @classmethod
    def name(cls):
        return 'IOP'


class OverridingMethodDeletion(AbstractOverriddenElementModification):

    def mutate_FunctionDef(self, node):
        if self.is_overridden(node):
            return ast.Pass()
        raise MutationResign()

    @classmethod
    def name(cls):
        return 'IOD'


class RelationalOperatorReplacement(MutationOperator):

    def mutate_Lt(self, node):
        return ast.Gt()

    def mutate_Lt_to_LtE(self, node):
        return ast.LtE()

    def mutate_Gt(self, node):
        return ast.Lt()

    def mutate_Gt_to_GtE(self, node):
        return ast.GtE()

    def mutate_LtE(self, node):
        return ast.GtE()

    def mutate_LtE_to_Lt(self, node):
        return ast.Lt()

    def mutate_GtE(self, node):
        return ast.LtE()

    def mutate_GtE_to_Gt(self, node):
        return ast.Gt()

    def mutate_Eq(self, node):
        return ast.NotEq()

    def mutate_NotEq(self, node):
        return ast.Eq()


class SliceIndexRemove(MutationOperator):

    def mutate_Slice_remove_lower(self, node):
        if not node.lower:
            raise MutationResign()

        return ast.Slice(lower=None, upper=node.upper, step=node.step)

    def mutate_Slice_remove_upper(self, node):
        if not node.upper:
            raise MutationResign()

        return ast.Slice(lower=node.lower, upper=None, step=node.step)

    def mutate_Slice_remove_step(self, node):
        if not node.step:
            raise MutationResign()

        return ast.Slice(lower=node.lower, upper=node.upper, step=None)


class SuperCallingDeletion(AbstractSuperCallingModification):

    @copy_node
    def mutate_FunctionDef(self, node):
        if not self.should_mutate(node):
            raise MutationResign()
        index, _ = self.get_super_call(node)
        if index is None:
            raise MutationResign()
        node.body[index] = ast.Pass()
        return node


class SuperCallingInsert(AbstractSuperCallingModification, AbstractOverriddenElementModification):

    def should_mutate(self, node):
        return super().should_mutate(node) and self.is_overridden(node)

    @copy_node
    def mutate_FunctionDef(self, node):
        if not self.should_mutate(node):
            raise MutationResign()
        index, stmt = self.get_super_call(node)
        if index is not None:
            raise MutationResign()
        node.body.insert(0, self.create_super_call(node))
        return node

    def create_super_call(self, node):
        super_call = utils.create_ast('super().{}()'.format(node.name)).body[0]
        for arg in node.args.args[1:-len(node.args.defaults) or None]:
            super_call.value.args.append(ast.Name(id=arg.arg, ctx=ast.Load()))
        for arg, default in zip(node.args.args[-len(node.args.defaults):], node.args.defaults):
            super_call.value.keywords.append(ast.keyword(arg=arg.arg, value=default))
        for arg, default in zip(node.args.kwonlyargs, node.args.kw_defaults):
            super_call.value.keywords.append(ast.keyword(arg=arg.arg, value=default))
        if node.args.vararg:
            super_call.value.starargs = ast.Name(id=node.args.vararg, ctx=ast.Load())
        if node.args.kwarg:
            super_call.value.kwargs = ast.Name(id=node.args.kwarg, ctx=ast.Load())
        return super_call


class AbstractMethodDecoratorInsertionMutationOperator(MutationOperator):

    @copy_node
    def mutate_FunctionDef(self, node):
        if not isinstance(node.parent, ast.ClassDef):
            raise MutationResign()
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Call):
                decorator_name = decorator.func.id
            elif isinstance(decorator, ast.Attribute):
                decorator_name = decorator.value.id
            else:
                decorator_name = decorator.id
            if decorator_name == self.get_decorator_name():
                raise MutationResign()

        decorator = ast.Name(id=self.get_decorator_name(), ctx=ast.Load())
        node.decorator_list.append(decorator)
        return node

    def get_decorator_name(self):
        raise NotImplementedError()


class ClassmethodDecoratorInsertion(AbstractMethodDecoratorInsertionMutationOperator):

    def get_decorator_name(self):
        return 'classmethod'


class OneIterationLoop(MutationOperator):

    def one_iteration(self, node):
        node.body.append(ast.Break())
        return node

    @copy_node
    def mutate_For(self, node):
        return self.one_iteration(node)

    @copy_node
    def mutate_While(self, node):
        return self.one_iteration(node)


class ReverseIterationLoop(MutationOperator):

    @copy_node
    def mutate_For(self, node):
        old_iter = node.iter
        node.iter = ast.Call(
            func=ast.Name(id=reversed.__name__, ctx=ast.Load()),
            args=[old_iter],
            keywords=[],
            starargs=None,
            kwargs=None,
        )
        return node


class SelfVariableDeletion(MutationOperator):

    def mutate_Attribute(self, node):
        try:
            if node.value.id == 'self':
                return ast.Name(id=node.attr, ctx=ast.Load())
            else:
                raise MutationResign()
        except AttributeError:
            raise MutationResign()


class StatementDeletion(MutationOperator):

    def mutate_Assign(self, node):
        return ast.Pass()

    def mutate_Return(self, node):
        return ast.Pass()

    def mutate_Expr(self, node):
        if utils.is_docstring(node.value):
            raise MutationResign()
        return ast.Pass()

    @classmethod
    def name(cls):
        return 'SDL'


class StaticmethodDecoratorInsertion(AbstractMethodDecoratorInsertionMutationOperator):

    def get_decorator_name(self):
        return 'staticmethod'


class ZeroIterationLoop(MutationOperator):

    def zero_iteration(self, node):
        node.body = [ast.Break()]
        return node

    @copy_node
    def mutate_For(self, node):
        return self.zero_iteration(node)

    @copy_node
    def mutate_While(self, node):
        return self.zero_iteration(node)


standard_operators = {
    ArithmeticOperatorDeletion,
    ArithmeticOperatorReplacement,
    AssignmentOperatorReplacement,
    BreakContinueReplacement,
    ConditionalOperatorDeletion,
    ConditionalOperatorInsertion,
    ConstantReplacement,
    DecoratorDeletion,
    ExceptionHandlerDeletion,
    ExceptionSwallowing,
    HidingVariableDeletion,
    LogicalConnectorReplacement,
    LogicalOperatorDeletion,
    LogicalOperatorReplacement,
    OverriddenMethodCallingPositionChange,
    OverridingMethodDeletion,
    RelationalOperatorReplacement,
    SliceIndexRemove,
    SuperCallingDeletion,
    SuperCallingInsert,
}

experimental_operators = {
    ClassmethodDecoratorInsertion,
    OneIterationLoop,
    ReverseIterationLoop,
    SelfVariableDeletion,
    StatementDeletion,
    StaticmethodDecoratorInsertion,
    ZeroIterationLoop,
}
