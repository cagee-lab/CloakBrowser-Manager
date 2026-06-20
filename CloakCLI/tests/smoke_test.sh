#!/bin/bash
# cloak-cli 冒烟测试脚本
# 用法: CLOAKBROWSER_HOST=http://192.168.3.12:8080 bash tests/smoke_test.sh
# 需要: 运行中的 CloakBrowser Manager (无 token 认证)

set -euo pipefail

HOST="${CLOAKBROWSER_HOST:-http://localhost:8080}"
CLI="cloak-cli --host $HOST"
PASS=0
FAIL=0
SKIP=0

green() { echo -e "\033[32m$1\033[0m"; }
red()   { echo -e "\033[31m$1\033[0m"; }
dim()   { echo -e "\033[2m$1\033[0m"; }

check() {
    local label="$1"; shift
    local cmd="$@"
    if eval "$cmd" > /dev/null 2>&1; then
        green "  ✅ $label"
        PASS=$((PASS+1))
    else
        red "  ❌ $label"
        FAIL=$((FAIL+1))
    fi
}

check_output() {
    local label="$1"; shift
    local expected="$1"; shift
    local cmd="$@"
    local result
    if result=$(eval "$cmd" 2>/dev/null); then
        if echo "$result" | grep -q "$expected"; then
            green "  ✅ $label"
            PASS=$((PASS+1))
        else
            red "  ❌ $label (expected '$expected', got '${result:0:80}')"
            FAIL=$((FAIL+1))
        fi
    else
        red "  ❌ $label (command failed)"
        FAIL=$((FAIL+1))
    fi
}

# --- Setup ---
echo ""
echo "cloak-cli Smoke Test"
echo "Target: $HOST"
echo ""

# Verify Manager is up
echo "1. System Status"
check_output "status" "running_count" "$CLI status --json"

# Create test profile
echo ""
echo "2. Profile CRUD"
PROFILE_NAME="smoke-test-$(date +%s)"
PROFILE_ID=$($CLI profile create --name "$PROFILE_NAME" --headless --json 2>/dev/null | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])" 2>/dev/null || echo "")
if [ -n "$PROFILE_ID" ]; then
    green "  ✅ profile create ($PROFILE_ID)"
    PASS=$((PASS+1))
else
    red "  ❌ profile create failed"
    FAIL=$((FAIL+1))
    exit 1
fi

check_output "profile list" "$PROFILE_NAME" "$CLI profile list"
check_output "profile get" "$PROFILE_NAME" "$CLI profile get $PROFILE_ID --json"

# Browser Lifecycle
echo ""
echo "3. Browser Lifecycle"
check_output "launch" "running" "$CLI launch $PROFILE_ID"
sleep 3  # wait for browser to initialize

check_output "status (per-profile)" "running" "$CLI status $PROFILE_ID --json"
check_output "status (system)" "1" "$CLI status --json | python3 -c \"import sys,json; print(json.load(sys.stdin)['running_count'])\""

# Navigation
echo ""
echo "4. Navigation"
check_output "open" "Navigated" "$CLI run $PROFILE_ID open https://example.com"
check_output "get title" "Example Domain" "$CLI run $PROFILE_ID get title"
check_output "get url" "example.com" "$CLI run $PROFILE_ID get url"
check_output "reload" "reloaded" "$CLI run $PROFILE_ID reload"
check_output "back (navigate to httpbin)" "Navigated" "$CLI run $PROFILE_ID open https://httpbin.org/ip"
check_output "back" "Navigated back" "$CLI run $PROFILE_ID back"
check_output "forward" "Navigated forward" "$CLI run $PROFILE_ID forward"

# Info Gathering
echo ""
echo "5. Information"
$CLI run $PROFILE_ID open "https://example.com" > /dev/null 2>&1
check_output "get text h1" "Example Domain" "$CLI run $PROFILE_ID get text h1"
check_output "get attr lang" "en" "$CLI run $PROFILE_ID get attr html lang"
check_output "get count" "1" "$CLI run $PROFILE_ID get count h1"
check_output "get html" "<h1>" "$CLI run $PROFILE_ID get html body"

# Interactions (--fast)
echo ""
echo "6. Interactions (--fast)"
$CLI run $PROFILE_ID open "https://httpbin.org/forms/post" > /dev/null 2>&1
check_output "focus" "Focused" "$CLI run $PROFILE_ID focus \"input[name='custname']\" --fast"
check_output "type" "Typed" "$CLI run $PROFILE_ID type \"input[name='custname']\" TestUser --fast"
check_output "fill" "Filled" "$CLI run $PROFILE_ID fill \"input[name='custtel']\" 555-1234 --fast"
check_output "press Tab" "Pressed" "$CLI run $PROFILE_ID press Tab --fast"
check_output "check" "Checked" "$CLI run $PROFILE_ID check \"input[type='checkbox']\" --fast"
check_output "uncheck" "Unchecked" "$CLI run $PROFILE_ID uncheck \"input[type='checkbox']\" --fast"
check_output "dblclick" "Double-clicked" "$CLI run $PROFILE_ID dblclick h1 --fast"

# Capture
echo ""
echo "7. Capture"
$CLI run $PROFILE_ID open "https://example.com" > /dev/null 2>&1
check_output "screenshot" "Screenshot saved" "$CLI run $PROFILE_ID screenshot /tmp/smoke-ss.png --fast"
[ -f /tmp/smoke-ss.png ] && check_output "screenshot file exists" "" "ls /tmp/smoke-ss.png"
check_output "pdf" "PDF saved" "$CLI run $PROFILE_ID pdf /tmp/smoke-pdf.pdf --fast"
[ -f /tmp/smoke-pdf.pdf ] && check_output "pdf file exists" "" "ls /tmp/smoke-pdf.pdf"
check_output "eval" "Example Domain" "$CLI run $PROFILE_ID eval document.title --fast"

# Tab
echo ""
echo "8. Tabs"
$CLI run $PROFILE_ID open "https://example.com" > /dev/null 2>&1
check_output "tab list" "t1" "$CLI run $PROFILE_ID tab"
check_output "tab new" "New tab opened" "$CLI run $PROFILE_ID tab-new https://httpbin.org/ip --fast"
check_output "tab switch" "Switched to tab: t1" "$CLI run $PROFILE_ID tab-switch t1 --fast"
check_output "tab close" "Closed tab" "$CLI run $PROFILE_ID tab-close t2 --fast"
check_output "window new" "New window created" "$CLI run $PROFILE_ID window-new --fast"

# Utility
echo ""
echo "9. Utility"
$CLI run $PROFILE_ID open "https://example.com" > /dev/null 2>&1
check_output "wait 500ms" "Wait completed" "$CLI run $PROFILE_ID wait 500 --fast"
check_output "scroll down" "Scrolled down" "$CLI run $PROFILE_ID scroll down 200 --fast"
check_output "scroll up" "Scrolled up" "$CLI run $PROFILE_ID scroll up 100 --fast"
check_output "scrollintoview" "Scrolled into view" "$CLI run $PROFILE_ID scrollintoview p --fast"

# Clipboard
echo ""
echo "10. Clipboard"
check_output "clipboard write" "Clipboard" "$CLI clipboard write $PROFILE_ID \"smoke-test-text\""
check_output "clipboard read" "ok" "$CLI clipboard read $PROFILE_ID"

# --- Cleanup ---
echo ""
echo "11. Cleanup"
check_output "stop" "Stopped" "$CLI stop $PROFILE_ID"
check_output "delete" "Deleted" "$CLI profile delete $PROFILE_ID --force"

# Clean up temp files
rm -f /tmp/smoke-ss.png /tmp/smoke-pdf.pdf

# --- Summary ---
echo ""
echo "========================================"
echo -n "Results: "
green "$PASS passed  "
[ $FAIL -gt 0 ] && red "$FAIL failed  "
dim "$SKIP skipped"
echo "========================================"

[ $FAIL -eq 0 ] && exit 0 || exit 1
