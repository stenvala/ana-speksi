"""ana-speksi as-codify -- implementation phase (delegates to AI via skill)."""

from __future__ import annotations

import typer
from rich.console import Console

from ana-speksi.commands.continue_cmd import continue_command

console = Console()


def codify_command(
    name: str = typer.Argument(
        None,
        help="Name of the spec to implement.",
    ),
) -> None:
    """Start or continue implementation of a spec (codify phase).

    This is a convenience alias for as-continue that signals
    the AI agent to enter the codify (implementation) phase.
    """
    continue_command(name=name)
