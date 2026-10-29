---
name: changelog
description: Structure and update CHANGELOG.md following Keep a Changelog 2.0.0, turning the git history since the previous version into curated, human-readable entries. Use always, and only, when the version of the solution (the version field in pyproject.toml) is bumped, e.g. with uv version --bump patch|minor|major or when releasing a new version. Do not use for any other change, including other edits to pyproject.toml or CHANGELOG.md.
---

# Changelog

Changelog conventions of this repository, based on **[Keep a Changelog 2.0.0](https://keepachangelog.com/en/2.0.0/)**. They complement [`AGENTS.md`](../../../AGENTS.md), [`versioning.md`](../../rules/versioning.md) and [`commit-conventions.md`](../../rules/commit-conventions.md).

A changelog is a **curated**, chronologically ordered list of the **notable** changes of each version, written for the people who use the software. **It is not a git log.** Commits are the raw material: read them, then decide what is notable, group it and describe it from the reader's point of view.

## When to use this skill

- **Always** when the `version` field in `pyproject.toml` is bumped (`uv version --bump <part>`), in the same task and the same commit as the bump.
- **Only** then. Do not touch `CHANGELOG.md` for regular commits, features or fixes that do not bump the version.

## Workflow

1. Read the previous version (`uv version --short`) **before** bumping, then bump it following [`versioning.md`](../../rules/versioning.md) and read the new one.
2. Find the base of the range: the tag `v<previous>` if it exists (`git tag --list "v<previous>"`); otherwise the last commit that changed the version line, `git log -1 --format=%H -G '^version = ' -- pyproject.toml`; if there is none, the whole history.
3. Read the commits of the range, including bodies and files, not only the subjects: `git log --no-merges --format="%h %s%n%b" --stat <base>..HEAD`. Inspect the diff (`git show <hash>`) whenever a message is unclear.
4. Select the notable changes and sort each one into a [type of change](#types-of-changes) (see [From commits to entries](#from-commits-to-entries)).
5. Create `CHANGELOG.md` from the [file structure](#file-structure) if it does not exist yet.
6. Move the entries of `## [Unreleased]` into a new `## [<new>] - <YYYY-MM-DD>` section, merge them with the new entries without duplicates, and leave an empty `## [Unreleased]` at the top.
7. Update the [reference links](#reference-links) at the bottom of the file.
8. Review the result as a reader would and remove anything not worth reading.
9. Commit the bump and the changelog together, e.g. `chore(release): bump version to 1.5.0`.

## File structure

The file is `CHANGELOG.md` at the repository root. It opens with this fixed header and preamble, keeps an `Unreleased` section at the top and lists the latest version first:

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/2.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.5.0] - 2026-10-28

Adds order cancellation and drops support for the legacy CSV export.

### Added

- Cancel an order before it ships with `cancel_order()`.

### Changed

- **Breaking:** `export_orders()` now returns a list of `Order` objects instead of a CSV string.

### Fixed

- Totals are no longer rounded twice when a coupon is applied.

## [1.4.0] - 2026-09-02

### Added

- Pay orders by bank transfer.

[Unreleased]: https://github.com/<owner>/<repo>/compare/v1.5.0...HEAD
[1.5.0]: https://github.com/<owner>/<repo>/compare/v1.4.0...v1.5.0
[1.4.0]: https://github.com/<owner>/<repo>/releases/tag/v1.4.0
```

- **Version heading:** `## [<version>] - <YYYY-MM-DD>`. The date is the release date (the day of the bump, from `date +%F`) in ISO 8601 format; never use regional formats.
- **Summary (optional):** one or two sentences right below the heading, before the typed sections, when the release has a theme or a headline change worth introducing. Skip it otherwise.
- **Sections:** `### <Type>` headings in the order of the [types table](#types-of-changes). Omit empty sections.
- **Entries:** one `- ` bullet per notable change, in plain, concise English, ending with a period. Describe the effect on the user, not the implementation. Mention public names in backticks.
- **Yanked releases:** a version pulled because of a serious bug or vulnerability stays listed, marked `## [0.0.5] - 2014-12-13 [YANKED]`. Never delete it.
- **Never delete old entries.** Fixing a past entry (a forgotten change, an unrecorded breaking change) is allowed.

## Types of changes

Use only these six types, in this order. Do not invent others (`Performance`, `Dependencies`, `Internal`, ...): the kind of change goes in the type, why it matters goes in the wording.

| Type         | Use for                                                    |
| ------------ | ---------------------------------------------------------- |
| `Added`      | New features.                                              |
| `Changed`    | Changes in existing functionality.                         |
| `Deprecated` | Features that will be removed in a future version.         |
| `Removed`    | Features removed in this version.                          |
| `Fixed`      | Bug fixes.                                                 |
| `Security`   | Vulnerabilities. Lead with the CVE identifier if any.      |

- **Fixed or Changed?** If the old behavior was a bug, it is `Fixed`. If it worked as intended and now works differently, it is `Changed`.
- **Security** wins over `Fixed` and `Changed` when the change addresses a vulnerability: `- CVE-2024-12345: out-of-bounds read when parsing malformed input.`
- **Dependencies** are not a type. Describe the effect of an upgrade under the right type if users notice it; otherwise leave it out.
- **Deprecations** are announced in a release (`Deprecated`, saying which version will remove them) before the removal (`Removed`) in a later one.

## Breaking changes

Breaking changes usually go under `Changed` or `Removed`. Keep them in their type, never in a separate section, and start the entry with a `**Breaking:**` marker. Say what breaks and add a short upgrade note; link to a migration guide in `docs/` when the steps are long.

```markdown
### Removed

- **Breaking:** the `legacy_export()` function. Use `export_orders()` instead.
```

The public API covered by Semantic Versioning is the public interface of the `my_awesome_project` package.

## From commits to entries

The [Conventional Commits](../../rules/commit-conventions.md) type is a hint, not a rule:

| Commit                                   | Usual changelog type                                              |
| ---------------------------------------- | ----------------------------------------------------------------- |
| `feat`                                   | `Added` (or `Changed` when it alters an existing feature)         |
| `fix`                                    | `Fixed` (or `Security` when it addresses a vulnerability)         |
| `!` or `BREAKING CHANGE:` footer         | `Changed` or `Removed`, with the `**Breaking:**` marker           |
| `perf`, `refactor`                       | `Changed` only when users notice the effect; otherwise omit       |
| `build`                                  | Omit, unless users notice it (e.g. a new minimum Python version)  |
| `revert`                                 | Drop the reverted entry if it was never released; else `Removed`  |
| `docs`, `style`, `test`, `ci`, `chore`   | Omit, unless they change what users get                           |

- **One entry per notable change**, not per commit: several commits that build one feature become a single entry.
- **Omit the noise:** merge commits, typo fixes, formatting, internal refactorings, test-only and CI-only changes.
- **Never paste commit subjects or hashes** as entries; rewrite them for the reader.
- **Be consistent:** every notable change must be there. Always record deprecations, removals and breaking changes.

❌ Undesirable — a reworded git log:

```markdown
### Added

- feat(orders): add cancel endpoint (a1b2c3d)
- fix typo in docstring
- refactor: extract OrderCanceller class
- test: add cancellation tests
```

✅ Fixed — curated for the reader:

```markdown
### Added

- Cancel an order before it ships with `cancel_order()`.
```

## Reference links

Each version heading is a Markdown reference link, resolved at the bottom of the file. Versions are tagged as `v<version>` (the tag is created when the release is published on GitHub). Build the base URL from `git remote get-url origin`, converting SSH remotes (`git@github.com:<owner>/<repo>.git`) to `https://github.com/<owner>/<repo>`.

```markdown
[Unreleased]: https://github.com/<owner>/<repo>/compare/v<new>...HEAD
[<new>]: https://github.com/<owner>/<repo>/compare/v<previous>...v<new>
[<oldest>]: https://github.com/<owner>/<repo>/releases/tag/v<oldest>
```

- `[Unreleased]` always compares the latest version to `HEAD`.
- Every version compares with the one before it; the oldest version links to its tag.
- When cutting a release, rename `Unreleased` to the new version in its link too, then add the new `[Unreleased]` link.
- Before the first release, when no version exists yet, `[Unreleased]` points to `https://github.com/<owner>/<repo>/commits/main`.
- Prefer prose over bare `(#123)` references; when linking issues or pull requests, collect them as reference links at the bottom of the file too.
