import pytest

from sloperator.runner import run_source


@pytest.mark.parametrize("literal", ["✅", "❌"])
def test_unary_minus_rejects_booleans(literal: str):
    result = run_source(f"hallucinate(-{literal})✨")

    assert result.exit_code == 1
    assert result.stdout == ""
    assert result.stderr == (
        "SlopLang runtime error at line 1: operand of unary '-' must be a number, got boolean\n"
    )
