"""Browser lifecycle commands: launch, stop, status (registered at top level)."""

from __future__ import annotations

import typer
from rich.console import Console
from rich.table import Table

from ..utils import print_json


def launch(
    ctx: typer.Context,
    profile_id: str = typer.Argument(..., help="Profile ID to launch"),
):
    """Launch a browser for a profile."""
    from ..client import CloakBrowserManagerClient
    client = CloakBrowserManagerClient.from_config(ctx.obj["config"])
    result = client.launch(profile_id)
    console = Console()
    table = Table(title=f"Browser Launched: {profile_id}")
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="green")
    table.add_row("Status", result.status)
    table.add_row("VNC Port", str(result.vnc_ws_port))
    table.add_row("Display", result.display)
    table.add_row("CDP URL", result.cdp_url or "-")
    console.print(table)


def stop(
    ctx: typer.Context,
    profile_id: str = typer.Argument(..., help="Profile ID to stop"),
):
    """Stop a running browser."""
    from ..client import CloakBrowserManagerClient
    client = CloakBrowserManagerClient.from_config(ctx.obj["config"])
    client.stop(profile_id)
    Console().print(f"[green]Stopped browser for profile:[/green] {profile_id}")


def status(
    ctx: typer.Context,
    profile_id: str = typer.Argument(None, help="Profile ID (omit for system overview)"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Show browser or system status."""
    from ..client import CloakBrowserManagerClient
    client = CloakBrowserManagerClient.from_config(ctx.obj["config"])
    result = client.status(profile_id)
    if json_output:
        print_json(result.model_dump())
    else:
        if profile_id:
            Console().print(f"Status: {result.status}")
            if result.vnc_ws_port:
                Console().print(f"VNC Port: {result.vnc_ws_port}")
            if result.cdp_url:
                Console().print(f"CDP URL: {result.cdp_url}")
        else:
            console = Console()
            table = Table(title="System Status")
            table.add_column("Metric", style="cyan")
            table.add_column("Value", style="green")
            table.add_row("Running Profiles", str(result.running_count))
            table.add_row("Total Profiles", str(result.profiles_total))
            table.add_row("Binary Version", result.binary_version)
            console.print(table)
