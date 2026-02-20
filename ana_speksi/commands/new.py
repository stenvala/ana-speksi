"""ana_speksi as-new -- start a new spec."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import typer
from rich.console import Console

from ana_speksi.models import ONGOING_DIR, make_spec_name, slugify
from ana_speksi.status import get_ana_speksi_root, ensure_dirs
from ana_speksi.resources import read_template

console = Console()


def new_command(
    ticket_id: str = typer.Argument(
        None,
        help="Ticket identifier (e.g. PROJ-123). Will be prompted if not provided.",
    ),
    description: str = typer.Argument(
        None,
        help="Short description of the change (used to derive folder name).",
    ),
    short_name: str = typer.Option(
        None,
        "--name",
        "-n",
        help="Explicit short name (kebab-case). Derived from description if not given.",
    ),
    debt_file: str = typer.Option(
        None,
        "--from-debt",
        help="Path to a technical debt document to base this change on.",
    ),
) -> None:
    """Start a new spec-driven change."""
    root = get_ana_speksi_root()
    ensure_dirs(root)
    ongoing = root / ONGOING_DIR

    # Ticket ID is required -- prompt if not provided
    if not ticket_id:
        ticket_id = typer.prompt(
            "What is the ticket ID for this change? (e.g. PROJ-123)"
        )
    if not ticket_id:
        console.print("[red]A ticket ID is required to create a new spec.[/red]")
        raise typer.Exit(1)

    # Determine short name
    if short_name:
        slug = slugify(short_name)
    elif description:
        slug = slugify(description)
    else:
        desc = typer.prompt("Describe the change in a few words")
        slug = slugify(desc)
        description = desc

    if not slug:
        console.print(
            "[red]Could not derive a valid name. Please provide one with --name.[/red]"
        )
        raise typer.Exit(1)

    folder_name = make_spec_name(ticket_id, slug)
    spec_dir = ongoing / folder_name

    if spec_dir.exists():
        console.print(f"[red]Spec directory already exists: {spec_dir}[/red]")
        raise typer.Exit(1)

    spec_dir.mkdir(parents=True)

    # Build prompt text
    prompt_text = description or ""

    # Add debt file content if provided
    if debt_file:
        debt_path = Path(debt_file)
        if debt_path.exists():
            prompt_text += f"\n\nBased on technical debt analysis:\n{debt_path.read_text(encoding='utf-8')}"
        else:
            console.print(f"[yellow]Debt file not found: {debt_file}[/yellow]")

    # Create proposal.md
    today = date.today().isoformat()
    proposal_content = read_template(
        "as-new",
        "proposal-template.md",
        name=folder_name,
        ticket_id=ticket_id,
        date=today,
        prompt=prompt_text,
        generated_with="as-new",
    )
    (spec_dir / "proposal.md").write_text(proposal_content, encoding="utf-8")

    console.print(f"\nCreated new spec: [bold cyan]{folder_name}[/bold cyan]")
    console.print(f"  Location: {spec_dir}")
    console.print(f"  Phase: [cyan]proposal[/cyan]")
    console.print(f"\nNext: Review and fill in proposal.md, then run:")
    console.print(f"  uv run ana-speksi continue {folder_name}")
