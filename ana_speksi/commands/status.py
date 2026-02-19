"""ana-speksi status -- show current status of all specs."""

from __future__ import annotations

import toons

import typer
from rich.console import Console

from ana-speksi.status import get_ana-speksi_root, print_status, print_status_json

console = Console()


def status_command(
    as_toon: bool = typer.Option(
        False,
        "--toon",
        help="Output as TOON.",
    ),
    name: str = typer.Option(
        None,
        "--name",
        "-n",
        help="Show status for a specific spec.",
    ),
) -> None:
    """Show the current status of all ongoing specs."""
    root = get_ana-speksi_root()

    if as_toon:
        data = print_status_json(root)
        if name:
            data["ongoing"] = [s for s in data["ongoing"] if s["name"] == name]
        console.print(toons.dumps(data))
    else:
        print_status(root)
