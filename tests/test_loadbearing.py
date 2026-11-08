import pytest

from sloperator.runner import run_source


@pytest.mark.parametrize(
    ("initializer", "expected"),
    [
        ("20 + 22", "42"),
        ("“hello”", "hello"),
        ("✅", "✅"),
        ("❌", "❌"),
        ("nothing()", "nil"),
        ("nothing", "<clanker nothing>"),
        ("hallucinate", "<clanker hallucinate>"),
    ],
)
def test_loadbearing_accepts_every_value_kind(initializer: str, expected: str):
    source = f"clanker nothing() {{ }}\nloadbearing value = {initializer}✨\nhallucinate(value)✨"
    result = run_source(source)
    assert (result.stdout, result.stderr, result.exit_code) == (f"{expected}\n", "", 0)


@pytest.mark.parametrize("expression", ["200", "100", "LIMIT", "LIMIT + 1"])
def test_loadbearing_reassignment_fails_but_slop_stays_mutable(expression: str):
    source = f"""loadbearing LIMIT = 100✨
slop score = 10✨
score = score + 1✨
hallucinate(score)✨
LIMIT = {expression}✨
hallucinate(“unreachable”)✨"""
    result = run_source(source)
    assert result.stdout == "11\n"
    assert (
        result.stderr == "SlopLang runtime error at line 5: cannot assign to loadbearing 'LIMIT'\n"
    )
    assert result.exit_code == 1


def test_slop_can_shadow_loadbearing():
    source = """loadbearing LIMIT = 100✨
{
    slop LIMIT = 10✨
    LIMIT = 20✨
    hallucinate(LIMIT)✨
}
hallucinate(LIMIT)✨"""
    result = run_source(source)
    assert (result.stdout, result.stderr, result.exit_code) == ("20\n100\n", "", 0)


@pytest.mark.parametrize("outer_keyword", ["slop", "loadbearing"])
def test_loadbearing_can_shadow_an_outer_binding(outer_keyword: str):
    source = f"""{outer_keyword} LIMIT = 100✨
{{
    loadbearing LIMIT = 10✨
    hallucinate(LIMIT)✨
}}
hallucinate(LIMIT)✨"""
    result = run_source(source)
    assert (result.stdout, result.stderr, result.exit_code) == ("10\n100\n", "", 0)


def test_assignment_targets_inner_loadbearing_not_outer_slop():
    source = """slop LIMIT = 100✨
{
    loadbearing LIMIT = 10✨
    LIMIT = 20✨
}"""
    result = run_source(source)
    assert result.stdout == ""
    assert (
        result.stderr == "SlopLang runtime error at line 4: cannot assign to loadbearing 'LIMIT'\n"
    )
    assert result.exit_code == 1


@pytest.mark.parametrize("first_keyword", ["slop", "loadbearing"])
@pytest.mark.parametrize("second_keyword", ["slop", "loadbearing"])
def test_declarations_cannot_reuse_a_name_in_the_same_scope(
    first_keyword: str, second_keyword: str
):
    source = f"{first_keyword} value = 1✨\n{second_keyword} value = 2✨"
    result = run_source(source)
    assert result.stdout == ""
    assert result.stderr == (
        "SlopLang runtime error at line 2: 'value' is already declared in this scope\n"
    )
    assert result.exit_code == 1


@pytest.mark.parametrize(
    "body",
    [
        "{\n    LIMIT = 200✨\n}",
        "vibe ✅ {\n    LIMIT = 200✨\n}",
        "clanker change() {\n    LIMIT = 200✨\n}\nchange()✨",
    ],
)
def test_loadbearing_cannot_be_reassigned_from_an_inner_scope(body: str):
    result = run_source(f"loadbearing LIMIT = 100✨\n{body}")
    assert result.stdout == ""
    assert (
        result.stderr == "SlopLang runtime error at line 3: cannot assign to loadbearing 'LIMIT'\n"
    )
    assert result.exit_code == 1


def test_loadbearing_can_be_declared_in_a_conditional():
    source = "vibe ✅ {\n    loadbearing LIMIT = 100✨\n    hallucinate(LIMIT)✨\n}"
    result = run_source(source)
    assert (result.stdout, result.stderr, result.exit_code) == ("100\n", "", 0)


def test_loadbearing_is_local_to_each_function_call():
    source = """clanker next(value) {
    loadbearing result = value + 1✨
    ship result✨
}
hallucinate(next(10))✨
hallucinate(next(20))✨
hallucinate(result)✨"""
    result = run_source(source)
    assert result.stdout == "11\n21\n"
    assert result.stderr == "SlopLang runtime error at line 7: undefined variable 'result'\n"
    assert result.exit_code == 1


def test_function_local_loadbearing_is_immutable():
    source = """clanker change() {
    loadbearing LIMIT = 100✨
    LIMIT = 200✨
}
change()✨"""
    result = run_source(source)
    assert result.stdout == ""
    assert (
        result.stderr == "SlopLang runtime error at line 3: cannot assign to loadbearing 'LIMIT'\n"
    )
    assert result.exit_code == 1


@pytest.mark.parametrize(
    ("expression", "stdout", "message"),
    [
        ("hallucinate(“side effect”)", "side effect\n", "cannot assign to loadbearing 'LIMIT'"),
        ("missing", "", "undefined variable 'missing'"),
    ],
)
def test_loadbearing_assignment_evaluates_rhs_first(expression: str, stdout: str, message: str):
    result = run_source(f"loadbearing LIMIT = 100✨\nLIMIT = {expression}✨")
    assert result.stdout == stdout
    assert result.stderr == f"SlopLang runtime error at line 2: {message}\n"
    assert result.exit_code == 1


@pytest.mark.parametrize(
    ("source", "name", "line"),
    [("clanker f() { }\nf = 1✨", "f", 2), ("hallucinate = 1✨", "hallucinate", 1)],
)
def test_existing_immutable_binding_diagnostics_are_unchanged(source: str, name: str, line: int):
    result = run_source(source)
    assert result.stdout == ""
    assert result.stderr == (
        f"SlopLang runtime error at line {line}: cannot assign to immutable binding '{name}'\n"
    )
    assert result.exit_code == 1
