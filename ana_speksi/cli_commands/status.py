"""The ``status`` command."""

from __future__ import annotations

import toons
import typer

from ana_speksi.cli_commands._helpers import console
from ana_speksi.status import get_ana_speksi_root, print_status, print_status_json


def status_command(
    as_toon: bool = typer.Option(False, "--toon", help="Output as TOON."),
    name: str = typer.Option(
        None, "--name", "-n", help="Show status for a specific spec."
    ),
) -> None:
    """Show the current status of all ongoing specs."""
    root = get_ana_speksi_root()
    if as_toon:
        data = print_status_json(root)
        if name:
            data["ongoing"] = [s for s in data["ongoing"] if s["name"] == name]
        console.print(toons.dumps(data))
    else:
        print_status(root)
