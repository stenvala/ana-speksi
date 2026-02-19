"""bas_spec bs-truth -- manage ground truth."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.tree import Tree

from bas_spec.models import TRUTH_DIR
from bas_spec.status import get_bas_spec_root

console = Console()

truth_app = typer.Typer(
    name="bs-truth",
    help="Manage the ground truth hierarchy.",
    no_args_is_help=True,
)


@truth_app.command("show")
def truth_show() -> None:
    """Display the current ground truth hierarchy."""
    root = get_bas_spec_root()
    truth_dir = root / TRUTH_DIR

    if not truth_dir.exists() or not any(truth_dir.iterdir()):
        console.print("[dim]Ground truth is empty. Run bs-docufy or bs-from-changes to populate it.[/dim]")
        return

    tree = Tree(f"[bold]bas-spec/truth/[/bold]")
    _build_tree(truth_dir, tree)
    console.print(tree)


@truth_app.command("rearrange")
def truth_rearrange(
    description: str = typer.Argument(
        ...,
        help="Describe how truth should be rearranged.",
    ),
) -> None:
    """Rearrange the ground truth hierarchy.

    The AI agent will execute the bs-truth-rearrange skill to reorganize
    the truth directory based on your description.
    """
    console.print(f"\n[bold]Truth Rearrangement[/bold]")
    console.print(f"Request: {description}")
    console.print(
        "\nThe AI agent should now execute the [bold cyan]bs-truth-rearrange[/bold cyan] skill."
    )


def _build_tree(directory: Path, tree: Tree) -> None:
    """Recursively build a rich Tree from a directory."""
    for child in sorted(directory.iterdir()):
        if child.is_dir():
            branch = tree.add(f"[bold]{child.name}/[/bold]")
            _build_tree(child, branch)
        else:
            tree.add(child.name)
