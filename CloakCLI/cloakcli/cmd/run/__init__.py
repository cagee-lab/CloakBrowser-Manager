"""Run subcommand group — browser automation via CDP."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any

import typer
from rich.console import Console

from ...utils import print_json

app = typer.Typer(name="run", help="Execute browser automation commands", no_args_is_help=True)
console = Console()


@app.callback()
def run_callback(
    ctx: typer.Context,
    profile_id: str = typer.Argument(..., help="Profile ID"),
):
    """Profile ID shared by all run subcommands."""
    ctx.ensure_object(dict)
    ctx.obj["profile_id"] = profile_id


def _run_async(coro) -> Any:
    """Run an async coroutine synchronously."""
    return asyncio.run(coro)


def _get_client(ctx: typer.Context):
    from ...client import CloakBrowserManagerClient
    return CloakBrowserManagerClient.from_config(ctx.obj["config"])


def _get_profile_id(ctx: typer.Context) -> str:
    return ctx.obj.get("profile_id", "")


# --- Navigation ---

@app.command("open")
def run_open(
    ctx: typer.Context,
    url: str = typer.Argument(..., help="URL to navigate to"),
    fast: bool = typer.Option(False, "--fast", help="Skip humanize"),
):
    """Navigate to a URL."""
    async def _go():
        client = _get_client(ctx)
        await client.run.open(_get_profile_id(ctx), url, fast=fast)
        client.close()
    _run_async(_go())
    console.print(f"[green]Navigated to:[/green] {url}")


@app.command("back")
def run_back(
    ctx: typer.Context,
    
    fast: bool = typer.Option(False, "--fast"),
):
    """Go back in browser history."""
    async def _go():
        client = _get_client(ctx)
        await client.run.back(_get_profile_id(ctx), fast=fast)
        client.close()
    _run_async(_go())
    console.print("[green]Navigated back[/green]")


@app.command("forward")
def run_forward(
    ctx: typer.Context,
    
    fast: bool = typer.Option(False, "--fast"),
):
    """Go forward in browser history."""
    async def _go():
        client = _get_client(ctx)
        await client.run.forward(_get_profile_id(ctx), fast=fast)
        client.close()
    _run_async(_go())
    console.print("[green]Navigated forward[/green]")


@app.command("reload")
def run_reload(
    ctx: typer.Context,
    
    fast: bool = typer.Option(False, "--fast"),
):
    """Reload the current page."""
    async def _go():
        client = _get_client(ctx)
        await client.run.reload(_get_profile_id(ctx), fast=fast)
        client.close()
    _run_async(_go())
    console.print("[green]Page reloaded[/green]")


# --- Interactions ---

@app.command("click")
def run_click(
    ctx: typer.Context,
    
    selector: str = typer.Argument(..., help="CSS selector or @ref"),
    fast: bool = typer.Option(False, "--fast"),
):
    """Click an element."""
    async def _go():
        client = _get_client(ctx)
        await client.run.click(_get_profile_id(ctx), selector, fast=fast)
        client.close()
    _run_async(_go())
    console.print(f"[green]Clicked:[/green] {selector}")


@app.command("dblclick")
def run_dblclick(
    ctx: typer.Context,
    
    selector: str = typer.Argument(..., help="CSS selector or @ref"),
    fast: bool = typer.Option(False, "--fast"),
):
    """Double-click an element."""
    async def _go():
        client = _get_client(ctx)
        await client.run.dblclick(_get_profile_id(ctx), selector, fast=fast)
        client.close()
    _run_async(_go())
    console.print(f"[green]Double-clicked:[/green] {selector}")


@app.command("type")
def run_type(
    ctx: typer.Context,
    
    selector: str = typer.Argument(..., help="CSS selector or @ref"),
    text: str = typer.Argument(..., help="Text to type"),
    fast: bool = typer.Option(False, "--fast"),
):
    """Type text into an element (preserves existing content)."""
    async def _go():
        client = _get_client(ctx)
        await client.run.type(_get_profile_id(ctx), selector, text, fast=fast)
        client.close()
    _run_async(_go())
    console.print(f"[green]Typed into {selector}[/green]")


@app.command("fill")
def run_fill(
    ctx: typer.Context,
    
    selector: str = typer.Argument(..., help="CSS selector or @ref"),
    text: str = typer.Argument(..., help="Text to fill"),
    fast: bool = typer.Option(False, "--fast"),
):
    """Clear and fill an input element."""
    async def _go():
        client = _get_client(ctx)
        await client.run.fill(_get_profile_id(ctx), selector, text, fast=fast)
        client.close()
    _run_async(_go())
    console.print(f"[green]Filled {selector}[/green]")


@app.command("press")
def run_press(
    ctx: typer.Context,
    
    key: str = typer.Argument(..., help="Key to press (Enter, Tab, Escape, Control+a, etc.)"),
    fast: bool = typer.Option(False, "--fast"),
):
    """Press a keyboard key."""
    async def _go():
        client = _get_client(ctx)
        await client.run.press(_get_profile_id(ctx), key, fast=fast)
        client.close()
    _run_async(_go())
    console.print(f"[green]Pressed:[/green] {key}")


@app.command("hover")
def run_hover(
    ctx: typer.Context,
    
    selector: str = typer.Argument(..., help="CSS selector or @ref"),
    fast: bool = typer.Option(False, "--fast"),
):
    """Hover over an element."""
    async def _go():
        client = _get_client(ctx)
        await client.run.hover(_get_profile_id(ctx), selector, fast=fast)
        client.close()
    _run_async(_go())
    console.print(f"[green]Hovered:[/green] {selector}")


@app.command("focus")
def run_focus(
    ctx: typer.Context,
    
    selector: str = typer.Argument(..., help="CSS selector or @ref"),
    fast: bool = typer.Option(False, "--fast"),
):
    """Focus an element."""
    async def _go():
        client = _get_client(ctx)
        await client.run.focus(_get_profile_id(ctx), selector, fast=fast)
        client.close()
    _run_async(_go())
    console.print(f"[green]Focused:[/green] {selector}")


@app.command("select")
def run_select(
    ctx: typer.Context,
    
    selector: str = typer.Argument(..., help="CSS selector or @ref"),
    value: str = typer.Argument(..., help="Option value to select"),
    fast: bool = typer.Option(False, "--fast"),
):
    """Select a dropdown option."""
    async def _go():
        client = _get_client(ctx)
        await client.run.select(_get_profile_id(ctx), selector, value, fast=fast)
        client.close()
    _run_async(_go())
    console.print(f"[green]Selected '{value}' in {selector}[/green]")


@app.command("check")
def run_check(
    ctx: typer.Context,
    
    selector: str = typer.Argument(..., help="CSS selector or @ref"),
    fast: bool = typer.Option(False, "--fast"),
):
    """Check a checkbox."""
    async def _go():
        client = _get_client(ctx)
        await client.run.check(_get_profile_id(ctx), selector, fast=fast)
        client.close()
    _run_async(_go())
    console.print(f"[green]Checked:[/green] {selector}")


@app.command("uncheck")
def run_uncheck(
    ctx: typer.Context,
    
    selector: str = typer.Argument(..., help="CSS selector or @ref"),
    fast: bool = typer.Option(False, "--fast"),
):
    """Uncheck a checkbox."""
    async def _go():
        client = _get_client(ctx)
        await client.run.uncheck(_get_profile_id(ctx), selector, fast=fast)
        client.close()
    _run_async(_go())
    console.print(f"[green]Unchecked:[/green] {selector}")


# --- Information ---

@app.command("get")
def run_get(
    ctx: typer.Context,
    
    what: str = typer.Argument(..., help="What to get: text, html, value, attr, title, url, count, box"),
    selector: str = typer.Argument(None, help="CSS selector (required for text/html/value/attr/count/box)"),
    attr_name: str = typer.Argument(None, help="Attribute name (for 'attr')"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Get information from the page."""
    async def _go():
        client = _get_client(ctx)
        if what == "text":
            return await client.run.get_text(_get_profile_id(ctx), selector)
        elif what == "html":
            return await client.run.get_html(_get_profile_id(ctx), selector)
        elif what == "value":
            return await client.run.get_value(_get_profile_id(ctx), selector)
        elif what == "attr":
            return await client.run.get_attr(_get_profile_id(ctx), selector, attr_name or "")
        elif what == "title":
            return await client.run.get_title(_get_profile_id(ctx))
        elif what == "url":
            return await client.run.get_url(_get_profile_id(ctx))
        elif what == "count":
            return await client.run.get_count(_get_profile_id(ctx), selector)
        elif what == "box":
            return await client.run.get_box(_get_profile_id(ctx), selector)
        else:
            raise typer.BadParameter(f"Unknown get target: {what}")
    result = _run_async(_go())
    if json_output:
        print_json(result)
    else:
        print(result)


# --- Capture ---

@app.command("snapshot")
def run_snapshot(
    ctx: typer.Context,
    
    interactive: bool = typer.Option(False, "-i", "--interactive", help="Interactive elements only"),
    compact: bool = typer.Option(False, "-c", "--compact", help="Compact mode (skip empty containers)"),
    depth: int = typer.Option(None, "-d", "--depth", help="Max depth"),
    scope: str = typer.Option(None, "-s", "--scope", help="CSS selector scope"),
    fast: bool = typer.Option(False, "--fast"),
):
    """Take an accessibility tree snapshot (agent-browser compatible)."""
    async def _go():
        client = _get_client(ctx)
        result = await client.run.snapshot(
            _get_profile_id(ctx),
            interactive_only=interactive,
            compact=compact,
            max_depth=depth,
            scope=scope,
        )
        client.close()
        return result
    result = _run_async(_go())
    print(result)


@app.command("screenshot")
def run_screenshot(
    ctx: typer.Context,
    
    path: str = typer.Argument(None, help="Output file path"),
    full: bool = typer.Option(False, "--full", help="Full page screenshot"),
    fast: bool = typer.Option(False, "--fast"),
):
    """Take a screenshot."""
    async def _go():
        client = _get_client(ctx)
        result = await client.run.screenshot(_get_profile_id(ctx), path=path, full=full, fast=fast)
        client.close()
        return result
    dest = _run_async(_go())
    console.print(f"[green]Screenshot saved:[/green] {dest}")


@app.command("pdf")
def run_pdf(
    ctx: typer.Context,
    
    path: str = typer.Argument(..., help="Output PDF path"),
    fast: bool = typer.Option(False, "--fast"),
):
    """Save page as PDF."""
    async def _go():
        client = _get_client(ctx)
        result = await client.run.pdf(_get_profile_id(ctx), path, fast=fast)
        client.close()
        return result
    dest = _run_async(_go())
    console.print(f"[green]PDF saved:[/green] {dest}")


@app.command("eval")
def run_eval(
    ctx: typer.Context,
    
    code: str = typer.Argument(..., help="JavaScript code to execute"),
    fast: bool = typer.Option(False, "--fast"),
    json_output: bool = typer.Option(False, "--json"),
):
    """Execute JavaScript in the page context."""
    async def _go():
        client = _get_client(ctx)
        result = await client.run.eval(_get_profile_id(ctx), code, fast=fast)
        client.close()
        return result
    result = _run_async(_go())
    if json_output:
        print_json(result)
    else:
        print(result)


# --- Tab ---

@app.command("tab")
def run_tab_list(
    ctx: typer.Context,
    
    json_output: bool = typer.Option(False, "--json"),
):
    """List all browser tabs."""
    async def _go():
        client = _get_client(ctx)
        result = await client.run.tab_list(_get_profile_id(ctx))
        client.close()
        return result
    tabs = _run_async(_go())
    if json_output:
        print_json(tabs)
    else:
        for t in tabs:
            marker = " (active)" if t["active"] else ""
            print(f"{t['index']}: \"{t['title']}\" [{t['url']}]{marker}")


@app.command("tab-new")
def run_tab_new(
    ctx: typer.Context,
    
    url: str = typer.Argument(None, help="URL to open (omit for blank tab)"),
    fast: bool = typer.Option(False, "--fast"),
):
    """Open a new tab."""
    async def _go():
        client = _get_client(ctx)
        result = await client.run.tab_new(_get_profile_id(ctx), url=url, fast=fast)
        client.close()
        return result
    _run_async(_go())
    console.print(f"[green]New tab opened[/green]" + (f" at {url}" if url else ""))


@app.command("tab-switch")
def run_tab_switch(
    ctx: typer.Context,
    
    tab_ref: str = typer.Argument(..., help="Tab reference (t1, t2, ... or label)"),
    fast: bool = typer.Option(False, "--fast"),
):
    """Switch to a specific tab."""
    async def _go():
        client = _get_client(ctx)
        await client.run.tab_switch(_get_profile_id(ctx), tab_ref, fast=fast)
        client.close()
    _run_async(_go())
    console.print(f"[green]Switched to tab:[/green] {tab_ref}")


@app.command("tab-close")
def run_tab_close(
    ctx: typer.Context,
    
    tab_ref: str = typer.Argument(None, help="Tab reference (omit for current)"),
    fast: bool = typer.Option(False, "--fast"),
):
    """Close a tab."""
    async def _go():
        client = _get_client(ctx)
        await client.run.tab_close(_get_profile_id(ctx), tab_ref=tab_ref, fast=fast)
        client.close()
    _run_async(_go())
    console.print(f"[green]Closed tab[/green]" + (f" {tab_ref}" if tab_ref else " (current)"))


@app.command("window-new")
def run_window_new(
    ctx: typer.Context,
    
    fast: bool = typer.Option(False, "--fast"),
):
    """Open a new browser window."""
    async def _go():
        client = _get_client(ctx)
        await client.run.window_new(_get_profile_id(ctx), fast=fast)
        client.close()
    _run_async(_go())
    console.print("[green]New window created[/green]")


# --- Utility ---

@app.command("wait")
def run_wait(
    ctx: typer.Context,
    
    target: str = typer.Argument(..., help="Milliseconds to wait or CSS selector"),
    load_state: str = typer.Option(None, "--load", help="Wait for load state (load, domcontentloaded, networkidle)"),
    state: str = typer.Option("visible", "--state", help="Element state (visible, hidden)"),
    fast: bool = typer.Option(False, "--fast"),
):
    """Wait for a condition."""
    async def _go():
        client = _get_client(ctx)
        await client.run.wait(_get_profile_id(ctx), target, fast=fast, load_state=load_state, state=state)
        client.close()
    _run_async(_go())
    console.print(f"[green]Wait completed:[/green] {target}")


@app.command("scroll")
def run_scroll(
    ctx: typer.Context,
    
    direction: str = typer.Argument(..., help="Scroll direction: up, down, left, right"),
    px: int = typer.Argument(300, help="Pixels to scroll"),
    fast: bool = typer.Option(False, "--fast"),
):
    """Scroll the page."""
    async def _go():
        client = _get_client(ctx)
        await client.run.scroll(_get_profile_id(ctx), direction, px, fast=fast)
        client.close()
    _run_async(_go())
    console.print(f"[green]Scrolled {direction} {px}px[/green]")


@app.command("scrollintoview")
def run_scrollintoview(
    ctx: typer.Context,
    
    selector: str = typer.Argument(..., help="CSS selector or @ref"),
    fast: bool = typer.Option(False, "--fast"),
):
    """Scroll an element into view."""
    async def _go():
        client = _get_client(ctx)
        await client.run.scrollintoview(_get_profile_id(ctx), selector, fast=fast)
        client.close()
    _run_async(_go())
    console.print(f"[green]Scrolled into view:[/green] {selector}")


@app.command("batch")
def run_batch(
    ctx: typer.Context,
    
    commands_file: str = typer.Argument(..., help="JSON file with commands array"),
    fast: bool = typer.Option(False, "--fast", help="Skip humanize"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Execute a batch of commands from a JSON file in a single CDP connection."""
    with open(commands_file) as f:
        commands = json.load(f)

    async def _go():
        client = _get_client(ctx)
        results = await client.run.batch(_get_profile_id(ctx), commands, fast=fast)
        client.close()
        return results

    results = _run_async(_go())
    if json_output:
        print_json(results)
    else:
        for i, r in enumerate(results):
            if r is None:
                console.print(f"[dim]{i + 1}. {commands[i][0]}[/dim] [green]OK[/green]")
            elif isinstance(r, dict) and "error" in r:
                console.print(f"[dim]{i + 1}. {commands[i][0]}[/dim] [red]Error: {r['error']}[/red]")
            else:
                console.print(f"[dim]{i + 1}. {commands[i][0]}[/dim] [green]{r}[/green]")
