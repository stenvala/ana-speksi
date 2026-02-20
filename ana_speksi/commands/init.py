"""ana_speksi init -- initialize ana_speksi in a project."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console

from ana_speksi.models import AgentFramework, ANA_SPEKSI_DIR, SUBDIRS
from ana_speksi.skill_generator import generate_skills
from ana_speksi.status import ensure_dirs

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
    """Initialize ana_speksi in the current project."""
    root = project_dir / ANA_SPEKSI_DIR

    # If no frameworks specified, ask interactively
    if not frameworks:
        console.print("\n[bold]ana_speksi initialization[/bold]\n")
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
    console.print(f"\nCreating ana-speksi directory structure at [cyan]{root}[/cyan]")
    ensure_dirs(root)
    console.print("  Created directories:")
    for sub in SUBDIRS:
        console.print(f"    ana-speksi/{sub}/")

    # Generate skills
    console.print("\nGenerating agent skills...")
    generate_skills(project_dir, frameworks)

    # Create config
    config_file = root / "config.yml"
    if not config_file.exists():
        config_file.write_text(
            """\
# ana_speksi configuration
# Adjust these settings to match your project.

# When true, the AI agent skips all confirmation prompts during acceptance
# and other interactive steps -- it still notifies you of every action.
auto_confirm: false

# When true, the AI agent automatically continues to the next story during
# the codify phase without asking for confirmation between stories.
auto_story_implementation_continue: false

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
        console.print(f"  Created [cyan]ana-speksi/config.yml[/cyan]")

    console.print("\n[bold green]ana_speksi initialized successfully.[/bold green]")
    console.print("\nNext steps:")
    console.print("  1. Edit ana-speksi/config.yml to add your project context")
    console.print("  2. Run: uv run ana-speksi new")
    console.print("     Or use the /as-new slash command in your AI assistant")
