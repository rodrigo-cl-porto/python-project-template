---
name: wide-event-logging
description: Implement logging as wide events (canonical log lines) with structlog, always persisted to .jsonl files in the logs/ folder at the repository root. Use when code must log or record an event produced by the application (a request, CLI command, job, use case or business operation), when the application receives or may run into an external event (webhook, queue message, scheduled trigger, file arrival, calls to or failures of external APIs, databases and other services), or when writing or reviewing code that emits logs.
---

# Wide Event Logging

This skill is kept LLM-agnostic in [`.agents/skills/wide-event-logging/SKILL.md`](../../../.agents/skills/wide-event-logging/SKILL.md). Read that file in full and follow it. Do not add instructions here.
