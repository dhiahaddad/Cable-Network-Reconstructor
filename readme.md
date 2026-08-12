# Cable Network Reconstructor

## Cheat sheet
sqlite3 database.db < database.sql

### Ruff — linting and formatting

Check code for common issues:

```bash
ruff check src/
```

Automatically fix safe lint issues:

```bash
ruff check --fix src/
```

Check formatting without modifying files:

```bash
ruff format --check src/
```

Format the code:

```bash
ruff format src/
```

Show more detailed output:

```bash
ruff check --output-format=full src/
```

Typical workflow:

```bash
ruff check --fix src/
ruff format src/
```

---

### Pyright — static type checking

Check all source code:

```bash
pyright src/
```

---

### pytest — automated tests

Run all tests:

```bash
pytest
```

Run with concise output:

```bash
pytest -q
```

Run with more detail:

```bash
pytest -v
```

Show print output while testing:

```bash
pytest -s
```

---

### Recommended development check

Before committing:

```bash
ruff check src/
ruff format --check src/
pyright src/
pytest
```

If you want Ruff to clean things first:

```bash
ruff check --fix src/
ruff format src/
pyright src/
pytest
```

### What each tool does

```text
ruff check          code quality / linting
ruff format         code formatting
pyright             static type checking
pytest              run actual tests
```

A useful way to remember it:

```text
Ruff:    "Does the code look sane?"
Pyright: "Do the types make sense?"
pytest:  "Does the code actually behave correctly?"
```
