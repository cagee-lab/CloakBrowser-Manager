"""Clipboard subcommands: read, write."""

from __future__ import annotations

import typer
from rich.console import Console

app = typer.Typer(name="clipboard", help="Read and write clipboard")


@app.command("read")
def clipboard_read(
    ctx: typer.Context,
    profile_id: str = typer.Argument(..., help="Profile ID"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Read clipboard text from a running browser profile."""
    from ..client import CloakBrowserManagerClient
    client = CloakBrowserManagerClient.from_config(ctx.obj["config"])
    text = client.clipboard.read(profile_id)
    if json_output:
        import json
        print(json.dumps({"text": text}))
    else:
        print(text)


@app.command("write")
def clipboard_write(
    ctx: typer.Context,
    profile_id: str = typer.Argument(..., help="Profile ID"),
    text: str = typer.Argument(..., help="Text to write to clipboard"),
):
    """Write text to clipboard of a running browser profile."""
    from ..client import CloakBrowserManagerClient
    client = CloakBrowserManagerClient.from_config(ctx.obj["config"])
    client.clipboard.write(profile_id, text)
    Console().print("[green]Clipboard updated[/green]")
