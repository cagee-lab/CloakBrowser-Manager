import os
import tempfile
from pathlib import Path
import pytest
import yaml
from cloakcli.config import Config, ConfigLoader


class TestConfig:
    def test_direct_creation(self):
        cfg = Config(host="http://x:8080", token="t")
        assert cfg.host == "http://x:8080"
        assert cfg.token == "t"

    def test_defaults(self):
        cfg = Config()
        assert cfg.host == "http://localhost:8080"
        assert cfg.token is None


class TestConfigLoader:
    def test_from_cli_args(self):
        loader = ConfigLoader()
        cfg = loader.load(cli_host="http://cli:8080", cli_token="cli-token")
        assert cfg.host == "http://cli:8080"
        assert cfg.token == "cli-token"

    def test_from_env_vars(self, monkeypatch):
        monkeypatch.setenv("CLOAKBROWSER_HOST", "http://env:8080")
        monkeypatch.setenv("CLOAKBROWSER_TOKEN", "env-token")
        loader = ConfigLoader()
        cfg = loader.load()
        assert cfg.host == "http://env:8080"
        assert cfg.token == "env-token"

    def test_cli_overrides_env(self, monkeypatch):
        monkeypatch.setenv("CLOAKBROWSER_HOST", "http://env:8080")
        monkeypatch.setenv("CLOAKBROWSER_TOKEN", "env-token")
        loader = ConfigLoader()
        cfg = loader.load(cli_host="http://cli:8080")
        assert cfg.host == "http://cli:8080"  # CLI wins
        assert cfg.token == "env-token"       # env fallback

    def test_env_overrides_config_file(self, monkeypatch):
        # Create temp config file
        config_data = {"default": {"host": "http://file:8080", "token": "file-token"}}
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(config_data, f)
            config_path = f.name
        try:
            monkeypatch.setenv("CLOAKBROWSER_HOST", "http://env:8080")
            loader = ConfigLoader(config_path=config_path)
            cfg = loader.load()
            assert cfg.host == "http://env:8080"  # env wins
            assert cfg.token == "file-token"       # file fallback
        finally:
            os.unlink(config_path)

    def test_config_file_profile_switch(self):
        config_data = {
            "default": {"host": "http://default:8080", "token": "default-token"},
            "staging": {"host": "http://staging:8080", "token": "staging-token"},
        }
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(config_data, f)
            config_path = f.name
        try:
            loader = ConfigLoader(config_path=config_path)
            cfg = loader.load(profile="staging")
            assert cfg.host == "http://staging:8080"
            assert cfg.token == "staging-token"
        finally:
            os.unlink(config_path)

    def test_missing_profile_raises(self):
        config_data = {"default": {"host": "http://x:8080"}}
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(config_data, f)
            config_path = f.name
        try:
            loader = ConfigLoader(config_path=config_path)
            with pytest.raises(ValueError, match="Profile 'staging' not found"):
                loader.load(profile="staging")
        finally:
            os.unlink(config_path)

    def test_no_config_file_uses_defaults(self, monkeypatch):
        loader = ConfigLoader(config_path="/nonexistent/path.yaml")
        cfg = loader.load()
        assert cfg.host == "http://localhost:8080"
        assert cfg.token is None
