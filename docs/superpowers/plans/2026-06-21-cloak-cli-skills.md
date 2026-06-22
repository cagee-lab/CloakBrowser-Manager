# CloakCLI Agent Skills Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create three cloak-cli skills (profiles, automation, batch) following writing-skills TDD process, so agents can correctly operate CloakBrowser Manager via CLI.

**Architecture:** Each skill follows the SKILL.md format with YAML frontmatter, workflow-driven main content, and compact command reference tables. Skills live in `.claude/skills/cloak-cli-*/SKILL.md`. Testing uses subagent pressure scenarios per the writing-skills testing methodology.

**Tech Stack:** Markdown (SKILL.md), subagent-based testing (no test framework needed), CloakCLI commands as domain knowledge.

## Global Constraints

- Skills are reference/technique type (not discipline-enforcing) — testing focuses on correct command usage, not rule compliance under pressure
- YAML frontmatter: `name` uses only letters, numbers, hyphens; `description` starts with "Use when..."
- Command references match actual CloakCLI implementation (pyproject.toml v0.1.0, typer CLI)
- Output: `.claude/skills/cloak-cli-{profiles,automation,batch}/SKILL.md`
- All three skills share consistent formatting: connection setup → workflows → command reference → common mistakes

---

### Task 1: RED Phase — Baseline Test for cloak-cli-profiles

**Files:**
- Create: `.claude/skills/cloak-cli-profiles/SKILL.md` (placeholder for test)

**Interfaces:**
- Produces: Baseline test results document (no formal output, captured in conversation)

- [ ] **Step 1: Launch subagent WITHOUT skill — profile management scenario**

Dispatch a subagent with this task (no cloak-cli skill available):

```
You need to create a new CloakBrowser Manager profile with humanize enabled,
launch it, and check its status. The Manager is running at http://localhost:8080
with no auth token. Use the cloak-cli command.

Available commands: cloak-cli --help, cloak-cli profile --help, etc.
Do your best to figure out the correct commands.

What commands do you run, in what order?
```

- [ ] **Step 2: Document baseline failures**

Record verbatim what the agent does:
- Does it know `cloak-cli profile create --name "x" --humanize`?
- Does it know `cloak-cli launch <id>`?
- Does it know `cloak-cli status <id>` vs `cloak-cli status` (system)?
- Does it configure host/token correctly?
- Does it handle errors (missing profile, already running)?

- [ ] **Step 3: Launch subagent WITHOUT skill — config connection scenario**

```
You need to connect cloak-cli to a CloakBrowser Manager running at
http://192.168.1.100:9090 with auth token "abc123". You have no config
file set up. What's the fastest way to run a command?

Options:
A) cloak-cli --host http://192.168.1.100:9090 --token abc123 profile list
B) Create ~/.cloakcli/config.yaml first, then run
C) Set CLOAKBROWSER_HOST and CLOAKBROWSER_TOKEN env vars, then run
```

- [ ] **Step 4: Document baseline failures for config**

Record which option the agent chooses and whether it knows all three methods.

---

### Task 2: RED Phase — Baseline Test for cloak-cli-automation

**Files:**
- Create: `.claude/skills/cloak-cli-automation/SKILL.md` (placeholder for test)

**Interfaces:**
- Produces: Baseline test results for automation scenarios

- [ ] **Step 1: Launch subagent WITHOUT skill — form filling scenario**

```
Profile "abc123" is already running. You need to:
1. Navigate to https://example.com/login
2. Fill in email field (id="email") with "user@test.com"
3. Fill in password field (id="password") with "pass123"
4. Click the submit button (id="submit")
5. Take a screenshot to verify

You want humanized behavior. What cloak-cli commands do you run?
```

- [ ] **Step 2: Document automation baseline failures**

Record:
- Does the agent know `cloak-cli run <id> open <url>`?
- Does it use `fill` vs `type` correctly?
- Does it know about `--fast` flag?
- Does it know about `screenshot` command?
- Does it use snapshot-based @ref or CSS selectors?
- Does it know about `wait` for page load?

- [ ] **Step 3: Launch subagent WITHOUT skill — snapshot and extract scenario**

```
Profile "abc123" is running at https://news.ycombinator.com.
You need to:
1. Get a list of interactive elements on the page
2. Click the first link
3. Get the title of the new page
4. Go back

What commands do you run?
```

- [ ] **Step 4: Document snapshot baseline failures**

Record:
- Does the agent know `snapshot -i` for interactive elements?
- Does it understand @eN references?
- Does it know `get title`?
- Does it know `back`?

---

### Task 3: RED Phase — Baseline Test for cloak-cli-batch

**Files:**
- Create: `.claude/skills/cloak-cli-batch/SKILL.md` (placeholder for test)

**Interfaces:**
- Produces: Baseline test results for batch scenarios

- [ ] **Step 1: Launch subagent WITHOUT skill — multi-step automation scenario**

```
You need to automate a multi-step process on profile "abc123":
1. Go to https://example.com/login
2. Fill email
3. Fill password
4. Click login
5. Wait for dashboard
6. Take screenshot
7. Get page title

You want all steps to share one humanize session (so mouse movements
look natural across steps). What's the best approach?

Options:
A) Run each step as separate `cloak-cli run <id> <cmd>` calls
B) Create a batch JSON file and run `cloak-cli run <id> batch file.json`
C) Use the Python SDK
```

- [ ] **Step 2: Document batch baseline failures**

Record:
- Does the agent know batch exists?
- Does it understand the JSON format?
- Does it understand why batch > separate calls for humanize?
- Does it know `--fast` and `--json` flags for batch?

- [ ] **Step 3: Launch subagent WITHOUT skill — batch JSON format scenario**

```
Write a batch JSON file for the following flow on profile "abc123":
- Open https://example.com
- Take interactive snapshot
- Click element @e3
- Wait 2 seconds
- Take screenshot as "result.png"

Write the exact JSON content.
```

- [ ] **Step 4: Document batch format failures**

Record:
- Does the agent know the `[["cmd", "arg1", "arg2"], ...]` format?
- Does it handle snapshot flags (-i) correctly?
- Does it know the wait format (numeric string)?

---

### Task 4: GREEN Phase — Write cloak-cli-profiles SKILL.md

**Files:**
- Create: `.claude/skills/cloak-cli-profiles/SKILL.md`

**Interfaces:**
- Consumes: Baseline test results from Task 1 (specific failures to address)
- Produces: Complete SKILL.md with frontmatter, workflows, command reference, common mistakes

- [ ] **Step 1: Write SKILL.md with frontmatter**

```markdown
---
name: cloak-cli-profiles
description: Use when managing CloakBrowser Manager profiles via CLI — creating, listing, updating, deleting profiles, launching and stopping browsers, or checking status. Also use when configuring cloak-cli connection settings (host, token, profile switching).
---
```

- [ ] **Step 2: Write quick connection section**

Address the config scenario failures from Task 1 — make sure all three methods are clear:

```markdown
# CloakCLI — Profiles & Browser Lifecycle

## Quick Connection

Three ways to configure cloak-cli connection, highest priority first:

```bash
# 1. CLI arguments (overrides everything)
cloak-cli --host http://192.168.1.100:9090 --token abc123 profile list

# 2. Environment variables
export CLOAKBROWSER_HOST=http://localhost:8080
export CLOAKBROWSER_TOKEN=your-token

# 3. Config file (~/.cloakcli/config.yaml)
default:
  host: http://localhost:8080
  token: your-token
```

Switch config profiles with `--profile <name>` (e.g., `--profile staging`).

Check current config: `cloak-cli config show`
```

- [ ] **Step 3: Write profile management workflow**

```markdown
## Workflow: Create and Launch a Profile

```bash
# 1. Create a profile with humanize enabled
cloak-cli profile create --name "demo" --humanize
# Output: Created profile: abc123... (demo)

# 2. Launch the browser
cloak-cli launch abc123
# Shows: Status, VNC Port, Display, CDP URL

# 3. Check profile status
cloak-cli status abc123
# Shows: Status (running), VNC Port, CDP URL

# 4. Stop when done
cloak-cli stop abc123
```

## Workflow: Manage Existing Profiles

```bash
# List all profiles (table with id, name, status, proxy, tags)
cloak-cli profile list
cloak-cli profile list --json  # machine-readable

# Get full details of one profile
cloak-cli profile get abc123
cloak-cli profile get abc123 --json

# Update a profile (partial update — only specified fields change)
cloak-cli profile update abc123 --name "renamed" --no-humanize

# Delete (with confirmation)
cloak-cli profile delete abc123
cloak-cli profile delete abc123 --force  # skip confirmation

# System-wide status (all running profiles count, binary version)
cloak-cli status
cloak-cli status --json
```
```

- [ ] **Step 4: Write command reference table**

```markdown
## Command Reference

### Profile CRUD

| Command | Key Options | Notes |
|---------|------------|-------|
| `profile list` | `--json` | Table format by default |
| `profile get <id>` | `--json` | Full profile details |
| `profile create --name <n>` | `--humanize`, `--proxy <url>`, `--timezone <tz>`, `--locale <lc>`, `--platform <os>`, `--screen-width/height`, `--human-preset`, `--headless`, `--geoip`, `--auto-launch`, `--seed <n>`, `--user-agent <ua>`, `--tag k:v` | Only `--name` required |
| `profile update <id>` | `--name`, `--proxy`, `--humanize/--no-humanize`, `--human-preset`, `--headless/--no-headless` | Partial update |
| `profile delete <id>` | `--force` / `-f` | Confirms unless `--force` |

### Browser Lifecycle

| Command | Notes |
|---------|-------|
| `launch <id>` | Shows VNC port, display, CDP URL on success |
| `stop <id>` | Graceful shutdown |
| `status` | System overview: running count, total, binary version |
| `status <id>` | Profile-specific: status, VNC port, CDP URL |

### Config

| Command | Notes |
|---------|-------|
| `config show` | Current host, masked token |
| `config path` | Path to `~/.cloakcli/config.yaml` |

### Clipboard

| Command | Notes |
|---------|-------|
| `clipboard read <id>` | Read clipboard text; `--json` for `{"text": "..."}` |
| `clipboard write <id> <text>` | Write text to clipboard |
```

- [ ] **Step 5: Write common mistakes section**

```markdown
## Common Mistakes

| Mistake | Fix |
|---------|-----|
| `profile create` without `--name` | `--name` is required |
| Forgetting `--humanize` on create | Humanize is off by default; add `--humanize` |
| `status` vs `status <id>` confused | No arg = system overview; with id = profile status |
| Launching already-running profile | Check `status <id>` first |
| 401 Unauthorized | Check token with `config show`; set via `--token` or env var |
| Profile not found | Use `profile list` to see available profiles |
```

- [ ] **Step 6: Verify against baseline — re-run Task 1 scenarios with skill available**

Run the same subagent scenarios from Task 1, but this time the skill is available. Verify the agent now correctly:
- Creates profile with `--humanize`
- Launches and checks status
- Uses all three config methods
- Handles common errors

---

### Task 5: GREEN Phase — Write cloak-cli-automation SKILL.md

**Files:**
- Create: `.claude/skills/cloak-cli-automation/SKILL.md`

**Interfaces:**
- Consumes: Baseline test results from Task 2
- Produces: Complete SKILL.md

- [ ] **Step 1: Write SKILL.md with frontmatter**

```markdown
---
name: cloak-cli-automation
description: Use when automating a running CloakBrowser profile via CLI — navigating pages, clicking, typing, filling forms, taking snapshots, extracting information, capturing screenshots, managing tabs, waiting, scrolling, or executing JavaScript. Use when the profile is already launched and you need to interact with the page.
---
```

- [ ] **Step 2: Write core concepts**

```markdown
# CloakCLI — Browser Automation (run)

## Core Concepts

All automation goes through `cloak-cli run <profile-id> <command>`.

**Humanize by default:** mouse moves on Bézier curves, typing has random delays with occasional typos. Add `--fast` to skip humanize for testing.

**Element targeting:** prefer `@eN` references from snapshots. CSS selectors work too, but @refs are more reliable.

**Each `run` call = one CDP connection** that opens, executes, and closes. For multi-step flows sharing a humanize session, use `batch` (see cloak-cli-batch skill).
```

- [ ] **Step 3: Write explore-and-interact workflow**

```markdown
## Workflow: Explore and Interact

The standard pattern: snapshot → locate → interact → verify.

```bash
# 1. Get interactive elements
cloak-cli run <id> snapshot -i
# Output:
#   - link "Login" [@e1] -> https://example.com/login
#   - textbox "Email" [@e2]
#   - button "Submit" [@e3]

# 2. Click using @ref
cloak-cli run <id> click "@e1"

# 3. Type into field
cloak-cli run <id> type "@e2" "search term"

# 4. Press Enter
cloak-cli run <id> press "Enter"

# 5. Verify with screenshot
cloak-cli run <id> screenshot result.png
```
```

- [ ] **Step 4: Write form filling workflow (addresses fill vs type confusion from baseline)**

```markdown
## Workflow: Fill and Submit a Form

```bash
# fill = clear + type (for empty fields)
cloak-cli run <id> fill "@e2" "user@example.com"

# type = append to existing content (preserves what's there)
cloak-cli run <id> type "@e4" "additional text"

# Form controls
cloak-cli run <id> select "@e6" "option_value"   # dropdown
cloak-cli run <id> check "@e7"                     # checkbox
cloak-cli run <id> uncheck "@e7"                   # uncheck

# Submit
cloak-cli run <id> click "@e8"
```

**fill vs type:**
- `fill` — clears the field first (triple-click + Backspace), then types. Use for empty/replace.
- `type` — types into existing content without clearing. Use for appending.
```

- [ ] **Step 5: Write snapshot options reference**

```markdown
## Snapshot Options

The snapshot outputs an accessibility tree in agent-browser compatible format.
Each interactive element gets an `@eN` reference.

| Command | Effect | When to Use |
|---------|--------|-------------|
| `snapshot` | Full accessibility tree | Understanding page structure |
| `snapshot -i` | Interactive elements only | Finding what to click/type |
| `snapshot -c` | Skip empty containers | Reducing noise |
| `snapshot -d 3` | Max depth 3 levels | Top-level overview |
| `snapshot -s "#main"` | Scope to CSS selector | Focus on specific area |

Combine flags: `snapshot -i -c -d 5` for compact interactive view at depth 5.
```

- [ ] **Step 6: Write information extraction workflow**

```markdown
## Workflow: Extract Information

```bash
# Page-level info
cloak-cli run <id> get title        # "Example Domain"
cloak-cli run <id> get url          # "https://example.com"

# Element info (use @ref or CSS selector)
cloak-cli run <id> get text "@e5"       # visible text content
cloak-cli run <id> get html "@e5"       # innerHTML
cloak-cli run <id> get value "@e5"      # current input value
cloak-cli run <id> get attr "@e5" href  # specific attribute
cloak-cli run <id> get box "@e5"        # bounding box {x, y, width, height}
cloak-cli run <id> get count ".item"    # number of matching elements

# JSON output for machine parsing
cloak-cli run <id> get title --json
```
```

- [ ] **Step 7: Write tab management workflow**

```markdown
## Workflow: Tab Management

```bash
# List all tabs (t1, t2, ... with title, URL, active marker)
cloak-cli run <id> tab

# Open new tab
cloak-cli run <id> tab new "https://example.com"
cloak-cli run <id> tab new               # blank tab

# Switch tabs
cloak-cli run <id> tab switch t2

# Close tab
cloak-cli run <id> tab close t1          # specific tab
cloak-cli run <id> tab close             # current tab

# New window
cloak-cli run <id> window new
```
```

- [ ] **Step 8: Write command reference table**

```markdown
## Command Reference

### Navigation

| Command | Args | `--fast` |
|---------|------|----------|
| `open <url>` | URL to navigate to | ✓ |
| `back` | — | ✓ |
| `forward` | — | ✓ |
| `reload` | — | ✓ |

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
| `tab switch <ref>` | t1, t2, ... | Switch to tab by index |
| `tab close [ref]` | Optional ref | Omit for current tab |
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
```

- [ ] **Step 9: Write common mistakes**

```markdown
## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Using CSS selector that doesn't match | Run `snapshot -i` first, use `@eN` refs |
| `type` when you meant `fill` | `fill` clears first, `type` appends |
| Forgetting `--fast` for testing | Default is humanized (slow); add `--fast` |
| Clicking before page loads | Insert `wait 2000` or `wait <sel>` after navigation |
| `snapshot` without `-i` for interaction | Full snapshot is verbose; `-i` shows only actionable elements |
| Tab index confusion | Run `tab` first to see indices; use t1, t2, etc. |
| `get` without `--json` for parsing | Add `--json` when consuming output programmatically |
```

- [ ] **Step 10: Verify against baseline — re-run Task 2 scenarios with skill available**

---

### Task 6: GREEN Phase — Write cloak-cli-batch SKILL.md

**Files:**
- Create: `.claude/skills/cloak-cli-batch/SKILL.md`

**Interfaces:**
- Consumes: Baseline test results from Task 3
- Produces: Complete SKILL.md

- [ ] **Step 1: Write SKILL.md with frontmatter**

```markdown
---
name: cloak-cli-batch
description: Use when executing multi-step browser automation flows that need to share a single humanize session — login sequences, form workflows, data extraction pipelines. Use when separate `cloak-cli run` calls would break natural mouse/keyboard continuity. Also use when optimizing for speed (one CDP connection vs many).
---
```

- [ ] **Step 2: Write core concept**

```markdown
# CloakCLI — Batch Execution

## Core Concept

`batch` executes multiple commands in a single CDP connection with one humanize session. Mouse trajectory stays continuous, typing patterns stay natural. Faster than separate `run` calls (one connection, not N).

**When to use batch:**
- Multi-step login flows (navigate → fill → click → wait → verify)
- Data extraction pipelines (navigate → snapshot → extract → paginate)
- Any flow where humanize continuity matters

**When NOT to use batch:**
- Single isolated actions (use `run <cmd>` directly)
- Flows that need real-time human decisions between steps
```

- [ ] **Step 3: Write batch JSON format**

```markdown
## Batch JSON Format

Commands array of `["command", "arg1", "arg2", ...]` — compatible with agent-browser format.

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

**Supported commands in batch:** `open`, `back`, `click`, `type`, `fill`, `screenshot`, `snapshot`, `get`, `wait`

**Snapshot in batch:** pass flags as args: `["snapshot", "-i"]` or `["snapshot", "-i", "-c"]`

**Wait in batch:** numeric string = ms: `["wait", "2000"]`. Selector string = wait for element: `["wait", "#result"]`
```

- [ ] **Step 4: Write execution workflow**

```markdown
## Workflow: Execute a Batch

```bash
# Default (humanized) — natural mouse/keyboard across all steps
cloak-cli run <id> batch commands.json

# Fast mode — skip humanize, all commands execute instantly
cloak-cli run <id> --fast batch commands.json

# JSON output — see per-command results
cloak-cli run <id> --json batch commands.json
```

**Output format (default):**
```
1. open OK
2. snapshot OK
3. fill OK
4. fill OK
5. click OK
6. wait OK
7. snapshot OK
8. screenshot logged-in.png
```

**Output format (--json):** Array of results, `null` = success, `{"error": "..."}` = failure.
```

- [ ] **Step 5: Write scenario templates**

```markdown
## Scenario Templates

### Login + Navigate
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

### Form with Validation Check
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
4. **Use `--fast` only for testing** — humanized mode is what avoids detection
5. **Validate JSON before running:** `python -m json.tool commands.json`
6. **Single `--fast` per batch** — the flag applies to the entire batch, can't mix modes
```

- [ ] **Step 6: Write error handling section**

```markdown
## Error Handling

Batch continues on error — one failed command doesn't stop the rest.

```bash
# Run with --json to see per-command status
cloak-cli run <id> --json batch commands.json
# Output: [null, null, {"error": "Element not found: #bad-selector"}, null, ...]
```

**null** = success. **{"error": "..."}** = that command failed, subsequent commands still run.

**Debugging failed batches:**
1. Add `screenshot` before the failing step
2. Add `snapshot -i` to see what elements are actually on page
3. Check `wait` durations — page might not be loaded
```

- [ ] **Step 7: Write common mistakes**

```markdown
## Common Mistakes

| Mistake | Fix |
|---------|-----|
| JSON syntax error | Validate: `python -m json.tool commands.json` |
| Forgetting `wait` after navigation | Insert `["wait", "2000"]` after `["open", ...]` |
| Using `type` instead of `fill` for login forms | `fill` clears first — better for form fields |
| Expecting batch to stop on error | Batch continues; check `--json` output for failures |
| Mixing humanized and fast within one batch | `--fast` is all-or-nothing for the batch |
| Snapshot without `-i` in batch | Pass as arg: `["snapshot", "-i"]` |
| Commands not in supported list | Only `open`, `back`, `click`, `type`, `fill`, `screenshot`, `snapshot`, `get`, `wait` are supported |
```

- [ ] **Step 8: Verify against baseline — re-run Task 3 scenarios with skill available**

---

### Task 7: REFACTOR Phase — Cross-Skill Consistency and Loophole Closure

**Files:**
- Modify: `.claude/skills/cloak-cli-profiles/SKILL.md`
- Modify: `.claude/skills/cloak-cli-automation/SKILL.md`
- Modify: `.claude/skills/cloak-cli-batch/SKILL.md`

**Interfaces:**
- Consumes: GREEN phase verification results from Tasks 4-6
- Produces: Updated SKILL.md files with cross-references and consistency fixes

- [ ] **Step 1: Add cross-references between skills**

Add to each skill's overview section:

cloak-cli-profiles: Add `> **Next:** Once a profile is running, use [[cloak-cli-automation]] for page interactions or [[cloak-cli-batch]] for multi-step flows.`

cloak-cli-automation: Add `> **Prerequisite:** Profile must be launched via [[cloak-cli-profiles]]. For multi-step flows sharing a humanize session, prefer [[cloak-cli-batch]].`

cloak-cli-batch: Add `> **Prerequisite:** Profile must be launched via [[cloak-cli-profiles]]. For single isolated actions, use [[cloak-cli-automation]] directly.`

- [ ] **Step 2: Verify all command signatures match actual implementation**

Cross-check against source code:
- `profile create` options: --name, --proxy, --timezone, --locale, --platform, --screen-width, --screen-height, --humanize/--no-humanize, --human-preset, --headless/--no-headless, --geoip/--no-geoip, --auto-launch/--no-auto-launch, --seed, --user-agent, --tag, --json
- `profile update` options: --name, --proxy, --humanize/--no-humanize, --human-preset, --headless/--no-headless, --json
- `launch`, `stop`, `status` signatures
- All `run` subcommands and their flags
- `clipboard read/write` signatures
- `config show/path` signatures

- [ ] **Step 3: Run comprehensive scenario — agent uses all three skills together**

```
You have a CloakBrowser Manager at http://localhost:8080 (no auth).
Available skills: cloak-cli-profiles, cloak-cli-automation, cloak-cli-batch

Task:
1. Create a profile named "test-bot" with humanize enabled
2. Launch it
3. Navigate to https://httpbin.org/forms/post
4. Fill the form fields and submit
5. Take a screenshot of the result
6. Stop the browser

Execute this step by step using cloak-cli commands.
```

- [ ] **Step 4: Document any remaining failures and fix**

If the agent:
- Uses wrong command order → add ordering notes
- Confuses command flags → add to common mistakes
- Doesn't know to stop browser → emphasize cleanup in profiles skill
- Any other failure → fix the relevant skill and re-test

- [ ] **Step 5: Final consistency pass**

Check all three skills for:
- Same connection setup pattern
- Same @ref usage convention
- Same --fast explanation
- Same --json usage pattern
- Consistent terminology (profile-id, @eN, etc.)

- [ ] **Step 6: Commit all three skills**

```bash
git add .claude/skills/cloak-cli-profiles/SKILL.md
git add .claude/skills/cloak-cli-automation/SKILL.md
git add .claude/skills/cloak-cli-batch/SKILL.md
git commit -m "feat: add cloak-cli agent skills (profiles, automation, batch)"
```
```

---

## Self-Review

### 1. Spec Coverage
- cloak-cli-profiles: ✓ Covers config (all 3 methods), profile CRUD (create/list/get/update/delete), browser lifecycle (launch/stop/status), clipboard, config commands
- cloak-cli-automation: ✓ Covers navigation (open/back/forward/reload), all interactions (click/type/fill/press/hover/focus/select/check/uncheck), snapshot with all flags (-i/-c/-d/-s), all get variants, screenshot/PDF, tab management (tab/tab-new/tab-switch/tab-close/window-new), wait/scroll/scrollintoview/eval
- cloak-cli-batch: ✓ Covers JSON format, execution (--fast/--json), error handling, scenario templates, supported commands list

### 2. Placeholder Scan
No TBD, TODO, "implement later", or vague references. All command signatures are verified against source code.

### 3. Type Consistency
- `profile-id` / `<id>` used consistently across all three skills
- `@eN` / `@ref` / `sel` terminology consistent
- `--fast`, `--json` flags documented consistently
- Command formats match actual typer CLI signatures

### 4. Design Compliance
- Three skills matching the approved design
- Workflow-driven with command reference tables
- Common mistakes sections addressing likely failures
- Cross-references between skills
