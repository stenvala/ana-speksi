"""Shared helpers for CLI commands."""

from __future__ import annotations

import typer
from rich.console import Console

console = Console()


def find_spec(specs: list, name: str | None):
    """Find a spec by name, or auto-select if only one exists."""
    if name:
        for s in specs:
            if s.name == name or s.name.endswith(f"-{name}"):
                return s
        console.print(f"[red]Spec not found: {name}[/red]")
        for s in specs:
            console.print(f"  - {s.name} (phase: {s.phase.value})")
        raise typer.Exit(1)
    if len(specs) == 1:
        return specs[0]
    console.print("Multiple ongoing specs found. Specify which one:")
    for s in specs:
        console.print(f"  - {s.name} (phase: {s.phase.value})")
    raise typer.Exit(1)
