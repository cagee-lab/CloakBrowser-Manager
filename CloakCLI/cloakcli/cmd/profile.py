"""Profile CRUD subcommands: list, get, create, update, delete."""

from __future__ import annotations

from typing import Optional

import typer
from rich.console import Console

from ..utils import format_table, print_json

app = typer.Typer(name="profile", help="Manage browser profiles")


@app.command("list")
def profile_list(
    ctx: typer.Context,
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """List all profiles."""
    from ..client import CloakBrowserManagerClient
    client = CloakBrowserManagerClient.from_config(ctx.obj["config"])
    profiles = client.profiles.list()
    if json_output:
        print_json([p.model_dump() for p in profiles])
    else:
        rows = [
            {
                "id": p.id[:8] + "...",
                "name": p.name,
                "status": p.status,
                "proxy": p.proxy or "-",
                "tags": ", ".join(t.tag for t in p.tags) if p.tags else "-",
            }
            for p in profiles
        ]
        if rows:
            print(format_table(rows, ["id", "name", "status", "proxy", "tags"]))
        else:
            Console().print("[dim]No profiles found[/dim]")


@app.command("get")
def profile_get(
    ctx: typer.Context,
    profile_id: str = typer.Argument(..., help="Profile ID"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Get a single profile by ID."""
    from ..client import CloakBrowserManagerClient
    client = CloakBrowserManagerClient.from_config(ctx.obj["config"])
    profile = client.profiles.get(profile_id)
    if json_output:
        print_json(profile.model_dump())
    else:
        for key, val in profile.model_dump().items():
            if key in ("tags",) and val:
                val = ", ".join(f"{t['tag']}" for t in val)
            print(f"{key}: {val}")


@app.command("create")
def profile_create(
    ctx: typer.Context,
    name: str = typer.Option(..., "--name", help="Profile name"),
    proxy: str = typer.Option(None, "--proxy", help="Proxy URL"),
    timezone: str = typer.Option(None, "--timezone", help="IANA timezone"),
    locale: str = typer.Option(None, "--locale", help="Browser locale"),
    platform: str = typer.Option("windows", "--platform", help="OS platform"),
    screen_width: int = typer.Option(1920, "--screen-width"),
    screen_height: int = typer.Option(1080, "--screen-height"),
    humanize: bool = typer.Option(False, "--humanize/--no-humanize"),
    human_preset: str = typer.Option("default", "--human-preset"),
    headless: bool = typer.Option(False, "--headless/--no-headless"),
    geoip: bool = typer.Option(False, "--geoip/--no-geoip"),
    auto_launch: bool = typer.Option(False, "--auto-launch/--no-auto-launch"),
    seed: int = typer.Option(None, "--seed", help="Fingerprint seed"),
    user_agent: str = typer.Option(None, "--user-agent"),
    tag: list[str] = typer.Option(None, "--tag", help="Tag in key:color format"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Create a new profile."""
    from ..client import CloakBrowserManagerClient
    from ..models import TagCreate

    tags = None
    if tag:
        tags = []
        for t in tag:
            parts = t.split(":", 1)
            tags.append(TagCreate(tag=parts[0], color=parts[1] if len(parts) > 1 else None))

    client = CloakBrowserManagerClient.from_config(ctx.obj["config"])
    profile = client.profiles.create(
        name=name,
        proxy=proxy,
        timezone=timezone,
        locale=locale,
        platform=platform,
        screen_width=screen_width,
        screen_height=screen_height,
        humanize=humanize,
        human_preset=human_preset,
        headless=headless,
        geoip=geoip,
        auto_launch=auto_launch,
        fingerprint_seed=seed,
        user_agent=user_agent,
        tags=tags,
    )
    if json_output:
        print_json(profile.model_dump())
    else:
        Console().print(f"[green]Created profile:[/green] {profile.id} ({profile.name})")


@app.command("update")
def profile_update(
    ctx: typer.Context,
    profile_id: str = typer.Argument(..., help="Profile ID"),
    name: str = typer.Option(None, "--name"),
    proxy: str = typer.Option(None, "--proxy"),
    humanize: bool = typer.Option(None, "--humanize/--no-humanize"),
    human_preset: str = typer.Option(None, "--human-preset"),
    headless: bool = typer.Option(None, "--headless/--no-headless"),
    json_output: bool = typer.Option(False, "--json"),
):
    """Update an existing profile (partial update)."""
    from ..client import CloakBrowserManagerClient

    kwargs = {}
    if name is not None:
        kwargs["name"] = name
    if proxy is not None:
        kwargs["proxy"] = proxy
    if humanize is not None:
        kwargs["humanize"] = humanize
    if human_preset is not None:
        kwargs["human_preset"] = human_preset
    if headless is not None:
        kwargs["headless"] = headless

    client = CloakBrowserManagerClient.from_config(ctx.obj["config"])
    profile = client.profiles.update(profile_id, **kwargs)
    if json_output:
        print_json(profile.model_dump())
    else:
        Console().print(f"[green]Updated profile:[/green] {profile.id}")


@app.command("delete")
def profile_delete(
    ctx: typer.Context,
    profile_id: str = typer.Argument(..., help="Profile ID"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
):
    """Delete a profile."""
    if not force:
        confirm = typer.confirm(f"Delete profile {profile_id}? This cannot be undone.")
        if not confirm:
            raise typer.Abort()
    from ..client import CloakBrowserManagerClient
    client = CloakBrowserManagerClient.from_config(ctx.obj["config"])
    client.profiles.delete(profile_id)
    Console().print(f"[green]Deleted profile:[/green] {profile_id}")
