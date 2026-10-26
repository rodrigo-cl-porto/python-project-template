# Commit Conventions

Commit message conventions of this repository. They complement [`AGENTS.md`](../../AGENTS.md), and every agent must
follow them when writing or reviewing commit messages.

## Conventional Commits

Every commit message follows **[Conventional Commits 1.0.0](https://www.conventionalcommits.org/en/v1.0.0/)**:

```text
<type>[optional scope][!]: <description>

[optional body]

[optional footer(s)]
```

- **`type`** (lowercase):

  | Type       | When to use                                                   | SemVer impact |
  | ---------- | ------------------------------------------------------------- | ------------- |
  | `feat`     | A new feature                                                 | MINOR         |
  | `fix`      | A bug fix                                                     | PATCH         |
  | `docs`     | Documentation only                                            | —             |
  | `style`    | Formatting, whitespace; no code behavior change               | —             |
  | `refactor` | Code change that neither fixes a bug nor adds a feature       | —             |
  | `perf`     | Performance improvement                                       | —             |
  | `test`     | Adding or fixing tests                                        | —             |
  | `build`    | Build system or dependencies (`pyproject.toml`, `uv.lock`)    | —             |
  | `ci`       | CI configuration (`.github/workflows/`)                       | —             |
  | `chore`    | Maintenance that does not touch `src/` or `tests/`            | —             |
  | `revert`   | Reverts a previous commit                                     | —             |

- **`scope`** (optional): the affected area, in parentheses, e.g. `feat(checkout):`, `fix(parser):`.
- **`description`**: short summary in the imperative mood, lowercase, without a trailing period
  (`add order cancellation`, not `Added order cancellation.`).
- **`body`** (optional): separated by a blank line; explains *what* and *why*, not *how*.
- **`footer`** (optional): separated by a blank line, in the `Token: value` or `Token #value` format
  (e.g. `Refs: #123`, `Reviewed-by: Jane Doe`). Tokens use `-` instead of spaces.
- **Breaking changes** (SemVer MAJOR): add `!` before the `:` and/or a `BREAKING CHANGE: <description>` footer
  (`BREAKING CHANGE` must be uppercase).
- One logical change per commit.

## Examples

```text
feat(orders): add order cancellation
```

```text
fix(payment): retry charge on gateway timeout

The payment gateway occasionally times out under load. Retrying with
exponential backoff avoids failing checkouts that would succeed.

Refs: #87
```

```text
feat(api)!: return amounts in cents instead of decimals

BREAKING CHANGE: every monetary field in the API response is now an integer
number of cents.
```
