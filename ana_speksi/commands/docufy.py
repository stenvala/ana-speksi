"""ana-speksi as-docufy -- archive and update truth."""

from __future__ import annotations

import shutil
from datetime import date
from pathlib import Path

import typer
from rich.console import Console

from ana-speksi.models import ARCHIVE_DIR, ONGOING_DIR
from ana-speksi.status import get_ana-speksi_root, list_ongoing_specs

console = Console()


def docufy_command(
    name: str = typer.Argument(
        None,
        help="Name of the spec to archive.",
    ),
) -> None:
    """Archive a completed spec and update ground truth."""
    root = get_ana-speksi_root()
    specs = list_ongoing_specs(root)

    if not specs:
        console.print("[yellow]No ongoing specs found.[/yellow]")
        raise typer.Exit(1)

    # Find spec
    spec = None
    if name:
        for s in specs:
            if s.name == name or s.name.endswith(f"-{name}"):
                spec = s
                break
    elif len(specs) == 1:
        spec = specs[0]

    if not spec:
        console.print("[red]Specify which spec to archive.[/red]")
        for s in specs:
            console.print(f"  - {s.name} (phase: {s.phase.value})")
        raise typer.Exit(1)

    # Archive
    today = date.today().isoformat()
    archive_name = f"{today}-{spec.name}"
    archive_dir = root / ARCHIVE_DIR / archive_name
    source_dir = spec.path

    if archive_dir.exists():
        console.print(f"[red]Archive already exists: {archive_dir}[/red]")
        raise typer.Exit(1)

    shutil.move(str(source_dir), str(archive_dir))
    console.print(f"\nArchived [bold]{spec.name}[/bold] to:")
    console.print(f"  ana-speksi/archive/{archive_name}/")
    console.print("\nThe AI agent should now update ground truth (ana-speksi/truth/).")
    console.print(
        "Invoke the [bold cyan]as-docufy[/bold cyan] skill for detailed instructions."
    )
