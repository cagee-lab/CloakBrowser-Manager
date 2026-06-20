"""Multi-source configuration: YAML file → env vars → CLI args."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

import yaml


@dataclass
class Config:
    """Resolved configuration for connecting to CloakBrowser Manager."""
    host: str = "http://localhost:8080"
    token: str | None = None


class ConfigLoader:
    """Load config from multiple sources with priority: CLI > env > file > defaults."""

    def __init__(self, config_path: str | None = None):
        self._config_path = config_path or self._default_config_path()

    @staticmethod
    def _default_config_path() -> str:
        return str(Path.home() / ".cloakcli" / "config.yaml")

    def load(
        self,
        profile: str = "default",
        cli_host: str | None = None,
        cli_token: str | None = None,
    ) -> Config:
        # 1. Start with defaults
        host = "http://localhost:8080"
        token = None

        # 2. Overlay config file (lowest priority)
        file_cfg = self._read_config_file()
        if profile in file_cfg:
            if "host" in file_cfg[profile]:
                host = file_cfg[profile]["host"]
            if "token" in file_cfg[profile]:
                token = file_cfg[profile]["token"]
        elif profile != "default":
            raise ValueError(
                f"Profile '{profile}' not found in {self._config_path}"
            )

        # 3. Overlay environment variables
        env_host = os.environ.get("CLOAKBROWSER_HOST")
        env_token = os.environ.get("CLOAKBROWSER_TOKEN")
        if env_host:
            host = env_host
        if env_token:
            token = env_token

        # 4. Overlay CLI args (highest priority)
        if cli_host:
            host = cli_host
        if cli_token is not None:
            token = cli_token

        return Config(host=host, token=token)

    def _read_config_file(self) -> dict:
        try:
            with open(self._config_path) as f:
                return yaml.safe_load(f) or {}
        except (FileNotFoundError, yaml.YAMLError):
            return {}
