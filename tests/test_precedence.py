from sloperator.runner import run_source


def test_multiplication_happens_before_addition():
    result = run_source("hallucinate(2 + 3 * 4)✨\nhallucinate(2 * 3 + 4)✨")
    assert result.exit_code == 0
    assert result.stderr == ""
    assert result.stdout == "14\n10\n"
