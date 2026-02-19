"""ana-speksi as-one-shot -- run all phases without stopping."""

from __future__ import annotations

import typer
from rich.console import Console

console = Console()


def one_shot_command(
    description: str = typer.Argument(
        ...,
        help="Description of what to build.",
    ),
) -> None:
    """Run the full workflow (proposal -> implementation -> archive) without stopping.

    This command signals the AI agent to execute all phases sequentially
    using the as-one-shot skill.
    """
    console.print(f"\n[bold]One-shot mode[/bold]")
    console.print(f"Description: {description}")
    console.print(
        "\nThe AI agent should now execute the [bold cyan]as-one-shot[/bold cyan] skill,"
    )
    console.print(
        "which runs all phases from proposal through archive without stopping."
    )
    console.print(
        "\nPhases: proposal -> storify -> research+techify -> taskify -> codify -> docufy"
    )
