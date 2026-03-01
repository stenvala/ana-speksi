"""The ``update`` command."""

from __future__ import annotations

from pathlib import Path

import typer

from ana_speksi.cli_commands._helpers import console
from ana_speksi.models import ANA_SPEKSI_DIR, AgentFramework
from ana_speksi.skill_generator import detect_frameworks, generate_skills


def update_command(
    frameworks: list[AgentFramework] = typer.Option(
        None,
        "--framework",
        "-f",
        help="Agent frameworks to update. Can be specified multiple times.",
    ),
    project_dir: Path = typer.Option(
        Path.cwd(),
        "--project-dir",
        "-d",
        help="Project root directory.",
    ),
) -> None:
    """Update agent skills and commands without touching the ana-speksi/ folder."""
    config_path = project_dir / ANA_SPEKSI_DIR / "config.yml"
    if not config_path.exists():
        console.print(
            f"[red]ana-speksi is not initialized in this project. "
            f"Run 'ana-speksi init' first. Config.yml not found at {config_path}.[/red]"
        )
        raise typer.Exit(1)

    if not frameworks:
        detected = detect_frameworks(project_dir)
        if detected:
            frameworks = detected
            names = ", ".join(f.value for f in frameworks)
            console.print(f"\nDetected frameworks: [cyan]{names}[/cyan]")
        else:
            console.print(
                "[red]No agent framework directories found. "
                "Specify frameworks with --framework or run 'ana-speksi init'.[/red]"
            )
            raise typer.Exit(1)

    console.print("\nRegenerating agent skills and commands...")
    generate_skills(project_dir, frameworks)
    console.print("\n[bold green]Update complete.[/bold green]")
