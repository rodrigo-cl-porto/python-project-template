---
name: architecture-standards
description: >-
  Architectural patterns and design principles of this repository: Clean Architecture, Ports and Adapters (Hexagonal Architecture), Domain-Driven Design, SOLID and object-oriented design with patterns (entity, value object, repository, use case, controller, strategy...) with one class per file, with the recommended package layout, the Dependency Rule (adapters -> application -> domain), ports defined with typing.Protocol and dependency injection through the constructor. Always use before creating, modifying, designing or reviewing any file inside the src/ folder. Do not use for changes outside src/ or for changes that touch only Markdown files.
paths:
  - "src/**/*.py"
---

# Architecture Standards

This skill is kept LLM-agnostic in [`.agents/skills/architecture-standards/SKILL.md`](../../../.agents/skills/architecture-standards/SKILL.md). Read that file in full and follow it. Do not add instructions here.
