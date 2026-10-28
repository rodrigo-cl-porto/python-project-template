# Python Project Template

[![uv](https://img.shields.io/endpoint?style=flat&url=https://raw.githubusercontent.com/Onyx-Nostalgia/uv/refs/heads/fix/logo-badge/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![ty](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ty/main/assets/badge/v0.json)](https://github.com/astral-sh/ty)
[![Zensical](https://img.shields.io/pypi/v/zensical?logo=python&logoColor=white&label=Zensical)](https://pypi.org/project/zensical/)
[![Poe the Poet](https://img.shields.io/pypi/v/poethepoet.svg?label=Poe%20the%20Poet)](https://pypi.org/project/poethepoet/)
[![Pytest](https://img.shields.io/pypi/v/pytest.svg?label=Pytest)](https://pypi.org/project/pytest/)

A template for starting any Python project with readiness: a modern toolchain, opinionated conventions and automation
already wired together, so a new project can focus on its own problem from the first commit.

> [!IMPORTANT]
> **Do NOT clone or fork this repository to start a new project.**
> Click the green **"Use this template"** button at the top of this repository's page on GitHub and choose **"Create a new repository"**.
> This creates an independent repository with a clean Git history, not linked to this template.
> See [Getting started](#getting-started).

## Goal

This repository is the **starting point for new Python projects**. Instead of configuring packaging, linting, type
checking, testing, documentation and publishing from scratch every time, you create a new repository from this
template (with the **"Use this template"** button), rename the placeholder package (`my-awesome-project`, imported as `my_awesome_project`) and start writing code.

It provides:

- A **`src` layout** package, typed (PEP 561) and ready to be built and published to PyPI.
- **One configuration file per tool** at the repository root, keeping `pyproject.toml` for metadata and dependencies.
- **Quality gates**: linting, formatting, type checking and tests with a minimum of **80% coverage**.
- A **documentation site** generated from Markdown files and Google-style docstrings.
- **CI/CD workflows** that publish the package to TestPyPI and PyPI.
- **Instructions for AI agents** (`AGENTS.md` and `.agents/`) describing the conventions every contribution must
  follow: Clean Code, Clean Architecture, the test pyramid, wide-event logging, Conventional Commits and Semantic
  Versioning.

## Prerequisites: install uv globally

Every dependency, virtual environment and Python interpreter in this project is managed by **[uv](https://docs.astral.sh/uv/)**.
**If uv is not installed on your machine yet, install it globally before doing anything else:**

```bash
# macOS and Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

```powershell
# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Check the installation with `uv --version`. See the
[uv installation guide](https://docs.astral.sh/uv/getting-started/installation/) for other methods. You do **not**
need to install Python yourself: uv downloads the version pinned in `.python-version` (3.13) automatically.

> Do not use `pip`, `requirements.txt`, `poetry` or `conda` in this project; uv replaces all of them.

## Getting started

### 1. Create your repository from the template

> [!WARNING]
> **Do not run `git clone` on this repository and do not fork it.** A clone keeps this template as the `origin`
> remote, and a fork stays linked to it (pull requests default to the template, and the full history comes along).
> Neither is meant for starting a new project.

1. On this repository's page on GitHub, click the green **"Use this template"** button.
2. Select **"Create a new repository"**.
3. Choose the owner and name of your new repository (e.g. `my-awesome-project`) and click **"Create repository"**.

See GitHub's guide on
[creating a repository from a template](https://docs.github.com/repositories/creating-and-managing-repositories/creating-a-repository-from-a-template)
for details.

### 2. Clone **your new repository** and set it up

Clone the repository you just created (not this template):

```bash
git clone https://github.com/<your-user>/my-awesome-project.git
cd my-awesome-project
uv sync --all-groups      # Creates .venv and installs every dependency group
uv run poe check          # Lint, formatting and type checks
uv run poe test           # Tests with coverage (fails below 80%)
```

Then rename `my-awesome-project` / `my_awesome_project` and update the metadata (description, authors and
URLs) in `pyproject.toml`.

## Frameworks

This template is built on some of the most modern frameworks of the Python ecosystem, focused on speed, simplicity and
a single, consistent workflow.

### Astral toolchain: uv, Ruff and ty

[![uv](https://img.shields.io/endpoint?style=flat&url=https://raw.githubusercontent.com/Onyx-Nostalgia/uv/refs/heads/fix/logo-badge/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![ty](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ty/main/assets/badge/v0.json)](https://github.com/astral-sh/ty)

[Astral](https://astral.sh/) builds extremely fast Python tooling written in Rust. The template uses its three main
tools, which replace a whole set of older tools with a few consistent commands:

| Framework | What it does in the template | Replaces | Configuration |
| --------- | ---------------------------- | -------- | ------------- |
| [uv](https://docs.astral.sh/uv/) | Package and project manager: installs Python itself, creates the virtual environment, resolves and locks the dependencies (`uv.lock`), runs commands (`uv run`), bumps the version (`uv version --bump`), and builds and publishes the package. Its build backend, [uv_build](https://docs.astral.sh/uv/concepts/build-backend/), turns `src/` into a wheel and a source distribution. | pip, pip-tools, virtualenv, pyenv, Poetry, setuptools, twine | `uv.toml`, `pyproject.toml` |
| [Ruff](https://docs.astral.sh/ruff/) | Linter and formatter in a single tool, with many rule sets enabled (including mandatory type annotations), 120-character lines and safe automatic fixes. | Flake8 and its plugins, isort, Black, pyupgrade | `ruff.toml` |
| [ty](https://docs.astral.sh/ty/) | Static type checker that validates the type annotations of the typed package (`py.typed`). | mypy, Pyright | `ty.toml` |

### Zensical: documentation site

[![Zensical](https://img.shields.io/pypi/v/zensical?logo=python&logoColor=white&label=Zensical)](https://pypi.org/project/zensical/)

[Zensical](https://zensical.org/) is the modern successor of MkDocs and Material for MkDocs, created by the same team.
It builds the documentation site from the Markdown files in `docs/`, while
[mkdocstrings](https://mkdocstrings.github.io/) generates the API reference from the Google-style docstrings in
`src/`. Run `uv run poe docs` to preview the site locally. Configuration: `zensical.toml`.

### Poe the Poet: task runner

[![Poe the Poet](https://img.shields.io/pypi/v/poethepoet.svg?label=Poe%20the%20Poet)](https://pypi.org/project/poethepoet/)

[Poe the Poet](https://poethepoet.natn.io/) defines the project's common commands as named tasks, executed through uv
with `uv run poe <task>`. Single commands, shell scripts and sequences of tasks (such as `check` → `test` → `build` →
`publish`) are declared in TOML, without Makefiles or OS-specific scripts. Configuration: `poe_tasks.toml` (see
[Available tasks](#available-tasks)).

### Testing and logging

[![Pytest](https://img.shields.io/pypi/v/pytest.svg?label=Pytest)](https://pypi.org/project/pytest/)
[![pytest-cov](https://img.shields.io/pypi/v/pytest-cov.svg?label=pytest-cov)](https://pypi.org/project/pytest-cov/)
[![pytest-playwright](https://img.shields.io/pypi/v/pytest-playwright.svg?label=pytest-playwright)](https://pypi.org/project/pytest-playwright/)
[![structlog](https://img.shields.io/pypi/v/structlog.svg?label=structlog)](https://pypi.org/project/structlog/)

| Framework | What it does in the template | Configuration |
| --------- | ---------------------------- | ------------- |
| [Pytest](https://docs.pytest.org/) | Test runner for unit, integration and end-to-end tests. | `pytest.toml` |
| [pytest-cov](https://pytest-cov.readthedocs.io/) | Measures branch coverage and fails the test run below 80%. | `.coveragerc` |
| [Playwright](https://playwright.dev/python/) | Browser automation for end-to-end tests (add it with `uv add --group dev pytest-playwright` when needed). | — |
| [structlog](https://www.structlog.org/) | Structured logging as wide events persisted to `.jsonl` files in `logs/` (add it with `uv add structlog` when needed). | — |

## Repository features

Besides the frameworks, the repository comes with ready-to-use integrations:

- **CI/CD with [GitHub Actions](https://docs.github.com/actions)** (`.github/workflows/`): builds the package with uv
  and publishes it to TestPyPI on every push to `main`, and to PyPI when a GitHub release is published, using trusted
  publishing (OIDC) instead of stored tokens.
- **Documentation hosting on [Read the Docs](https://about.readthedocs.com/)** (`.readthedocs.yaml`): builds the
  Zensical site with uv and publishes it online.
- **Recommended VS Code extensions** (`.vscode/extensions.json`): Python, Ruff, ty, TOML support and other editor
  helpers, suggested when the folder is opened in [VS Code](https://code.visualstudio.com/).
- **Instructions for AI agents** (`AGENTS.md`, `.agents/` and `.claude/`): LLM-agnostic rules and skills that teach AI
  coding assistants the conventions of the repository (see [Conventions](#conventions)).

## Available tasks

Run any task with `uv run poe <task>`:

| Task          | What it does                                                 |
| ------------- | ------------------------------------------------------------ |
| `sync`        | Installs all dependency groups (`uv sync --all-groups`).     |
| `lint`        | Lints the code with Ruff, applying safe fixes.               |
| `format`      | Formats the code with Ruff.                                  |
| `typecheck`   | Checks the types with ty.                                    |
| `check`       | Lint, formatting and type checks without modifying files.    |
| `test`        | Runs the tests with coverage (fails below 80%).              |
| `docs`        | Serves the documentation site locally.                       |
| `build`       | Builds the package into `dist/`.                             |
| `clean`       | Removes `dist/`, caches, coverage data and `docs/_build/`.   |
| `test-deploy` | check → test → build → publish to TestPyPI.                  |
| `deploy`      | check → test → build → publish to PyPI.                      |

Publishing tasks read the tokens from a local `.env` file, which is ignored by Git.

## Repository structure

```mermaid
treeView-beta
  .agents/ ## Rules and skills for AI agents (LLM-agnostic)
  .claude/ ## Exposes the agent skills to Claude Code
  .github/workflows/ ## Publishing to TestPyPI and PyPI
  .vscode/ ## Recommended VS Code extensions
  docs/ ## Documentation site (Zensical)
  src/
    main.py ## Application entry point
    my_awesome_project/ ## Main package
    py.typed ## Marks the package as typed (PEP 561)
  tests/
    unit/ ## Fast, isolated tests without I/O
    integration/ ## Adapters against real infrastructure
    e2e/ ## Critical user journeys (Playwright)
  AGENTS.md ## Instructions for AI agents
  pyproject.toml ## Metadata, dependencies and build backend
  *.toml ## One configuration file per tool
```

The complete, annotated tree lives in [`.agents/rules/repo-structure.md`](.agents/rules/repo-structure.md).

## Conventions

- **Code:** Python 3.13+ syntax, mandatory type annotations, Google-style docstrings and Clean Code rules
  ([`code-standards.md`](.agents/rules/code-standards.md)).
- **Architecture:** Clean Architecture, Ports and Adapters, Domain-Driven Design and SOLID
  ([`architecture-standards`](.agents/skills/architecture-standards/SKILL.md)).
- **Tests:** Pytest, at least 80% coverage, FIRST principles, Arrange/Act/Assert and the test pyramid
  ([`tests.md`](.agents/rules/tests.md)).
- **Logging:** wide events with structlog saved to `logs/*.jsonl`
  ([`wide-event-logging`](.agents/skills/wide-event-logging/SKILL.md)).
- **Commits:** [Conventional Commits](https://www.conventionalcommits.org/)
  ([`commit-conventions.md`](.agents/rules/commit-conventions.md)).
- **Versioning:** [Semantic Versioning](https://semver.org/), bumped with `uv version --bump <part>`
  ([`versioning.md`](.agents/rules/versioning.md)).
- **Language:** everything (code, docs, commits) is written in English.

## License

See [LICENSE.md](LICENSE.md).
