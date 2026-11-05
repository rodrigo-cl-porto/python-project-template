---
description: Minimalism and via negativa (focus on the essential, no structure for its own sake, simple and readable code, remove before adding, fix bugs by subtraction first). Always loaded, because it governs every change, whether code, tests, configuration or documentation.
alwaysApply: true
---

# Minimalism

How every agent must approach a change in this repository. It complements [`AGENTS.md`](../../AGENTS.md) and takes precedence over any convention whenever following the convention would add code that the problem does not need.

## 1. Focus on the problem, not on the structure

Start from the need and stop when it is satisfied. The goal is a solution that meets every requirement and constraint of the specified product and that a human can read, review and maintain quickly, not an elaborate system that shows what is possible.

- **Never create patterns, layers, classes, abstractions or files just to follow a convention.** A port, a factory or a new module is justified only by a real problem it solves today (high coupling, a wrong dependency direction, duplicated logic), never by a hypothetical future need.
- **Build only what was asked.** No speculative options, parameters, configuration flags, extension points or "just in case" fallbacks.
- **Less is more.** Between two solutions that satisfy the requirements, choose the one with less code, fewer moving parts and fewer concepts to learn.

## 2. Question every addition

Before introducing any line, ask whether it is really necessary and criticize your own proposal: what breaks if it is not written? If the answer is "nothing", do not write it. Prefer reusing what already exists in the codebase or in the standard library over writing something new.

## 3. Operate by via negativa

Prefer subtraction to addition, i.e., _via negativa_. Each added line carries an iatrogenic risk: it can interact with the rest of the system in unknown ways, create new bugs and demand even more code to fix them, starting an undesirable loop of new layers and unexpected results. Removing code eliminates that risk instead of compounding it.

- **When you find a bug, first check whether removing the faulty code fixes it** before adding anything. Only add code when subtraction cannot solve the problem.
- When a change makes code, tests, dependencies, configuration or documentation obsolete, delete them in the same change.
- When simplifying, deleting is better than rewriting, and rewriting is better than wrapping.

❌ Undesirable (the bug is patched by adding a second layer of logic):

```python
def active_vessels(self) -> list[Vessel]:
    vessels = [vessel for vessel in self._vessels if vessel.is_active]
    vessels += [vessel for vessel in self._legacy_vessels if vessel.is_active]
    return list({vessel.imo: vessel for vessel in vessels}.values())  # fixes duplicates
```

✅ Fixed (the duplicates came from the obsolete legacy source, so it is removed):

```python
def active_vessels(self) -> list[Vessel]:
    return [vessel for vessel in self._vessels if vessel.is_active]
```

## 4. Write simple, direct and readable code

Short code is a means to readability, never a goal that sacrifices it. Write code that reads top to bottom with no surprises.

- **Use comprehensions** (list, dict, set and generator expressions) instead of building collections with loops and `append`: they take fewer lines and state the intent directly. Split a comprehension that needs nested loops or several conditions into well-named steps.
- Prefer the standard library and built-ins (`sum`, `any`, `all`, `next`, `max`, `sorted`, `zip`, `enumerate`) to hand-written loops.
- Respect the limits that keep code reviewable: at most 30 lines per function, 100 lines per file and 4 parameters per function, as defined in [`code-standards.md`](code-standards.md). Meet them by removing and simplifying first, and only then by splitting.

❌ Undesirable:

```python
totals = {}
for report in reports:
    if report.is_valid:
        totals[report.vessel] = report.consumption
```

✅ Fixed:

```python
totals = {report.vessel: report.consumption for report in reports if report.is_valid}
```
