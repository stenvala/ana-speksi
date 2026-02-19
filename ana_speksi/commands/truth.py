"""ana-speksi as-truth -- manage ground truth."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.tree import Tree

from ana-speksi.models import TRUTH_DIR
from ana-speksi.status import get_ana-speksi_root

console = Console()

truth_app = typer.Typer(
    name="as-truth",
    help="Manage the ground truth hierarchy.",
    no_args_is_help=True,
)


@truth_app.command("show")
def truth_show() -> None:
    """Display the current ground truth hierarchy."""
    root = get_ana-speksi_root()
    truth_dir = root / TRUTH_DIR

    if not truth_dir.exists() or not any(truth_dir.iterdir()):
        console.print(
            "[dim]Ground truth is empty. Run as-docufy or as-from-changes to populate it.[/dim]"
        )
        return

    tree = Tree(f"[bold]ana-speksi/truth/[/bold]")
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

    The AI agent will execute the as-truth-rearrange skill to reorganize
    the truth directory based on your description.
    """
    console.print(f"\n[bold]Truth Rearrangement[/bold]")
    console.print(f"Request: {description}")
    console.print(
        "\nThe AI agent should now execute the [bold cyan]as-truth-rearrange[/bold cyan] skill."
    )


def _build_tree(directory: Path, tree: Tree) -> None:
    """Recursively build a rich Tree from a directory."""
    for child in sorted(directory.iterdir()):
        if child.is_dir():
            branch = tree.add(f"[bold]{child.name}/[/bold]")
            _build_tree(child, branch)
        else:
            tree.add(child.name)
