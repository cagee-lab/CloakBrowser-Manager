"""Integration tests for cloak-cli against a live CloakBrowser Manager.

Usage:
    CLOAKBROWSER_HOST=http://192.168.3.12:8080 pytest tests/test_integration.py -v

    Without CLOAKBROWSER_HOST, all tests are skipped.
"""

from __future__ import annotations

import asyncio
import json
import os
import time

import pytest

from cloakcli import CloakBrowserManagerClient
from cloakcli.cmd.main import app as cli_app
from typer.testing import CliRunner

# --- Configuration ---

MANAGER_HOST = os.environ.get("CLOAKBROWSER_HOST", "")
MANAGER_TOKEN = os.environ.get("CLOAKBROWSER_TOKEN", None)

requires_manager = pytest.mark.skipif(
    not MANAGER_HOST,
    reason="Set CLOAKBROWSER_HOST env var to run integration tests",
)

runner = CliRunner()


def invoke(*args):
    """Run cloak-cli with --host."""
    cmd = ["--host", MANAGER_HOST]
    if MANAGER_TOKEN:
        cmd.extend(["--token", MANAGER_TOKEN])
    cmd.extend(args)
    return runner.invoke(cli_app, cmd)


def run_async(coro):
    """Helper to run RunAPI async methods synchronously in tests."""
    return asyncio.run(coro)


# --- SDK Tests ---

@requires_manager
class TestSDK_SystemStatus:
    def test_system_status(self):
        """GET /api/status returns running_count, binary_version, profiles_total."""
        client = CloakBrowserManagerClient(host=MANAGER_HOST, token=MANAGER_TOKEN)
        status = client.status()
        client.close()
        assert status.running_count >= 0
        assert status.binary_version
        assert status.profiles_total >= 0


@requires_manager
class TestSDK_ProfileCRUD:
    def test_create_and_delete(self):
        """Create a profile, verify it exists, then delete it."""
        client = CloakBrowserManagerClient(host=MANAGER_HOST, token=MANAGER_TOKEN)

        p = client.profiles.create(name=f"test-crud-{int(time.time())}", headless=True)
        assert p.id
        assert p.name
        assert p.status == "stopped"

        profiles = client.profiles.list()
        ids = [x.id for x in profiles]
        assert p.id in ids

        fetched = client.profiles.get(p.id)
        assert fetched.id == p.id

        updated = client.profiles.update(p.id, name=f"test-crud-updated-{int(time.time())}")
        assert updated.name != p.name

        result = client.profiles.delete(p.id)
        assert result is True

        client.close()


@requires_manager
class TestSDK_BrowserLifecycle:
    @pytest.fixture(autouse=True)
    def _profile(self):
        if not MANAGER_HOST:
            pytest.skip("No Manager")
        client = CloakBrowserManagerClient(host=MANAGER_HOST, token=MANAGER_TOKEN)
        p = client.profiles.create(name=f"test-lifecycle-{int(time.time())}", headless=True)
        self.profile_id = p.id
        client.close()
        yield
        client = CloakBrowserManagerClient(host=MANAGER_HOST, token=MANAGER_TOKEN)
        try:
            client.stop(self.profile_id)
        except Exception:
            pass
        try:
            client.profiles.delete(self.profile_id)
        except Exception:
            pass
        client.close()

    def test_launch_stop_status(self):
        """Launch a browser, check status, then stop it."""
        client = CloakBrowserManagerClient(host=MANAGER_HOST, token=MANAGER_TOKEN)

        result = client.launch(self.profile_id)
        assert result.status == "running"
        assert result.cdp_url is not None
        assert result.vnc_ws_port > 0

        ps = client.status(self.profile_id)
        assert ps.status == "running"

        ss = client.status()
        assert ss.running_count >= 1

        client.stop(self.profile_id)
        ps = client.status(self.profile_id)
        assert ps.status == "stopped"

        client.close()


@requires_manager
class TestSDK_Clipboard:
    @pytest.fixture(autouse=True)
    def _profile(self):
        if not MANAGER_HOST:
            pytest.skip("No Manager")
        client = CloakBrowserManagerClient(host=MANAGER_HOST, token=MANAGER_TOKEN)
        p = client.profiles.create(name=f"test-clipboard-{int(time.time())}", headless=True)
        self.profile_id = p.id
        client.launch(self.profile_id)
        client.close()
        yield
        client = CloakBrowserManagerClient(host=MANAGER_HOST, token=MANAGER_TOKEN)
        try:
            client.stop(self.profile_id)
        except Exception:
            pass
        try:
            client.profiles.delete(self.profile_id)
        except Exception:
            pass
        client.close()

    def test_read_write(self):
        """Write text to clipboard and read it back."""
        client = CloakBrowserManagerClient(host=MANAGER_HOST, token=MANAGER_TOKEN)
        test_text = f"clipboard-test-{int(time.time())}"
        client.clipboard.write(self.profile_id, test_text)
        result = client.clipboard.read(self.profile_id)
        assert isinstance(result, str)
        client.close()


# --- Browser Automation Tests (requires running browser) ---

@requires_manager
class TestBrowserAutomation:
    """Browser automation tests using a live launched profile."""

    @classmethod
    def setup_class(cls):
        if not MANAGER_HOST:
            return
        client = CloakBrowserManagerClient(host=MANAGER_HOST, token=MANAGER_TOKEN)
        p = client.profiles.create(name=f"test-auto-{int(time.time())}", headless=True)
        cls.profile_id = p.id
        client.launch(cls.profile_id)
        client.close()
        time.sleep(2)

    @classmethod
    def teardown_class(cls):
        if not MANAGER_HOST or not cls.profile_id:
            return
        client = CloakBrowserManagerClient(host=MANAGER_HOST, token=MANAGER_TOKEN)
        try:
            client.stop(cls.profile_id)
        except Exception:
            pass
        try:
            client.profiles.delete(cls.profile_id)
        except Exception:
            pass
        client.close()

    # --- Navigation ---

    def test_open_and_get_url(self):
        client = CloakBrowserManagerClient(host=MANAGER_HOST, token=MANAGER_TOKEN)
        try:
            run_async(client.run.open(self.profile_id, "https://example.com", fast=True))
            url = run_async(client.run.get_url(self.profile_id))
            assert "example.com" in url
        finally:
            client.close()

    def test_reload(self):
        client = CloakBrowserManagerClient(host=MANAGER_HOST, token=MANAGER_TOKEN)
        try:
            run_async(client.run.open(self.profile_id, "https://example.com", fast=True))
            run_async(client.run.reload(self.profile_id, fast=True))
        finally:
            client.close()

    def test_back_forward(self):
        client = CloakBrowserManagerClient(host=MANAGER_HOST, token=MANAGER_TOKEN)
        try:
            run_async(client.run.open(self.profile_id, "https://example.com", fast=True))
            run_async(client.run.open(self.profile_id, "https://httpbin.org/ip", fast=True))
            run_async(client.run.back(self.profile_id, fast=True))
            url = run_async(client.run.get_url(self.profile_id))
            assert "example.com" in url
            run_async(client.run.forward(self.profile_id, fast=True))
            url = run_async(client.run.get_url(self.profile_id))
            assert "httpbin.org" in url
        finally:
            client.close()

    # --- Information ---

    def test_get_title(self):
        client = CloakBrowserManagerClient(host=MANAGER_HOST, token=MANAGER_TOKEN)
        try:
            run_async(client.run.open(self.profile_id, "https://example.com", fast=True))
            title = run_async(client.run.get_title(self.profile_id))
            assert title == "Example Domain"
        finally:
            client.close()

    def test_get_text(self):
        client = CloakBrowserManagerClient(host=MANAGER_HOST, token=MANAGER_TOKEN)
        try:
            run_async(client.run.open(self.profile_id, "https://example.com", fast=True))
            text = run_async(client.run.get_text(self.profile_id, "h1"))
            assert "Example" in text
        finally:
            client.close()

    def test_get_attr(self):
        client = CloakBrowserManagerClient(host=MANAGER_HOST, token=MANAGER_TOKEN)
        try:
            run_async(client.run.open(self.profile_id, "https://example.com", fast=True))
            lang = run_async(client.run.get_attr(self.profile_id, "html", "lang"))
            assert lang is not None
        finally:
            client.close()

    def test_get_count(self):
        client = CloakBrowserManagerClient(host=MANAGER_HOST, token=MANAGER_TOKEN)
        try:
            run_async(client.run.open(self.profile_id, "https://example.com", fast=True))
            count = run_async(client.run.get_count(self.profile_id, "p"))
            assert count >= 1
        finally:
            client.close()

    # --- Interactions ---

    def test_click_and_type_on_form(self):
        client = CloakBrowserManagerClient(host=MANAGER_HOST, token=MANAGER_TOKEN)
        try:
            run_async(client.run.open(self.profile_id, "https://httpbin.org/forms/post", fast=True))
            run_async(client.run.focus(self.profile_id, "input[name='custname']", fast=True))
            run_async(client.run.type(self.profile_id, "input[name='custname']", "TestUser", fast=True))
            run_async(client.run.fill(self.profile_id, "input[name='custtel']", "555-0001", fast=True))
            run_async(client.run.press(self.profile_id, "Tab", fast=True))
        finally:
            client.close()

    def test_check_uncheck(self):
        client = CloakBrowserManagerClient(host=MANAGER_HOST, token=MANAGER_TOKEN)
        try:
            # Use example.com first to verify connection, then navigate to form
            run_async(client.run.open(self.profile_id, "https://example.com", fast=True))
            run_async(client.run.open(self.profile_id, "https://httpbin.org/forms/post", fast=True))
            run_async(client.run.check(self.profile_id, "input[type='checkbox']", fast=True))
            run_async(client.run.uncheck(self.profile_id, "input[type='checkbox']", fast=True))
        except Exception as e:
            if "Timeout" in str(e):
                pytest.skip("httpbin.org timed out")
            raise
        finally:
            client.close()

    def test_dblclick(self):
        client = CloakBrowserManagerClient(host=MANAGER_HOST, token=MANAGER_TOKEN)
        try:
            run_async(client.run.open(self.profile_id, "https://example.com", fast=True))
            run_async(client.run.dblclick(self.profile_id, "h1", fast=True))
        finally:
            client.close()

    # --- Capture ---

    def test_screenshot(self):
        client = CloakBrowserManagerClient(host=MANAGER_HOST, token=MANAGER_TOKEN)
        path = f"/tmp/cloak-cli-test-ss-{int(time.time())}.png"
        try:
            run_async(client.run.open(self.profile_id, "https://example.com", fast=True))
            result = run_async(client.run.screenshot(self.profile_id, path, fast=True))
            assert os.path.exists(result)
            assert os.path.getsize(result) > 100
        finally:
            client.close()
            if os.path.exists(path):
                os.remove(path)

    def test_pdf(self):
        client = CloakBrowserManagerClient(host=MANAGER_HOST, token=MANAGER_TOKEN)
        path = f"/tmp/cloak-cli-test-pdf-{int(time.time())}.pdf"
        try:
            run_async(client.run.open(self.profile_id, "https://example.com", fast=True))
            result = run_async(client.run.pdf(self.profile_id, path, fast=True))
            assert os.path.exists(result)
            assert os.path.getsize(result) > 100
        finally:
            client.close()
            if os.path.exists(path):
                os.remove(path)

    def test_eval(self):
        client = CloakBrowserManagerClient(host=MANAGER_HOST, token=MANAGER_TOKEN)
        try:
            run_async(client.run.open(self.profile_id, "https://example.com", fast=True))
            result = run_async(client.run.eval(self.profile_id, "document.title", fast=True))
            assert result == "Example Domain"
        finally:
            client.close()

    # --- Tab ---

    def test_tab_operations(self):
        client = CloakBrowserManagerClient(host=MANAGER_HOST, token=MANAGER_TOKEN)
        try:
            run_async(client.run.open(self.profile_id, "https://example.com", fast=True))
            run_async(client.run.tab_new(self.profile_id, "https://httpbin.org/ip", fast=True))

            tabs = run_async(client.run.tab_list(self.profile_id))
            assert len(tabs) >= 2, f"Expected >=2 tabs, got {len(tabs)}"

            run_async(client.run.tab_switch(self.profile_id, "t1", fast=True))
            run_async(client.run.wait(self.profile_id, "500", fast=True))
            url = run_async(client.run.get_url(self.profile_id))
            assert "example.com" in url, f"Expected example.com, got {url}"

            run_async(client.run.tab_close(self.profile_id, "t2", fast=True))
            tabs = run_async(client.run.tab_list(self.profile_id))
            assert len(tabs) >= 1
        finally:
            client.close()

    # --- Utility ---

    def test_scroll(self):
        client = CloakBrowserManagerClient(host=MANAGER_HOST, token=MANAGER_TOKEN)
        try:
            run_async(client.run.open(self.profile_id, "https://example.com", fast=True))
            run_async(client.run.scroll(self.profile_id, "down", 200, fast=True))
            run_async(client.run.scroll(self.profile_id, "up", 100, fast=True))
            run_async(client.run.scrollintoview(self.profile_id, "p", fast=True))
        finally:
            client.close()

    def test_wait_timeout(self):
        client = CloakBrowserManagerClient(host=MANAGER_HOST, token=MANAGER_TOKEN)
        try:
            run_async(client.run.open(self.profile_id, "https://example.com", fast=True))
            start = time.time()
            run_async(client.run.wait(self.profile_id, "500", fast=True))
            elapsed = time.time() - start
            assert elapsed >= 0.4, f"Wait too short: {elapsed:.2f}s"
        finally:
            client.close()


# --- CLI Tests ---

@requires_manager
class TestCLI_ProfileCommands:
    def test_profile_list(self):
        """cli profile list should succeed."""
        result = invoke("profile", "list")
        assert result.exit_code == 0

    def test_profile_list_json(self):
        """cli profile list --json should output valid JSON."""
        result = invoke("profile", "list", "--json")
        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert isinstance(data, list)

    def test_profile_create_and_get(self):
        """Create profile via CLI, get it, verify it."""
        name = f"cli-test-{int(time.time())}"
        result = invoke("profile", "create", "--name", name, "--headless", "--json")
        assert result.exit_code == 0
        data = json.loads(result.stdout)
        pid = data["id"]

        result = invoke("profile", "get", pid, "--json")
        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert data["name"] == name

        result = invoke("profile", "delete", pid, "--force")
        assert result.exit_code == 0


@requires_manager
class TestCLI_StatusCommands:
    def test_system_status(self):
        """cli status should succeed."""
        result = invoke("status")
        assert result.exit_code == 0
        assert "Running" in result.stdout or "Binary" in result.stdout

    def test_system_status_json(self):
        """cli status --json outputs valid JSON."""
        result = invoke("status", "--json")
        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert "running_count" in data
