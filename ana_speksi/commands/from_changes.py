"""ana-speksi as-from-changes -- create truth from existing changes."""

from __future__ import annotations

from typing import Optional

import typer
from rich.console import Console

console = Console()


def from_changes_command(
    staged: bool = typer.Option(False, "--staged", help="From git staged changes."),
    commit: Optional[str] = typer.Option(
        None, "--commit", help="From a specific commit hash."
    ),
    pr: Optional[str] = typer.Option(None, "--pr", help="From a pull request number."),
    diff: bool = typer.Option(False, "--diff", help="From current git diff."),
    folder: Optional[str] = typer.Option(
        None, "--folder", help="From a specific folder."
    ),
    codebase: bool = typer.Option(
        False, "--codebase", help="From the entire codebase."
    ),
) -> None:
    """Create or update ground truth from existing changes.

    Retroactively document changes that were made without a spec,
    or initialize truth for an existing codebase.
    """
    source = None
    if staged:
        source = "staged"
    elif commit:
        source = f"commit:{commit}"
    elif pr:
        source = f"pr:{pr}"
    elif diff:
        source = "diff"
    elif folder:
        source = f"folder:{folder}"
    elif codebase:
        source = "codebase"

    if not source:
        console.print("\n[bold]as-from-changes[/bold]")
        console.print("\nNo source specified. Available options:")
        console.print("  --staged     From git staged changes")
        console.print("  --commit N   From a specific commit")
        console.print("  --pr N       From a pull request")
        console.print("  --diff       From current git diff")
        console.print("  --folder P   From a specific folder")
        console.print("  --codebase   From the entire codebase")
        console.print("\nThe AI agent should ask the user which source to use.")
        return

    console.print(f"\n[bold]as-from-changes[/bold]")
    console.print(f"Source: [cyan]{source}[/cyan]")
    console.print(
        "\nThe AI agent should now execute the [bold cyan]as-from-changes[/bold cyan] skill"
    )
    console.print(f"to analyze the {source} and create/update ground truth.")
