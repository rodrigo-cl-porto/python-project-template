# Versioning

Versioning conventions of this repository. They complement [`AGENTS.md`](../../AGENTS.md) and
[`commit-conventions.md`](commit-conventions.md), and every agent must follow them when bumping or reading the version
of the solution.

## Semantic Versioning

The solution's version follows **[Semantic Versioning 2.0.0](https://semver.org/)** in the `MAJOR.MINOR.PATCH`
format. The single source of truth is the `version` field in `pyproject.toml`; read it at runtime with
`importlib.metadata.version("my-awesome-project")` instead of duplicating it in the code.

- **MAJOR** — incompatible (breaking) changes to the public API.
- **MINOR** — new backwards-compatible functionality.
- **PATCH** — backwards-compatible bug fixes.
- **Pre-releases** append a hyphen and identifiers: `1.0.0-alpha.1`, `1.0.0-rc.1`. **Build metadata** appends a plus
  sign: `1.0.0+20260115`.
- **`0.y.z`** is initial development: the public API is not stable yet and anything may change. Release `1.0.0` when
  the public API is stable.
- A released version is immutable: any change requires a new version.
- Derive the bump from the [Conventional Commits](commit-conventions.md) since the last release:
  `BREAKING CHANGE`/`!` → MAJOR, `feat` → MINOR, `fix` → PATCH.

## Bumping the version

Bump the version with uv (never edit it by hand):

```bash
uv version --bump patch   # 1.4.0 -> 1.4.1
uv version --bump minor   # 1.4.1 -> 1.5.0
uv version --bump major   # 1.5.0 -> 2.0.0
```
