---
name: cloak-cli-batch
description: Use when executing multi-step browser automation flows that need to share a single humanize session — login sequences, form workflows, data extraction pipelines. Use when separate `cloak-cli run` calls would break natural mouse/keyboard continuity. Also use when optimizing for speed (one CDP connection vs many).
---

# CloakCLI — Batch Execution

## Overview

`batch` executes multiple commands in a **single CDP connection** with **one humanize session**. Mouse trajectory stays continuous, typing patterns stay natural. Faster than separate `run` calls (one connection, not N).

**When to use batch:** multi-step login flows, data extraction pipelines, any flow where humanize continuity matters.

**When NOT to use batch:** single isolated actions (use `run <cmd>` directly), flows needing real-time human decisions between steps.

> **Prerequisite:** Profile must be launched via [[cloak-cli-profiles]]. For single isolated actions, use [[cloak-cli-automation]] directly.

## Batch JSON Format

Commands array: `["command", "arg1", "arg2", ...]` — compatible with agent-browser format. **All args are strings.**

```json
[
  ["open", "https://example.com/login"],
  ["snapshot", "-i"],
  ["fill", "#email", "user@example.com"],
  ["fill", "#password", "secret123"],
  ["click", "#submit"],
  ["wait", "3000"],
  ["snapshot", "-i"],
  ["screenshot", "logged-in.png"]
]
```

**Supported commands:** `open`, `back`, `click`, `type`, `fill`, `screenshot`, `snapshot`, `get`, `wait`

**Snapshot flags:** pass as string args: `["snapshot", "-i"]` or `["snapshot", "-i", "-c"]`. Must match literal `-i`, `-c`, `-d`, `-s` — not `--interactive`.

**Wait:** numeric string = milliseconds: `["wait", "2000"]`. Selector string = wait for element: `["wait", "#result"]`. Must be string `"2000"`, not integer `2000`.

## Workflow: Execute a Batch

```bash
# Default (humanized) — natural mouse/keyboard across all steps
cloak-cli run <id> batch commands.json

# Fast mode — skip humanize, all commands execute instantly
cloak-cli run <id> --fast batch commands.json

# JSON output — see per-command results
cloak-cli run <id> --json batch commands.json
```

**Default output:**
```
1. open OK
2. snapshot OK
3. fill OK
...
```

**JSON output:** Array of results. `null` = success, `{"error": "..."}` = failure.

## Scenario Templates

### Login + Dashboard
```json
[
  ["open", "https://example.com/login"],
  ["fill", "#username", "myuser"],
  ["fill", "#password", "mypass"],
  ["click", "#login-btn"],
  ["wait", "3000"],
  ["snapshot", "-i"],
  ["screenshot", "dashboard.png"]
]
```

### Data Extraction
```json
[
  ["open", "https://example.com/data"],
  ["wait", "2000"],
  ["snapshot", "-i"],
  ["get", "text", ".result-count"],
  ["screenshot", "data-page.png"]
]
```

### Multi-Page Navigation
```json
[
  ["open", "https://example.com/page1"],
  ["snapshot", "-i"],
  ["click", "@e5"],
  ["wait", "2000"],
  ["snapshot", "-i"],
  ["screenshot", "page2.png"],
  ["back"],
  ["wait", "1000"]
]
```

### Form with Validation
```json
[
  ["open", "https://example.com/form"],
  ["fill", "#name", "Test User"],
  ["fill", "#email", "test@example.com"],
  ["click", "#submit"],
  ["wait", "2000"],
  ["get", "text", ".success-message"],
  ["screenshot", "submitted.png"]
]
```

## Best Practices

1. **Start with `open` or `snapshot`** — confirm page state before interacting
2. **Insert `wait` after navigation** — pages need time to load; 2-3s or wait for a selector
3. **Add `screenshot` checkpoints** — after critical steps for debugging
4. **Use `--fast` only for testing** — humanized mode avoids detection
5. **Validate JSON before running:** `python -m json.tool commands.json`
6. **Single `--fast` per batch** — applies to entire batch, can't mix modes
7. **Use `fill` not `type` for login forms** — `fill` clears the field first

## Error Handling

Batch **continues on error** — one failed command doesn't stop the rest.

```bash
# Run with --json to see per-command status
cloak-cli run <id> --json batch commands.json
# → [null, null, {"error": "Element not found: #bad-selector"}, null, ...]
```

**null** = success. **{"error": "..."}** = that command failed, subsequent commands still run.

**Debugging failed batches:**
1. Add `screenshot` before the failing step
2. Add `snapshot -i` to see what elements are actually on page
3. Check `wait` durations — page might not be loaded yet

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| JSON syntax error | Validate: `python -m json.tool commands.json` |
| `wait` value is integer, not string | Must be `["wait", "2000"]`, not `["wait", 2000]` |
| Snapshot flag wrong format | Use `-i` not `--interactive`; `-c` not `--compact` |
| Forgetting `wait` after navigation | Insert `["wait", "2000"]` after `["open", ...]` |
| `type` instead of `fill` for login | `fill` clears first — better for form fields |
| Expecting batch to stop on error | Batch continues; check `--json` output |
| Mixing humanized and fast | `--fast` is all-or-nothing for the batch |
| Command not supported | Only: `open`, `back`, `click`, `type`, `fill`, `screenshot`, `snapshot`, `get`, `wait` |
