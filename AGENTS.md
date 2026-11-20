# Sloperator agent notes

## Project layout

- `sloperator.py`: CLI entrypoint; `sloperator/runner.py` connects the lexer, parser, and evaluator.
- `tests/`: regression tests; `examples/`: runnable `.slop` programs.
- `playground/`: web UI and server; `.opencode/`: OpenCode plugin and configuration.

## Validation

Run all four commands from the project root after Python changes:

```bash
uv run pytest
uv run ruff format --check
uv run ruff check
uv run ty check
```

## Regression tests

- For comparison and equality precedence changes, run `uv run pytest tests/test_comparisons.py -q` from the project root.
- Add focused tests for bug fixes and changes to parsing, evaluation, or diagnostics, covering the failing case and relevant edge cases.
- Use `sloperator.runner.run_source` for end-to-end language tests; assert exact stdout, stderr (including line numbers), and `exit_code` where relevant.
- Keep invalid programs in test fixtures. Every `examples/*.slop` must run successfully with nonempty output; add a focused test when exact output matters.

## Language behavior

Consult [docs/spec.md](docs/spec.md) before changing language behavior or writing `.slop` fixtures. It defines syntax, precedence, types, scoping, and errors.
