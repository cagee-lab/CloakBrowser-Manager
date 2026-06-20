"""Shared utilities for CLI output formatting and helpers."""

from __future__ import annotations

import json
from typing import Any


def format_table(rows: list[dict], columns: list[str], title: str | None = None) -> str:
    """Render a list of dicts as a Rich-powered table string.

    Args:
        rows: List of dicts with column keys.
        columns: Column keys in display order.
        title: Optional table title.
    """
    from rich.console import Console
    from rich.table import Table

    console = Console(no_color=False)
    table = Table(title=title, show_lines=False, leading=1)
    for col in columns:
        table.add_column(col, no_wrap=True)
    for row in rows:
        table.add_row(*[str(row.get(col, "")) for col in columns])
    # Capture to string
    with console.capture() as capture:
        console.print(table)
    return capture.get()


def print_json(data: Any) -> None:
    """Print data as formatted JSON to stdout."""
    print(json.dumps(data, indent=2, ensure_ascii=False, default=str))


def mask_token(token: str) -> str:
    """Mask a token string for safe display: show first 4 and last 4 chars."""
    if len(token) <= 8:
        return token[:2] + "***"
    return token[:4] + "***" + token[-4:]


def resolve_ref(page: Any, ref: str) -> str:
    """Resolve an @ref (e.g. @e3) to a CSS selector using data-snapshot-ref attribute.

    Args:
        page: Playwright Page object.
        ref: The @ref string from snapshot output.

    Returns:
        CSS selector string like '[data-snapshot-ref="e3"]'.
    """
    if not ref.startswith("@"):
        return ref  # already a CSS selector
    ref_id = ref[1:]  # strip @
    return f'[data-snapshot-ref="{ref_id}"]'
