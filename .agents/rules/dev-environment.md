# Development Environment

Development environment setup of this repository: dependency management with uv, the development tools and the Poe the Poet tasks. It complements [`AGENTS.md`](../../AGENTS.md), and every agent must follow it when installing, adding, removing or upgrading dependencies, and when running the development tools.

## Dependency management: uv

Dependencies and environments are managed **exclusively with [uv](https://docs.astral.sh/uv/)** by Astral. **Never** use `pip`, `pip install`, `requirements.txt`, `poetry` or `conda`.

| Action                           | Command                                                    |
| -------------------------------- | ---------------------------------------------------------- |
| Install all dependencies         | `uv sync --all-groups`                                     |
| Add a runtime dependency         | `uv add <package>`                                         |
| Add a development dependency     | `uv add --group dev <package>`                             |
| Add a documentation dependency   | `uv add --group docs <package>`                            |
| Remove a dependency              | `uv remove <package>` (add `--group <group>` if needed)    |
| Upgrade one dependency           | `uv lock --upgrade-package <package>`, then `uv sync`      |
| Upgrade all dependencies         | `uv lock --upgrade`, then `uv sync`                        |
| Run a command in the environment | `uv run <command>`                                         |
| Build the package (wheel/sdist)  | `uv build --no-sources`                                    |

Dependency groups defined in `pyproject.toml`:

- `dependencies` — package runtime (empty by default).
- `dev` — `poethepoet`, `pytest`, `pytest-cov`, `ruff`, `ty`.
- `docs` — `zensical`, `mkdocstrings`.

When changing dependencies, use uv commands (which update `pyproject.toml` and `uv.lock` together) instead of editing those files by hand.

## Development tools

- **Ruff** (`ruff.toml`) — linter and formatter. 120-character lines, double quotes, 4-space indentation, LF line
  endings, `py313` target. Many rule sets are enabled, including mandatory type annotations (`ANN`) and exception
  message rules (`EM`: assign the message to a variable before raising).
- **ty** (`ty.toml`) — Astral's type checker, rooted at `./src`.
- **Pytest** (`pytest.toml`) — test runner for every test level (see [`tests.md`](tests.md)).
- **pytest-cov** (`.coveragerc`) — test coverage measurement; fails below 80%.
- **Playwright** (`pytest-playwright`) — browser automation for end-to-end tests.
- **structlog** — structured logging (see the [`wide-event-logging`](../skills/wide-event-logging/SKILL.md) skill).
- **Poe the Poet** (`poe_tasks.toml`) — task runner; runs tasks through uv.
- **Zensical** (`zensical.toml`) — documentation site generator.

## Available tasks (`uv run poe <task>`)

| Task          | What it does                                                         |
| ------------- | -------------------------------------------------------------------- |
| `sync`        | `uv sync --all-groups`                                               |
| `lint`        | `ruff check` (applies safe fixes automatically)                      |
| `format`      | `ruff format`                                                        |
| `typecheck`   | `ty check`                                                           |
| `check`       | Lint, formatting and type checks without modifying any file          |
| `test`        | `pytest --maxfail=1 --cov` (fails below 80% coverage)                |
| `docs`        | `zensical serve` (local server at `localhost:3000`)                  |
| `build`       | Cleans `dist/` and runs `uv build --no-sources`                      |
| `clean`       | Removes `dist/`, caches, coverage data and `docs/_build/`            |
| `test-deploy` | check → test → build → publish to TestPyPI                           |
| `deploy`      | check → test → build → publish to PyPI                               |

Useful direct commands: `uv run ruff check`, `uv run ruff format`, `uv run ty check`, `uv run pytest`.
