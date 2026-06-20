"""Config subcommand: config show, config path."""

from __future__ import annotations

from pathlib import Path

import typer

app = typer.Typer(name="config", help="View configuration settings")


@app.command("show")
def config_show(ctx: typer.Context):
    """Display current effective configuration."""
    from rich.console import Console
    from rich.table import Table
    from ..utils import mask_token

    config = ctx.obj["config"]
    console = Console()
    table = Table(title="Current Configuration")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")
    table.add_row("Host", config.host)
    table.add_row("Token", mask_token(config.token) if config.token else "(none)")
    console.print(table)


@app.command("path")
def config_path():
    """Show the path to the configuration file."""
    print(str(Path.home() / ".cloakcli" / "config.yaml"))
