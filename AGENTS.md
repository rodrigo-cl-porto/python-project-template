# AGENTS.md

Instructions for AI agents (LLMs) working in this repository. Read this file in full at the start of every session.

## Language: always English

**Everything must be written in English. This rule is ESSENTIAL and has no exceptions.** It applies even when the
user writes or asks in any other language (Portuguese, Spanish, etc.):

- Responses and explanations given to the user.
- Source code: identifiers (variables, functions, classes, modules, packages), comments and docstrings.
- Tests, including test names and assertion messages.
- Documentation in `docs/`, `README.md` and any other Markdown file.
- Log messages, exception messages and user-facing strings (unless the product explicitly requires localization,
  which must then be done through a proper i18n mechanism, never by hardcoding non-English strings).
- Commit messages, branch names, pull request titles and descriptions, issues and code review comments.
- Configuration files and their comments.

**Why:** English is the current lingua franca of software development, the language in which people from any
country can understand each other. The vast majority of frameworks, libraries and their documentation are written in
English, including every tool used by this repository (Python, uv, Ruff, ty, Pytest, Zensical). Writing everything in
English keeps the codebase consistent with its ecosystem and accessible to any contributor.

## Project context

This repository is a **template for Python projects**. It is the starting point for new projects, so the structure,
conventions and tools described here must be preserved and followed.

- **Default language: Python.** If no technology is explicitly mentioned, assume every question or task is about
  Python. Always prefer libraries, frameworks and dependencies from the Python ecosystem.
- **Python version:** 3.13 (see `.python-version` and `requires-python` in `pyproject.toml`).
- **Package name:** `my-awesome-project` (imported as `my_awesome_project`). It is a placeholder name that will be
  renamed in each project derived from this template.

## Repository structure

**Before creating, moving or renaming any file or folder, read and follow
[`.agents/rules/repo-structure.md`](.agents/rules/repo-structure.md).** It defines the folder and file layout of the
repository and the role of each folder (`src/`, `tests/`, `docs/`, `.agents/rules/` and the root `*.toml` files).
Keep it up to date whenever the structure changes.

@.agents/rules/repo-structure.md

## Development environment

Dependencies and environments are managed **exclusively with [uv](https://docs.astral.sh/uv/)**; **never** use
`pip`, `requirements.txt`, `poetry` or `conda`. **Before installing, adding, removing or upgrading dependencies, or
running the development tools, read and follow
[`.agents/rules/dev-environment.md`](.agents/rules/dev-environment.md).** It defines the uv commands and dependency
groups, the development tools (Ruff, ty, Pytest, pytest-cov, Playwright, structlog, Poe the Poet, Zensical) and the
Poe the Poet tasks (`uv run poe <task>`).

@.agents/rules/dev-environment.md

## Code standards

**Before writing or reviewing any code, read and follow
[`.agents/rules/code-standards.md`](.agents/rules/code-standards.md).** It defines the code conventions (Python
3.13+ syntax, mandatory type annotations, Google-style docstrings, Ruff rules) and the Clean Code rules, with
undesirable and fixed examples: no magic numbers, intention-revealing names, small functions, guard clauses (early
return), no `break`/`continue` or tautologies such as `while True`, classes to group related logic, specific
exceptions, DRY and meaningful comments.

@.agents/rules/code-standards.md

## Architecture

**Before creating, modifying, designing or reviewing any file inside `src/`, always use the
[`architecture-standards`](.agents/skills/architecture-standards/SKILL.md) skill.** It defines the preferred
architectural patterns (**Clean Architecture**, **Ports and Adapters** and **Domain-Driven Design**) and the **SOLID**
principles, with undesirable and fixed examples: the recommended package layout, the Dependency Rule
(`adapters → application → domain`), ports defined with `typing.Protocol`, dependency injection through the
constructor, and rich domain models with entities, value objects and aggregates. Do not load it for changes outside
`src/` or for changes that touch only Markdown files.

## Automated tests

**Every piece of code must be covered by automated tests, with at least 80% coverage. This rule is CRITICAL.** Before
writing or reviewing any test, read and follow [`.agents/rules/tests.md`](.agents/rules/tests.md). It defines the
testing rules, with undesirable and fixed examples: mandatory Pytest tests, minimum coverage, focus on critical
behaviors, the FIRST principles (Fast, Independent, Repeatable, Self-validating, Timely), the Arrange/Act/Assert
(Given/When/Then) structure and the test pyramid split into `tests/unit/`, `tests/integration/` and `tests/e2e/`.

@.agents/rules/tests.md

## Logging: wide events with structlog

**Before writing or reviewing any code that emits logs, use the
[`wide-event-logging`](.agents/skills/wide-event-logging/SKILL.md) skill.** Use it whenever the application must
record an event it generates (request, CLI command, job, use case) or receives or may run into an external event
(webhook, queue message, scheduled trigger, calls to or failures of external services). Logs follow the **wide events**
(canonical log lines) convention proposed by **[Logging Sucks](https://loggingsucks.com/)**: one structured JSON event
per unit of work, emitted once at the end with **structlog** and always persisted to a **`.jsonl`** file in the
**`logs/`** folder at the repository root (ignored by Git), always including the execution date and time
(`timestamp`), the file and the method or function where the main event occurred (`origin.file` and
`origin.function`), and tail sampling to decide which events to keep.

## Commit messages: Conventional Commits

**Before writing any commit message, read and follow
[`.agents/rules/commit-conventions.md`](.agents/rules/commit-conventions.md).** Every commit message follows
**[Conventional Commits 1.0.0](https://www.conventionalcommits.org/en/v1.0.0/)**
(`<type>[optional scope][!]: <description>`). The file defines the allowed types and their SemVer impact and the rules
for scope, description, body, footers and breaking changes, with examples.

@.agents/rules/commit-conventions.md

## Versioning: Semantic Versioning

**Before bumping or reading the version of the solution, read and follow
[`.agents/rules/versioning.md`](.agents/rules/versioning.md).** The version follows
**[Semantic Versioning 2.0.0](https://semver.org/)** (`MAJOR.MINOR.PATCH`), its single source of truth is the
`version` field in `pyproject.toml`, and it is bumped only with `uv version --bump <part>`. The file defines when to
bump each part, pre-releases, build metadata and how to derive the bump from the Conventional Commits.

@.agents/rules/versioning.md

## Checklist before finishing a task

1. Everything written (code, comments, docs, messages, commits) is in **English**.
2. `uv run poe check` passes (Ruff lint, Ruff formatting and ty type checks).
3. The changed behavior is covered by tests following [`.agents/rules/tests.md`](.agents/rules/tests.md), and
   `uv run poe test` passes with at least 80% coverage.
4. The rules in `.agents/rules/code-standards.md` and, for changes inside `src/`, the `architecture-standards` skill
   (Dependency Rule and SOLID principles) are respected.
5. Logs are emitted as wide events with structlog and persisted to `.jsonl` files in `logs/` (repository root,
   listed in `.gitignore`), following the `wide-event-logging` skill (including `timestamp`, `origin.file` and
   `origin.function`).
6. Commits follow Conventional Commits, and the version is bumped according to SemVer when releasing.
7. Documentation in `docs/` is updated when the change affects the public usage of the solution.
8. `.agents/rules/repo-structure.md` is updated when files or folders are added, renamed or removed.
