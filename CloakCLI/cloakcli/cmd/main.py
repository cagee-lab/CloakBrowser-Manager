"""Typer CLI entry point for cloak-cli."""

from __future__ import annotations

from typing import Optional

import typer

from ..config import ConfigLoader

app = typer.Typer(
    name="cloak-cli",
    help="CLI client for CloakBrowser Manager",
    no_args_is_help=True,
)


@app.callback()
def main(
    ctx: typer.Context,
    host: str = typer.Option(
        None, "--host", help="Manager host URL", envvar="CLOAKBROWSER_HOST"
    ),
    token: str = typer.Option(
        None, "--token", help="Auth token", envvar="CLOAKBROWSER_TOKEN"
    ),
    profile: str = typer.Option(
        "default", "--profile", help="Config profile name (not browser profile)"
    ),
):
    """CloakBrowser Manager CLI — manage profiles, browsers, and automation."""
    loader = ConfigLoader()
    config = loader.load(profile=profile, cli_host=host, cli_token=token)
    ctx.ensure_object(dict)
    ctx.obj["config"] = config


def get_client(ctx: typer.Context):
    """Create a CloakBrowserManagerClient from the context's config."""
    from ..client import CloakBrowserManagerClient
    return CloakBrowserManagerClient.from_config(ctx.obj["config"])


# Register subcommand groups
from . import config_cmd
app.add_typer(config_cmd.app, name="config")
from . import profile
app.add_typer(profile.app, name="profile")
from . import browser
app.add_typer(browser.app, name="browser")
from . import run
app.add_typer(run.app, name="run")
from . import clipboard
app.add_typer(clipboard.app, name="clipboard")
