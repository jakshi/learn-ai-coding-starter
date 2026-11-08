import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
INTERPRETER = ROOT / "sloperator.py"


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(INTERPRETER), *args], capture_output=True, encoding="utf-8", timeout=5
    )


def test_runs_a_file():
    completed = run_cli(str(ROOT / "examples/hello.slop"))
    assert completed.returncode == 0
    assert completed.stdout == "hello, slop\n"
    assert completed.stderr == ""


def test_error_goes_to_stderr_after_earlier_output(tmp_path: Path):
    program = tmp_path / "boom.slop"
    program.write_text("hallucinate(“before”)✨\nhallucinate(missing)✨\n", encoding="utf-8")
    completed = run_cli(str(program))
    assert completed.returncode == 1
    assert completed.stdout == "before\n"
    assert completed.stderr == "SlopLang runtime error at line 2: undefined variable 'missing'\n"
    assert "Traceback" not in completed.stderr


def test_missing_file_and_usage():
    assert run_cli().returncode == 2
    missing = run_cli(str(ROOT / "nope.slop"))
    assert missing.returncode == 2
    assert "could not read" in missing.stderr


@pytest.mark.parametrize(
    ("source", "stdout", "line"),
    [
        ("hallucinate(1 / 0)✨", "", 1),
        ("hallucinate(0 / 0)✨", "", 1),
        ("hallucinate(-7 / 0)✨", "", 1),
        ("hallucinate(1 / (2 - 2))✨", "", 1),
        (
            "hallucinate(“before”)✨\nhallucinate(1 / 0)✨\nhallucinate(“after”)✨",
            "before\n",
            2,
        ),
    ],
    ids=["positive", "zero", "negative", "computed-zero", "earlier-output"],
)
def test_division_by_zero_reports_a_runtime_error(
    tmp_path: Path, source: str, stdout: str, line: int
):
    program = tmp_path / "division-by-zero.slop"
    program.write_text(source, encoding="utf-8")
    completed = run_cli(str(program))
    assert completed.returncode == 1
    assert completed.stdout == stdout
    assert completed.stderr == f"SlopLang runtime error at line {line}: division by zero\n"
    assert "Traceback" not in completed.stderr


@pytest.mark.parametrize("check_first", [True, False], ids=["flag-first", "flag-last"])
@pytest.mark.parametrize(
    "source",
    [
        "",
        "hallucinate(“not executed”)✨",
        "hallucinate(missing)✨",
        "hallucinate(1 / 0)✨",
        "loadbearing LIMIT = 100✨\nLIMIT = 200✨",
        "ralph ✅ { }",
    ],
    ids=[
        "empty",
        "output",
        "undefined-name",
        "division-by-zero",
        "immutable-assignment",
        "infinite-loop",
    ],
)
def test_check_only_parses_without_running(tmp_path: Path, source: str, check_first: bool):
    program = tmp_path / "check me.slop"
    program.write_text(source, encoding="utf-8")
    args = ("--check", str(program)) if check_first else (str(program), "--check")
    completed = run_cli(*args)
    assert completed.returncode == 0
    assert completed.stdout == ""
    assert completed.stderr == ""


@pytest.mark.parametrize(
    ("source", "message"),
    [
        (
            "hallucinate(“not executed”)✨\n@",
            "SlopLang lexical error at line 2: unexpected character '@'\n",
        ),
        (
            "hallucinate(“not executed”)✨\nslop x = 1",
            "SlopLang syntax error at line 2: expected ✨ after variable declaration, "
            "but reached end of file\n",
        ),
        (
            "loadbearing LIMIT✨",
            "SlopLang syntax error at line 1: expected '=' after variable name, "
            "an initializer is required, found '✨'\n",
        ),
    ],
    ids=["lexical-error", "syntax-error", "missing-initializer"],
)
def test_check_reports_errors_without_executing(tmp_path: Path, source: str, message: str):
    program = tmp_path / "invalid.slop"
    program.write_text(source, encoding="utf-8")
    completed = run_cli("--check", str(program))
    assert completed.returncode == 1
    assert completed.stdout == ""
    assert completed.stderr == message


def test_check_missing_file_returns_two(tmp_path: Path):
    completed = run_cli("--check", str(tmp_path / "missing.slop"))
    assert completed.returncode == 2
    assert completed.stdout == ""
    assert "could not read" in completed.stderr


@pytest.mark.parametrize(
    "args",
    [
        ("--check",),
        ("--check", "one.slop", "two.slop"),
        ("--validate", str(ROOT / "examples/hello.slop")),
    ],
    ids=["missing-file-argument", "too-many-files", "old-flag-name"],
)
def test_invalid_check_arguments_show_usage(args: tuple[str, ...]):
    completed = run_cli(*args)
    assert completed.returncode == 2
    assert completed.stdout == ""
    assert "usage:" in completed.stderr
