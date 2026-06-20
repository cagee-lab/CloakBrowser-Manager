"""Test CLI commands with Typer CliRunner."""

from typer.testing import CliRunner
from cloakcli.cmd.main import app

runner = CliRunner()


class TestProfileCommands:
    def test_profile_list_help(self):
        result = runner.invoke(app, ["profile", "list", "--help"])
        assert result.exit_code == 0
        assert "List all profiles" in result.stdout

    def test_profile_create_help(self):
        result = runner.invoke(app, ["profile", "create", "--help"])
        assert result.exit_code == 0
        assert "--name" in result.stdout

    def test_config_show(self, monkeypatch):
        monkeypatch.setenv("CLOAKBROWSER_HOST", "http://example.com:8080")
        result = runner.invoke(app, ["config", "show"])
        assert result.exit_code == 0
        assert "example.com" in result.stdout

    def test_config_path(self):
        result = runner.invoke(app, ["config", "path"])
        assert result.exit_code == 0
        assert "cloakcli" in result.stdout


class TestRunCommands:
    def test_open_missing_args(self):
        result = runner.invoke(app, ["run", "test-id", "open"])
        # requires profile_id AND url -> needs url arg too
        assert result.exit_code != 0

    def test_click_help(self):
        result = runner.invoke(app, ["run", "test-id", "click", "--help"])
        assert result.exit_code == 0
        assert "Click an element" in result.stdout

    def test_snapshot_help(self):
        result = runner.invoke(app, ["run", "test-id", "snapshot", "--help"])
        assert result.exit_code == 0
        assert "accessibility tree" in result.stdout.lower()

    def test_batch_help(self):
        result = runner.invoke(app, ["run", "test-id", "batch", "--help"])
        assert result.exit_code == 0
        assert "batch" in result.stdout.lower()
