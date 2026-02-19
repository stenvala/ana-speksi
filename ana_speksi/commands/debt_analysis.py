"""ana_speksi as-debt-analysis -- analyze technical debt."""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from ana_speksi.models import TECHNICAL_DEBT_DIR
from ana_speksi.status import get_ana_speksi_root, ensure_dirs
from ana_speksi.resources import read_template

console = Console()


def debt_analysis_command(
    target: str = typer.Argument(
        ...,
        help="Folder path or skill name to analyze.",
    ),
    scope: Optional[str] = typer.Option(
        None,
        "--scope",
        "-s",
        help="Scope description (e.g. 'database layer', 'API endpoints').",
    ),
) -> None:
    """Analyze technical debt by comparing code against skills.

    NO CODE CHANGES ARE ALLOWED during this analysis.
    """
    root = get_ana_speksi_root()
    ensure_dirs(root)

    today = date.today().isoformat()
    area = target.replace("/", "-").replace("\\", "-").strip("-")
    debt_filename = f"{today}-{area}.md"
    debt_path = root / TECHNICAL_DEBT_DIR / debt_filename

    # Create template
    content = read_template(
        "as-debt-analysis",
        "debt-analysis-template.md",
        area=target,
        date=today,
        scope=scope or target,
    )
    debt_path.write_text(content, encoding="utf-8")

    console.print(f"\n[bold]Technical Debt Analysis[/bold]")
    console.print(f"Target: [cyan]{target}[/cyan]")
    console.print(f"Document: [cyan]ana_speksi/technical-debt/{debt_filename}[/cyan]")
    console.print(
        "\nThe AI agent should now execute the [bold cyan]as-debt-analysis[/bold cyan] skill"
    )
    console.print("to analyze the target and fill in the debt document.")
    console.print(
        "\n[yellow]NO CODE CHANGES ARE ALLOWED during this analysis.[/yellow]"
    )
    console.print(
        "\nAfter analysis, you can run: "
        f"uv run ana_speksi new --from-debt ana_speksi/technical-debt/{debt_filename}"
    )
