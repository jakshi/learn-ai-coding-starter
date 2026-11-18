# Parser conventions

- Use one parser method per grammar rule, matching the grammar in `docs/spec.md`.
- Syntax errors must describe what was expected and which token was found. Use `Parser.error` to include `found '<lexeme>'` or an explicit end-of-file message.
