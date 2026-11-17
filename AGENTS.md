# Sloperator agent notes

## Verification

- Standard run and validation commands are in `README.md`. Focus one regression with `uv run pytest tests/test_evaluator.py -k division -q`.
- For Python changes, also run `uv run ty check`: the repo-local `validate` skill runs pytest and Ruff but omits type checking.
- `bootdev run <UUID>` checks a lesson; adding `-s` submits it. Submit only when requested.

## Interpreter contracts

- Consult `docs/spec.md` before changing language behavior or writing `.slop` fixtures. Smart quotes `“...”`, em-dash comments `—`, and statement terminators `✨` are actual syntax.
- The CLI, playground, and OpenCode tool share `sloperator.py` → `sloperator/runner.py` → lexer/parser/evaluator. `--check` stops after parsing; syntactically valid runtime failures must still pass it.
- Raise the appropriate `SlopError` subclass from `sloperator/errors.py`; the runner catches only that family. Language regressions can use `sloperator.runner.run_source`, asserting exact stderr/line numbers, `exit_code`, and preservation of earlier stdout.
- Use the evaluator's `is_number` for numeric operands: Python booleans are integers, but SlopLang booleans are not numbers. Division must truncate toward zero without converting arbitrary-precision integers to floats.
- `tests/test_examples.py` discovers every `examples/*.slop` and requires successful, nonempty output. Keep invalid programs in test fixtures. The example suite does not assert exact stdout; add a focused assertion when output matters.

## Integration gotchas

- `.opencode/` has its own Bun dependencies. In `.opencode/plugins/run-slop.ts`, preserve project-root cwd, `uv run --no-active` (avoids inherited virtualenv paths), and `codemode: false`. Its JSON uses `exitCode`; the Python runner and playground use `exit_code`.
- Playground logs are written to root `logs/runs.log`, not `playground/logs/`.
- `uv.lock` is Git-tracked but excluded from ordinary search by `.ignore`; inspect it by its explicit path when investigating dependencies.
- Honor `opencode.jsonc` permissions. Do not route around denied `.env` reads or `explore` delegation through other tools or agents.

## Documentation

- Keep `README.md` under 50 lines, with interpreter and validation commands in the first 20. Put language details in `docs/spec.md` rather than expanding the README.
