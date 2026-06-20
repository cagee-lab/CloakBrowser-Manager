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

    def test_run_click_help(self):
        result = runner.invoke(app, ["run", "click", "--help"])
        assert result.exit_code == 0
        assert "Click an element" in result.stdout

    def test_run_snapshot_help(self):
        result = runner.invoke(app, ["run", "snapshot", "--help"])
        assert result.exit_code == 0
        assert "accessibility tree" in result.stdout.lower()

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
        result = runner.invoke(app, ["run", "open"])
        assert result.exit_code != 0  # requires profile_id and url

    def test_click_with_fast(self):
        result = runner.invoke(app, ["run", "click", "--fast", "--help"])
        assert result.exit_code == 0

    def test_batch_help(self):
        result = runner.invoke(app, ["run", "batch", "--help"])
        assert result.exit_code == 0
        assert "batch" in result.stdout.lower()
