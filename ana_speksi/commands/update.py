"""ana_speksi update -- regenerate skills and commands without touching ana-speksi/."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console

from ana_speksi.models import AgentFramework, ANA_SPEKSI_DIR
from ana_speksi.skill_generator import generate_skills

console = Console()


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
    """Update agent skills and commands without touching the ana-speksi/ folder.

    Regenerates all skill files and command/prompt files for the selected
    agent frameworks based on the latest ana-speksi skill definitions and
    project config. The ana-speksi/ directory (config, ongoing, truth, archive)
    is left untouched.
    """
    config_path = project_dir / ANA_SPEKSI_DIR / "config.yml"
    if not config_path.exists():
        console.print(
            f"[red]ana-speksi is not initialized in this project. Run 'ana_speksi init' first. Config.yml not found at {config_path}.[/red]"
        )
        raise typer.Exit(1)

    # If no frameworks specified, detect which ones are already present
    if not frameworks:
        detected = _detect_frameworks(project_dir)
        if detected:
            frameworks = detected
            names = ", ".join(f.value for f in frameworks)
            console.print(f"\nDetected frameworks: [cyan]{names}[/cyan]")
        else:
            console.print(
                "[red]No agent framework directories found. "
                "Specify frameworks with --framework or run 'ana_speksi init'.[/red]"
            )
            raise typer.Exit(1)

    console.print("\nRegenerating agent skills and commands...")
    generate_skills(project_dir, frameworks)
    console.print("\n[bold green]Update complete.[/bold green]")


def _detect_frameworks(project_root: Path) -> list[AgentFramework]:
    """Detect which agent frameworks are already set up in the project."""
    detected: list[AgentFramework] = []
    framework_markers = {
        AgentFramework.CLAUDE: ".claude",
        AgentFramework.CURSOR: ".cursor",
        AgentFramework.COPILOT: ".github",
    }
    for framework, marker_dir in framework_markers.items():
        if (project_root / marker_dir).exists():
            detected.append(framework)
    return detected
