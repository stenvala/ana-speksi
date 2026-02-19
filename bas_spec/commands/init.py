"""bas_spec init -- initialize bas-spec in a project."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console

from bas_spec.models import AgentFramework, BAS_SPEC_DIR, SUBDIRS
from bas_spec.skill_generator import generate_skills
from bas_spec.status import ensure_dirs

console = Console()


def init_command(
    frameworks: list[AgentFramework] = typer.Option(
        None,
        "--framework",
        "-f",
        help="Agent frameworks to generate skills for. Can be specified multiple times.",
    ),
    project_dir: Path = typer.Option(
        Path.cwd(),
        "--project-dir",
        "-d",
        help="Project root directory.",
    ),
) -> None:
    """Initialize bas-spec in the current project."""
    root = project_dir / BAS_SPEC_DIR

    # If no frameworks specified, ask interactively
    if not frameworks:
        console.print("\n[bold]bas-spec initialization[/bold]\n")
        console.print("Select the agent frameworks you want to generate skills for:\n")
        console.print("  1) Claude Code")
        console.print("  2) Cursor")
        console.print("  3) GitHub Copilot")
        console.print("  4) All of the above")
        console.print()

        choice = typer.prompt(
            "Enter your choice (comma-separated, e.g. 1,3)", default="4"
        )
        choices = [c.strip() for c in choice.split(",")]

        frameworks = []
        mapping = {
            "1": AgentFramework.CLAUDE,
            "2": AgentFramework.CURSOR,
            "3": AgentFramework.COPILOT,
        }

        if "4" in choices:
            frameworks = list(AgentFramework)
        else:
            for c in choices:
                if c in mapping:
                    frameworks.append(mapping[c])

        if not frameworks:
            console.print("[red]No valid frameworks selected. Aborting.[/red]")
            raise typer.Exit(1)

    # Create directory structure
    console.print(f"\nCreating bas-spec directory structure at [cyan]{root}[/cyan]")
    ensure_dirs(root)
    console.print("  Created directories:")
    for sub in SUBDIRS:
        console.print(f"    bas-spec/{sub}/")

    # Generate skills
    console.print("\nGenerating agent skills...")
    generate_skills(project_dir, frameworks)

    # Create config
    config_file = root / "config.yaml"
    if not config_file.exists():
        config_file.write_text(
            """\
# bas-spec configuration
# Adjust these settings to match your project.

# Project context injected into all skill instructions.
# Helps the AI understand your project's conventions.
context: |
  # Add your project context here.
  # Tech stack, conventions, constraints, etc.

# Per-phase rules (optional)
rules:
  proposal:
    - Keep proposals focused and concise
  storify:
    - Use WHEN/THEN format for acceptance scenarios
  taskify:
    - Each task should reference a skill
    - Include exact file paths
""",
            encoding="utf-8",
        )
        console.print(f"  Created [cyan]bas-spec/config.yaml[/cyan]")

    console.print("\n[bold green]bas-spec initialized successfully.[/bold green]")
    console.print("\nNext steps:")
    console.print("  1. Edit bas-spec/config.yaml to add your project context")
    console.print("  2. Run: uv run bas_spec new")
    console.print("     Or use the /bs-new slash command in your AI assistant")
