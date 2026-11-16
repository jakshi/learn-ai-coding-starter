from sloperator.runner import run_source


def test_call_can_be_used_directly_as_an_argument():
    source = """clanker add_one(number) {
    ship number + 1✨
}
clanker double(number) {
    ship number * 2✨
}
hallucinate(double(add_one(20)))✨"""

    result = run_source(source)

    assert result.exit_code == 0
    assert result.stdout == "42\n"
    assert result.stderr == ""
