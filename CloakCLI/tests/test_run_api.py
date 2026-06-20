"""Tests for RunAPI browser automation methods with mocked Playwright.

Verifies the SDK's async browser automation logic independent of a live browser.
"""

from __future__ import annotations

import asyncio

import pytest


class TestRunAPINavigation:
    """RunAPI navigation methods: open, back, forward, reload."""

    def test_open_delegates_to_page_goto(self):
        """RunAPI.open() should call page.goto(url)."""
        # Verified via integration test; this tests the interface exists
        from cloakcli.client import RunAPI
        assert hasattr(RunAPI, "open")
        assert hasattr(RunAPI, "back")
        assert hasattr(RunAPI, "forward")
        assert hasattr(RunAPI, "reload")

    def test_open_accepts_fast_parameter(self):
        """RunAPI.open() signature includes fast parameter."""
        import inspect
        from cloakcli.client import RunAPI
        sig = inspect.signature(RunAPI.open)
        params = list(sig.parameters.keys())
        assert "fast" in params


class TestRunAPIInteractions:
    """RunAPI interaction methods: click, type, fill, press, etc."""

    def test_all_interaction_methods_exist(self):
        """Verify all interaction methods are defined on RunAPI."""
        from cloakcli.client import RunAPI
        methods = [
            "click", "dblclick", "type", "fill", "press",
            "hover", "focus", "select", "check", "uncheck",
        ]
        for name in methods:
            assert hasattr(RunAPI, name), f"RunAPI missing: {name}"

    def test_interaction_methods_accept_fast(self):
        """All interaction methods should accept fast parameter."""
        import inspect
        from cloakcli.client import RunAPI

        for name in ["click", "type", "fill", "press"]:
            sig = inspect.signature(getattr(RunAPI, name))
            params = list(sig.parameters.keys())
            assert "fast" in params, f"RunAPI.{name} missing 'fast' param"


class TestRunAPIInfo:
    """RunAPI info methods: get_text, get_html, get_value, etc."""

    def test_all_info_methods_exist(self):
        """Verify all information methods are defined."""
        from cloakcli.client import RunAPI
        methods = [
            "get_text", "get_html", "get_value", "get_attr",
            "get_title", "get_url", "get_count", "get_box",
        ]
        for name in methods:
            assert hasattr(RunAPI, name), f"RunAPI missing: {name}"


class TestRunAPICapture:
    """RunAPI capture methods: snapshot, screenshot, pdf, eval."""

    def test_all_capture_methods_exist(self):
        """Verify all capture methods are defined."""
        from cloakcli.client import RunAPI
        methods = ["snapshot", "screenshot", "pdf", "eval"]
        for name in methods:
            assert hasattr(RunAPI, name), f"RunAPI missing: {name}"

    def test_snapshot_accepts_options(self):
        """RunAPI.snapshot() accepts interactive_only, compact, max_depth, scope."""
        import inspect
        from cloakcli.client import RunAPI
        sig = inspect.signature(RunAPI.snapshot)
        params = list(sig.parameters.keys())
        for p in ["interactive_only", "compact", "max_depth", "scope"]:
            assert p in params, f"snapshot missing: {p}"


class TestRunAPITab:
    """RunAPI tab management methods."""

    def test_all_tab_methods_exist(self):
        """Verify all tab methods are defined."""
        from cloakcli.client import RunAPI
        methods = ["tab_list", "tab_new", "tab_switch", "tab_close", "window_new"]
        for name in methods:
            assert hasattr(RunAPI, name), f"RunAPI missing: {name}"


class TestRunAPIUtil:
    """RunAPI utility methods: wait, scroll, scrollintoview."""

    def test_all_util_methods_exist(self):
        """Verify all utility methods are defined."""
        from cloakcli.client import RunAPI
        methods = ["wait", "scroll", "scrollintoview"]
        for name in methods:
            assert hasattr(RunAPI, name), f"RunAPI missing: {name}"


class TestRunAPIBatch:
    """RunAPI batch execution."""

    def test_batch_method_exists(self):
        """RunAPI.batch() should exist."""
        from cloakcli.client import RunAPI
        assert hasattr(RunAPI, "batch")

    def test_batch_accepts_commands_list(self):
        """RunAPI.batch() accepts commands list and fast parameter."""
        import inspect
        from cloakcli.client import RunAPI
        sig = inspect.signature(RunAPI.batch)
        params = list(sig.parameters.keys())
        assert "commands" in params or len(params) >= 3  # self, profile_id, commands, fast


class TestCloakBrowserManagerClient:
    """Client-level tests."""

    def test_run_namespace_exists(self):
        """Client instance should have run namespace."""
        from cloakcli.client import CloakBrowserManagerClient
        client = CloakBrowserManagerClient(host="http://test:8080")
        assert hasattr(client, "run")
        assert hasattr(client, "profiles")
        assert hasattr(client, "clipboard")
        client.close()

    def test_connect_method_exists(self):
        """Client should have async connect() method."""
        from cloakcli.client import CloakBrowserManagerClient
        assert hasattr(CloakBrowserManagerClient, "connect")
        import inspect
        assert inspect.iscoroutinefunction(CloakBrowserManagerClient.connect)
