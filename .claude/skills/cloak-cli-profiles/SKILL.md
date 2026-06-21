---
name: cloak-cli-profiles
description: Use when managing CloakBrowser Manager profiles via CLI — creating, listing, updating, deleting profiles, launching and stopping browsers, or checking status. Also use when configuring cloak-cli connection settings (host, token, profile switching).
---

# CloakCLI — Profiles & Browser Lifecycle

## Overview

Manage CloakBrowser Manager profiles and browser lifecycle via `cloak-cli`. Profiles are referenced by **UUID** (not name). `launch`, `stop`, `status` are top-level commands, not under `profile`.

> **Next:** Once a profile is running, use [[cloak-cli-automation]] for page interactions or [[cloak-cli-batch]] for multi-step flows.

## Quick Connection

Three ways, highest priority first:

```bash
# 1. CLI flags (overrides everything)
cloak-cli --host http://192.168.1.100:9090 --token abc123 profile list

# 2. Environment variables
export CLOAKBROWSER_HOST=http://localhost:8080
export CLOAKBROWSER_TOKEN=your-token

# 3. Config file: ~/.cloakcli/config.yaml
default:
  host: http://localhost:8080
  token: your-token
```

**Priority:** CLI flags > env vars > config file > defaults (`http://localhost:8080`, no token).

Switch config profiles: `cloak-cli --profile staging profile list` (uses `staging:` section in config.yaml).

Check current config: `cloak-cli config show`. Config file path: `cloak-cli config path`.

## Workflow: Create and Launch a Profile

```bash
# 1. Create with humanize enabled
cloak-cli profile create --name "demo" --humanize
# → Created profile: abc12345... (demo)

# 2. Launch the browser (top-level command, not profile launch)
cloak-cli launch abc12345
# → Shows: Status, VNC Port, Display, CDP URL

# 3. Check per-profile status
cloak-cli status abc12345
# → Status: running, VNC Port, CDP URL

# 4. Stop when done
cloak-cli stop abc12345
```

## Workflow: Manage Existing Profiles

```bash
# List all profiles (table: id, name, status, proxy, tags)
cloak-cli profile list
cloak-cli profile list --json

# Get full details of one profile
cloak-cli profile get abc12345
cloak-cli profile get abc12345 --json

# Partial update (only specified fields change)
cloak-cli profile update abc12345 --name "renamed" --no-humanize

# Delete (confirms unless --force)
cloak-cli profile delete abc12345
cloak-cli profile delete abc12345 --force
```

## Workflow: System Status

```bash
# System overview (no argument)
cloak-cli status
# → Running Profiles: 2, Total Profiles: 5, Binary Version: ...

cloak-cli status --json

# Per-profile status (with profile ID)
cloak-cli status abc12345
# → Status: running, VNC Port: ..., CDP URL: ...
```

## Command Reference

### Profile CRUD

| Command | Key Options | Notes |
|---------|------------|-------|
| `profile list` | `--json` | Table format by default |
| `profile get <id>` | `--json` | Full details |
| `profile create --name <n>` | `--humanize`, `--proxy <url>`, `--timezone <tz>`, `--locale <lc>`, `--platform <os>`, `--screen-width/height`, `--human-preset`, `--headless`, `--geoip`, `--auto-launch`, `--seed <n>`, `--user-agent <ua>`, `--tag k:v` | Only `--name` required; `--humanize` is off by default |
| `profile update <id>` | `--name`, `--proxy`, `--humanize/--no-humanize`, `--human-preset`, `--headless/--no-headless` | Partial update — only specified fields change |
| `profile delete <id>` | `--force` / `-f` | Confirms unless `--force` |

### Browser Lifecycle (top-level commands)

| Command | Notes |
|---------|-------|
| `launch <id>` | Shows VNC port, display, CDP URL |
| `stop <id>` | Graceful shutdown |
| `status` | System overview: running count, total, binary version |
| `status <id>` | Per-profile: status, VNC port, CDP URL |

### Config & Clipboard

| Command | Notes |
|---------|-------|
| `config show` | Current host, masked token |
| `config path` | Path to `~/.cloakcli/config.yaml` |
| `clipboard read <id>` | Read clipboard; `--json` for `{"text": "..."}` |
| `clipboard write <id> <text>` | Write to clipboard |

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| `profile create` without `--name` | `--name` is required |
| Using profile name as ID | Profiles are UUIDs; use `profile list` to find IDs |
| `cloak-cli profile launch <id>` | `launch` is top-level: `cloak-cli launch <id>` |
| `cloak-cli profile status <id>` | `status` is top-level: `cloak-cli status <id>` |
| `status` vs `status <id>` confused | No arg = system overview; with id = profile status |
| Forgetting `--humanize` on create | Humanize is off by default; add `--humanize` |
| Launching already-running profile | Check `status <id>` first |
| 401 Unauthorized | Check token with `config show`; set via `--token` or env var |
| Config file YAML invalid | Must use profile sections: `default:`, `staging:`, etc. |
| Env var names unknown | `CLOAKBROWSER_HOST` and `CLOAKBROWSER_TOKEN` |
| Config file location unknown | `~/.cloakcli/config.yaml` |
