"""The ``truth`` sub-app."""

from __future__ import annotations

import typer
from rich.tree import Tree

from ana_speksi.cli_commands._helpers import console
from ana_speksi.models import TRUTH_DIR
from ana_speksi.status import build_truth_tree, get_ana_speksi_root

truth_app = typer.Typer(
    name="as-truth",
    help="Manage the ground truth hierarchy.",
    no_args_is_help=True,
)


@truth_app.command("show")
def truth_show() -> None:
    """Display the current ground truth hierarchy."""
    root = get_ana_speksi_root()
    truth_dir = root / TRUTH_DIR

    if not truth_dir.exists() or not any(truth_dir.iterdir()):
        console.print(
            "[dim]Ground truth is empty. "
            "Run as-docufy or as-from-changes to populate it.[/dim]"
        )
        return

    tree = Tree("[bold]ana-speksi/truth/[/bold]")
    build_truth_tree(truth_dir, tree)
    console.print(tree)
