---
name: cloak-cli-automation
description: Use when automating a running CloakBrowser profile via CLI — navigating pages, clicking, typing, filling forms, taking snapshots, extracting information, capturing screenshots, managing tabs, waiting, scrolling, or executing JavaScript. Use when the profile is already launched and you need to interact with the page.
---

# CloakCLI — Browser Automation (run)

## Overview

All page interaction via `cloak-cli run <profile-id> <command>`. Each `run` call opens one CDP connection, executes, and closes. **Humanize is on by default** — mouse moves on Bézier curves, typing has random delays. Add `--fast` to skip humanize.

**Element targeting:** prefer `@eN` references from snapshots. CSS selectors also work, but `@refs` are more reliable.

> **Prerequisite:** Profile must be launched via [[cloak-cli-profiles]]. For multi-step flows sharing a humanize session, prefer [[cloak-cli-batch]].

## Workflow: Explore and Interact

Standard pattern: **snapshot → locate → interact → verify**.

```bash
# 1. Get interactive elements with @eN references
cloak-cli run <id> snapshot -i
# Output:
#   - link "Login" [@e1] -> https://example.com/login
#   - textbox "Email" [@e2]
#   - button "Submit" [@e3]

# 2. Click using @ref
cloak-cli run <id> click "@e1"

# 3. Type into field
cloak-cli run <id> type "@e2" "search term"

# 4. Press a key
cloak-cli run <id> press "Enter"

# 5. Verify with screenshot
cloak-cli run <id> screenshot result.png
```

## Workflow: Fill and Submit a Form

```bash
# fill = clear + type (use for empty/replace)
cloak-cli run <id> fill "@e2" "user@example.com"

# type = append to existing content (preserves what's there)
cloak-cli run <id> type "@e4" "additional text"

# Form controls
cloak-cli run <id> select "@e6" "option_value"   # dropdown
cloak-cli run <id> check "@e7"                     # checkbox on
cloak-cli run <id> uncheck "@e7"                   # checkbox off

# Submit
cloak-cli run <id> click "@e8"
```

**fill vs type:** `fill` clears the field first (triple-click + Backspace) then types. Use for empty/replace. `type` appends without clearing. Use for adding to existing content.

## Workflow: Extract Information

```bash
# Page-level
cloak-cli run <id> get title          # "Example Domain"
cloak-cli run <id> get url            # "https://example.com"

# Element info (@ref or CSS selector)
cloak-cli run <id> get text "@e5"         # visible text content
cloak-cli run <id> get html "@e5"         # innerHTML
cloak-cli run <id> get value "@e5"        # current input value
cloak-cli run <id> get attr "@e5" href    # specific attribute
cloak-cli run <id> get box "@e5"          # bounding box {x, y, width, height}
cloak-cli run <id> get count ".item"      # number of matching elements

# JSON output for programmatic parsing
cloak-cli run <id> get title --json
```

## Snapshot Options

Snapshot outputs accessibility tree in agent-browser compatible format. Interactive elements get `@eN` refs.

| Command | Effect | When to Use |
|---------|--------|-------------|
| `snapshot` | Full accessibility tree | Understanding page structure |
| `snapshot -i` | Interactive elements only | Finding what to click/type |
| `snapshot -c` | Skip empty containers | Reducing noise |
| `snapshot -d 3` | Max depth 3 levels | Top-level overview |
| `snapshot -s "#main"` | Scope to CSS selector | Focus on specific area |

Combine flags: `snapshot -i -c -d 5` for compact interactive view at depth 5.

## Workflow: Tab Management

```bash
# List all tabs (t1, t2, ... with title, URL, active marker)
cloak-cli run <id> tab

# New tab
cloak-cli run <id> tab new "https://example.com"
cloak-cli run <id> tab new                    # blank tab

# Switch tabs
cloak-cli run <id> tab switch t2

# Close tab
cloak-cli run <id> tab close t1               # specific tab
cloak-cli run <id> tab close                  # current tab

# New window
cloak-cli run <id> window new
```

## Workflow: Wait and Scroll

```bash
# Wait for time (milliseconds)
cloak-cli run <id> wait 2000

# Wait for element to appear
cloak-cli run <id> wait "#result"

# Wait for element to disappear
cloak-cli run <id> wait "#spinner" --state hidden

# Wait for network idle
cloak-cli run <id> wait --load networkidle

# Scroll
cloak-cli run <id> scroll down 300
cloak-cli run <id> scroll up 200

# Scroll element into view
cloak-cli run <id> scrollintoview "@e10"

# Execute JavaScript
cloak-cli run <id> eval "document.title"
cloak-cli run <id> eval "document.title" --json
```

## Command Reference

### Navigation (all support `--fast`)

| Command | Args |
|---------|------|
| `open <url>` | URL to navigate to |
| `back` | — |
| `forward` | — |
| `reload` | — |

### Interaction (all support `--fast`)

| Command | Args | Notes |
|---------|------|-------|
| `click <sel>` | @ref or CSS | Humanized Bézier curve |
| `dblclick <sel>` | @ref or CSS | Double click |
| `type <sel> <text>` | @ref, text | Appends to existing content |
| `fill <sel> <text>` | @ref, text | Clears first, then types |
| `press <key>` | Key name | Enter, Tab, Escape, Control+a, ArrowUp, etc. |
| `hover <sel>` | @ref or CSS | Mouse hover |
| `focus <sel>` | @ref or CSS | Keyboard focus |
| `select <sel> <value>` | @ref, option value | Dropdown select |
| `check <sel>` | @ref or CSS | Check checkbox |
| `uncheck <sel>` | @ref or CSS | Uncheck checkbox |

### Information

| Command | Args | Notes |
|---------|------|-------|
| `get text <sel>` | @ref or CSS | Visible text; `--json` |
| `get html <sel>` | @ref or CSS | innerHTML; `--json` |
| `get value <sel>` | @ref or CSS | Input value; `--json` |
| `get attr <sel> <name>` | @ref, attr name | e.g., `href`, `src`; `--json` |
| `get title` | — | Page title; `--json` |
| `get url` | — | Current URL; `--json` |
| `get count <sel>` | CSS selector | Match count; `--json` |
| `get box <sel>` | @ref or CSS | Bounding box; `--json` |

### Capture

| Command | Args | Notes |
|---------|------|-------|
| `snapshot` | `-i`, `-c`, `-d <n>`, `-s <css>` | Accessibility tree |
| `screenshot [path]` | `--full` | Default: `screenshot-<timestamp>.png` |
| `pdf <path>` | Output path | Page as PDF |

### Tab Management

| Command | Args | Notes |
|---------|------|-------|
| `tab` | `--json` | List tabs with tN indices |
| `tab new [url]` | Optional URL | Omit for blank tab |
| `tab switch <ref>` | t1, t2, ... | Switch by index |
| `tab close [ref]` | Optional ref | Omit for current |
| `window new` | — | New browser window |

### Utility

| Command | Args | Notes |
|---------|------|-------|
| `wait <ms>` | Numeric ms | e.g., `wait 2000` |
| `wait <sel>` | CSS selector | Wait for element visible |
| `wait <sel> --state hidden` | CSS selector | Wait for element gone |
| `wait --load networkidle` | — | Wait for network idle |
| `scroll <dir> [px]` | up/down/left/right, default 300 | Smooth scroll |
| `scrollintoview <sel>` | @ref or CSS | Scroll element into view |
| `eval <js>` | JavaScript code | Execute in page; `--json` |

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| CSS selector doesn't match | Run `snapshot -i` first, use `@eN` refs |
| `type` when you meant `fill` | `fill` clears first, `type` appends |
| Forgetting `--fast` for testing | Default is humanized (slow); add `--fast` |
| Clicking before page loads | Insert `wait 2000` or `wait <sel>` after navigation |
| `snapshot` without `-i` for interaction | Full snapshot is verbose; `-i` shows only actionable elements |
| Tab index confusion | Run `tab` first to see indices (t1, t2, ...) |
| `get` without `--json` for parsing | Add `--json` when consuming output programmatically |
| Humanize on by default | Add `--fast` if you need instant execution |
