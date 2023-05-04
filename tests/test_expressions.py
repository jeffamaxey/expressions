# -*- encoding: utf8 -*-
import unittest
from expressions import Compiler, ExpressionInspector
from expressions import Variable, Function, UnaryOperator, BinaryOperator

class ValidatingCompiler(Compiler):
    def compile_variable(self, context, variable):
        if variable not in context:
            raise ExpressionError(variable)
    def compile_function(self, context, function, args):
        if function not in context:
            raise ExpressionError(function)
    def compile_literal(self, context, literal):
        pass
    def compile_operator(self, context, operator, op1, op2):
        pass

class FunctionCompiler(Compiler):
    def compile_variable(self, context, variable):
        return variable
    def compile_function(self, context, function, args):
        return f'CALL {function}({", ".join(args)})'

class CompilerTestCase(unittest.TestCase):
    def test_basic(self):
        compiler = Compiler()
        result = compiler.compile("1")
        self.assertEqual(result, 1)
        self.assertIsInstance(result, int)

        result = compiler.compile("1.2")
        self.assertEqual(result, 1.2)
        self.assertIsInstance(result, float)

        result = compiler.compile("'a string'")
        self.assertEqual(result, "a string")
        self.assertIsInstance(result, str)

    def test_strings(self):
        compiler = Compiler()

        result = compiler.compile("''")
        self.assertEqual(result, "")

        result = compiler.compile("'a \\' quote'")
        self.assertEqual(result, "a ' quote")

    def test_variable(self):
        compiler = Compiler()
        result = compiler.compile("foo")
        self.assertIsInstance(result, Variable)
        self.assertEqual(result.name, "foo")
        self.assertEqual(result.reference, ["foo"])

        result = compiler.compile("foo.bar.baz")
        self.assertIsInstance(result, Variable)
        self.assertEqual(result.name, "foo.bar.baz")
        self.assertEqual(result.reference, ["foo", "bar", "baz"])

    def test_function(self):
        compiler = Compiler()

        result = compiler.compile("foo()")
        self.assertIsInstance(result, Function)
        self.assertEqual(result.name, "foo")
        self.assertEqual(result.reference, ["foo"])
        self.assertEqual(result.args, [])

        result = compiler.compile("foo.bar.baz()")
        self.assertIsInstance(result, Function)
        self.assertEqual(result.name, "foo.bar.baz")
        self.assertEqual(result.reference, ["foo", "bar", "baz"])
        self.assertEqual(result.args, [])

        result = compiler.compile("foo(10,20,30)")
        self.assertIsInstance(result, Function)
        self.assertEqual(result.args, [10, 20, 30])

    def test_unary(self):
        compiler = Compiler()

        result = compiler.compile("+1")
        self.assertIsInstance(result, UnaryOperator)
        self.assertEqual(result.operator, "+")
        self.assertEqual(result.operand, 1)

    def test_binary(self):
        compiler = Compiler()

        result = compiler.compile("101 + 202")
        self.assertIsInstance(result, BinaryOperator)
        self.assertEqual(result.operator, "+")
        self.assertEqual(result.left, 101)
        self.assertEqual(result.right, 202)

    @unittest.skip("later")
    def test_validating_compiler(self):
        compiler = ValidatingCompiler()
        result = compiler.compile("a+a", ["a", "b"])

    @unittest.skip("later")
    def test_function_call_compile(self):
        compiler = FunctionCompiler()

        result = compiler.compile("f()")
        self.assertEqual("CALL f()", result)

        result = compiler.compile("f(x)")
        self.assertEqual("CALL f(x)", result)

        result = compiler.compile("f(x, y)")
        self.assertEqual("CALL f(x, y)", result)

class CustomCompilersTestCase(unittest.TestCase):
    def test_preprocessor(self):
        pp = ExpressionInspector()
        pp.compile("foo(a + b) * bar(b + c)")

        functions = set(pp.functions)
        variables = set(pp.variables)

        self.assertEqual(functions, {"foo", "bar"})
        self.assertEqual(variables, {"a", "b", "c"})

    def test_preprocessor_unique(self):
        pp = ExpressionInspector()
        pp.compile("foo(a,a,b,b,c,c,c,c) + foo(a,b,c)")

        functions = sorted(pp.functions)
        variables = sorted(pp.variables)

        self.assertEqual(functions, ["foo"])
        self.assertEqual(variables, ["a", "b", "c"])
