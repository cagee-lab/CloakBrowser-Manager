# CloakCLI

CLI client and Python SDK for [CloakBrowser Manager](https://github.com/CloakHQ/CloakBrowser-Manager).

## Install

```bash
pip install cloak-cli
playwright install chromium
```

## Configure

```bash
mkdir -p ~/.cloakcli
cat > ~/.cloakcli/config.yaml << EOF
default:
  host: http://localhost:8080
  token: your-auth-token
EOF
```

Or use environment variables:

```bash
export CLOAKBROWSER_HOST=http://localhost:8080
export CLOAKBROWSER_TOKEN=your-auth-token
```

## CLI Quick Start

```bash
# Manage profiles
cloak-cli profile list
cloak-cli profile create --name "my-profile" --humanize
cloak-cli profile get <id>

# Browser lifecycle
cloak-cli launch <id>
cloak-cli status <id>
cloak-cli stop <id>

# Automation (auto-humanized)
cloak-cli run <id> open "https://example.com"
cloak-cli run <id> snapshot -i
cloak-cli run <id> click "@e3"
cloak-cli run <id> type "#search" "cloakbrowser"
cloak-cli run <id> screenshot result.png

# Fast mode (skip humanize, for testing)
cloak-cli run <id> --fast click "#btn"

# Batch execution
cloak-cli run <id> batch commands.json

# Clipboard
cloak-cli clipboard read <id>
cloak-cli clipboard write <id> "hello"
```

## Python SDK

```python
from cloakcli import CloakBrowserManagerClient

client = CloakBrowserManagerClient(host="http://localhost:8080", token="...")

# Profile management
profiles = client.profiles.list()
client.profiles.create(name="test", humanize=True)

# Browser lifecycle
result = client.launch(profiles[0].id)

# CDP + humanize (returns Playwright Browser)
browser = await client.connect(profiles[0].id)
page = browser.contexts[0].pages[0]
await page.goto("https://example.com")
await page.click("#login")  # humanized click!
await browser.close()

# Convenience run methods
await client.run.click(profiles[0].id, "#btn")
await client.run.snapshot(profiles[0].id, interactive_only=True)
```

## Commands

See `cloak-cli --help` and `cloak-cli run --help` for full command reference.
