import pytest

from sloperator.errors import SlopSyntaxError
from sloperator.lexer import TokenType, tokenize
from sloperator.parser import parse
from sloperator.parser.ast import (
    Assign,
    Binary,
    Call,
    ExprStmt,
    FunctionDecl,
    Grouping,
    If,
    Literal,
    Ship,
    VarDecl,
    Variable,
    While,
)


def parse_source(source: str):
    return parse(tokenize(source))


def only_expression(source: str):
    (statement,) = parse_source(source)
    assert isinstance(statement, ExprStmt)
    return statement.expression


def test_same_precedence_is_left_associative():
    expr = only_expression("10 - 3 - 2✨")
    assert isinstance(expr, Binary)
    assert isinstance(expr.left, Binary)
    assert isinstance(expr.right, Literal) and expr.right.value == 2


def test_multiplication_and_division_are_left_associative():
    expr = only_expression("8 / 3 * 2✨")
    assert isinstance(expr, Binary) and expr.operator.type is TokenType.STAR
    assert isinstance(expr.left, Binary) and expr.left.operator.type is TokenType.SLASH
    assert isinstance(expr.right, Literal) and expr.right.value == 2


def test_grouping_overrides_precedence():
    expr = only_expression("(1 + 2) * 3✨")
    assert isinstance(expr, Binary) and expr.operator.type is TokenType.STAR
    assert isinstance(expr.left, Grouping)


def test_calls_chain():
    expr = only_expression("f(1)(2, 3)✨")
    assert isinstance(expr, Call) and len(expr.arguments) == 2
    assert isinstance(expr.callee, Call) and len(expr.callee.arguments) == 1
    assert isinstance(expr.callee.callee, Variable)


@pytest.mark.parametrize(
    ("source", "count"),
    [("f()✨", 0), ("f(1)✨", 1), ("f(1, 2, 3)✨", 3)],
)
def test_call_argument_counts(source: str, count: int):
    expr = only_expression(source)
    assert isinstance(expr, Call) and len(expr.arguments) == count


def test_assignment_is_a_statement():
    (plain,) = parse_source("x = 1✨")
    assert isinstance(plain, Assign) and plain.operator.type is TokenType.EQUAL


def test_assignment_is_not_an_expression():
    with pytest.raises(SlopSyntaxError, match=r"expected '\)' after arguments, found '='"):
        parse_source("hallucinate(x = 1)✨")


def test_slop_declaration():
    (declaration,) = parse_source("slop a = 1✨")
    assert isinstance(declaration, VarDecl) and declaration.mutable


def test_loadbearing_declaration():
    (declaration,) = parse_source("loadbearing LIMIT = 100✨")
    assert isinstance(declaration, VarDecl) and not declaration.mutable
    assert declaration.name.lexeme == "LIMIT"
    assert isinstance(declaration.initializer, Literal) and declaration.initializer.value == 100


def test_control_flow_shapes():
    (conditional, loop) = parse_source("vibe ✅ { } nah { } ralph ❌ { }")
    assert isinstance(conditional, If) and conditional.else_branch is not None
    assert isinstance(loop, While)


def test_function_declaration():
    (decl,) = parse_source("clanker add(a, b) { ship a + b✨ }")
    assert isinstance(decl, FunctionDecl)
    assert [p.lexeme for p in decl.params] == ["a", "b"]
    assert isinstance(decl.body.statements[0], Ship)


@pytest.mark.parametrize(
    ("source", "names"),
    [
        ("clanker f() { }", []),
        ("clanker f(a) { }", ["a"]),
        ("clanker f(a, b, c) { }", ["a", "b", "c"]),
    ],
)
def test_function_parameter_names(source: str, names: list[str]):
    (declaration,) = parse_source(source)
    assert isinstance(declaration, FunctionDecl)
    assert [parameter.lexeme for parameter in declaration.params] == names


@pytest.mark.parametrize(
    ("source", "line", "message"),
    [
        ("ship 1✨", 1, "ship is only allowed inside a clanker, found 'ship'"),
        (
            "{\n    clanker f() { }\n}",
            2,
            "clanker declarations are only allowed at the top level, found 'clanker'",
        ),
        ("clanker f(a, a) { }", 1, "duplicate parameter name 'a', found 'a'"),
        ("clanker f(a,\na) { }", 2, "duplicate parameter name 'a', found 'a'"),
        (
            "clanker f(a,) { }",
            1,
            "expected a parameter name after ',', found ')'",
        ),
        ("clanker f(", 1, "expected a parameter name, but reached end of file"),
        ("clanker f() { ship✨ }", 1, "expected an expression, found '✨'"),
        ("slop x = 1", 1, "expected ✨ after variable declaration, but reached end of file"),
        ("slop x✨", 1, "expected '=' after variable name, an initializer is required, found '✨'"),
        (
            "loadbearing LIMIT✨",
            1,
            "expected '=' after variable name, an initializer is required, found '✨'",
        ),
        (
            "loadbearing LIMIT = 100",
            1,
            "expected ✨ after variable declaration, but reached end of file",
        ),
        ("loadbearing = 100✨", 1, "expected a variable name after 'loadbearing', found '='"),
        ("loadbearing LIMIT = ✨", 1, "expected an expression, found '✨'"),
        (
            "slop loadbearing = 100✨",
            1,
            "expected a variable name after 'slop', found 'loadbearing'",
        ),
        ("vibe ✅ { } nah hallucinate()✨", 1, "expected '{' after nah, found 'hallucinate'"),
        ("vibe ✅ hallucinate()✨", 1, "expected '{' after vibe condition, found 'hallucinate'"),
        ("f(1,)✨", 1, "expected an expression, found ')'"),
        ("f(1,", 1, "expected an expression, but reached end of file"),
        ("(1 + 2✨", 1, "expected ')' after expression, found '✨'"),
        ("}", 1, "expected an expression, found '}'"),
    ],
)
def test_syntax_errors(source: str, line: int, message: str):
    with pytest.raises(SlopSyntaxError) as info:
        parse_source(source)
    assert info.value.line == line
    assert info.value.message == message
