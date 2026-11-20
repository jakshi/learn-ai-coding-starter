import pytest

from sloperator.runner import run_source


@pytest.mark.parametrize(
    ("expression", "expected"),
    [
        ("1 < 2 == 3 < 4", "✅"),
        ("1 < 2 != 3 < 4", "❌"),
        ("1 < 2 == 3 > 4", "❌"),
        ("1 < 2 != 3 > 4", "✅"),
        ("1 <= 2 == 4 >= 3", "✅"),
        ("1 < 2 == ✅", "✅"),
        ("✅ == 1 < 2", "✅"),
        ("1 < 2 != ❌", "✅"),
        ("❌ != 1 < 2", "✅"),
        ("1 + 2 < 4 == 2 * 3 >= 6", "✅"),
        ("1 < 2 == ✅ && 3 > 2 != ❌", "✅"),
        ("1 > 2 == ✅ || 3 < 4 == ✅", "✅"),
        ("(1 < 2) == (3 < 4)", "✅"),
    ],
)
def test_comparisons_bind_more_tightly_than_equality(expression: str, expected: str):
    result = run_source(f"hallucinate({expression})✨")

    assert result.exit_code == 0
    assert result.stderr == ""
    assert result.stdout == f"{expected}\n"
