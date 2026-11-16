# Sloperator

A tree-walking SlopLang interpreter written in Python. Requires Python 3.13+ and uv.

## Run and validate

Run these commands from the project root:

```bash
uv run sloperator.py examples/hello.slop          # run a program
uv run sloperator.py --check examples/hello.slop  # check syntax without executing
uv run pytest                                   # run tests
uv run ruff format --check                       # check formatting
uv run ruff check                               # lint
uv run ty check                                 # type-check
```

## Language reference

See [docs/spec.md](docs/spec.md) for syntax, types, scoping, operators, and errors.
Browse [examples/](examples/) for runnable programs.

## Layout

- `sloperator.py`: command-line entrypoint.
- `sloperator/`: lexer, parser, evaluator, and shared runner.
- `tests/`: regression and example tests.

## Playground

```bash
uv run playground/server.py
```

Open <http://localhost:8080>.
