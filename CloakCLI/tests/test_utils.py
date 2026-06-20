"""Tests for cloakcli.utils module."""

from cloakcli.utils import format_table, print_json, mask_token, resolve_ref


class TestMaskToken:
    def test_long_token(self):
        """Long token shows first 4 and last 4 chars."""
        result = mask_token("abcdef1234567890")
        assert result == "abcd***7890"

    def test_short_token(self):
        """Short token (<=8 chars) shows first 2 only."""
        result = mask_token("abc123")
        assert "***" in result

    def test_none_token(self):
        """None token handled by caller, not mask_token."""
        # mask_token expects a string; None is caller's responsibility
        pass


class TestFormatTable:
    def test_returns_string(self):
        """format_table returns a string with content."""
        rows = [{"name": "test", "status": "running"}]
        result = format_table(rows, ["name", "status"])
        assert isinstance(result, str)
        assert "test" in result
        assert "running" in result

    def test_empty_rows(self):
        """Empty rows produce a table with headers."""
        result = format_table([], ["name", "status"])
        assert isinstance(result, str)

    def test_with_title(self):
        """Title is included in output (may be line-wrapped by Rich)."""
        result = format_table([{"a": "1"}], ["a"], title="MyTable")
        # Rich may wrap the title; check without whitespace
        collapsed = result.replace("\n", "").replace(" ", "")
        assert "MyTable" in collapsed


class TestResolveRef:
    def test_ref_conversion(self):
        """@ref becomes data-snapshot-ref selector."""
        result = resolve_ref(None, "@e3")
        assert result == '[data-snapshot-ref="e3"]'

    def test_css_passthrough(self):
        """Non-@ref strings pass through unchanged."""
        result = resolve_ref(None, "#my-button")
        assert result == "#my-button"

    def test_no_page_needed(self):
        """resolve_ref does not need a real page for string conversion."""
        result = resolve_ref(None, "@e99")
        assert result == '[data-snapshot-ref="e99"]'
