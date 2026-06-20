#!/bin/bash
# Typical cloak-cli workflow: create → launch → automate → stop → cleanup

set -e

PROFILE_NAME="cli-demo-$(date +%s)"

echo "=== Creating profile ==="
PROFILE_ID=$(cloak-cli profile create --name "$PROFILE_NAME" --humanize --json | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")
echo "Created: $PROFILE_ID"

echo "=== Launching browser ==="
cloak-cli launch "$PROFILE_ID"

echo "=== Navigating ==="
cloak-cli run "$PROFILE_ID" open "https://example.com"

echo "=== Taking snapshot ==="
cloak-cli run "$PROFILE_ID" snapshot -i

echo "=== Screenshot ==="
cloak-cli run "$PROFILE_ID" screenshot "demo-screenshot.png"

echo "=== Stopping browser ==="
cloak-cli stop "$PROFILE_ID"

echo "=== Cleaning up ==="
cloak-cli profile delete "$PROFILE_ID" --force

echo "Done!"
