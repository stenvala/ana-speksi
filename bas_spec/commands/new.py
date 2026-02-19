"""bas_spec bs-new -- start a new spec."""

from __future__ import annotations

from datetime import date
from pathlib import Path
import subprocess
import re

import typer
from rich.console import Console

from bas_spec.models import BAS_SPEC_DIR, ONGOING_DIR, make_spec_name, slugify
from bas_spec.status import get_bas_spec_root, ensure_dirs
from bas_spec.resources import read_template

console = Console()


def _fetch_jira_description(jira_item: str) -> str | None:
    """Fetch Jira ticket description using zaira CLI."""
    try:
        result = subprocess.run(
            ["uv", "run", "zaira", "get", jira_item, "--format", "md"],
            capture_output=True,
            text=True,
            check=True,
        )
        output = result.stdout.strip()

        # Extract description from markdown output
        # The zaira output includes metadata and description
        # We want to extract the actual description content
        if not output:
            return None

        # Find description section - it's typically after the metadata
        # and before any other sections like comments
        lines = output.split("\n")
        description_lines = []
        in_description = False

        for line in lines:
            # Skip YAML front matter and metadata
            if line.strip() in ["---", ""] and not in_description:
                continue
            # Start capturing after metadata headers
            if line.startswith("#"):
                if "description" in line.lower():
                    in_description = True
                    continue
                elif in_description:
                    # Hit another section, stop
                    break
            elif in_description:
                description_lines.append(line)

        # If we didn't find a description section, use the whole output
        # minus front matter
        if not description_lines:
            # Remove front matter if present
            clean_lines = []
            skip_front_matter = False
            front_matter_count = 0

            for line in lines:
                if line.strip() == "---":
                    front_matter_count += 1
                    if front_matter_count == 2:
                        skip_front_matter = False
                        continue
                    skip_front_matter = True
                    continue
                if not skip_front_matter:
                    clean_lines.append(line)

            return "\n".join(clean_lines).strip() if clean_lines else output

        return "\n".join(description_lines).strip()

    except subprocess.CalledProcessError as e:
        console.print(
            f"[yellow]Warning: Could not fetch Jira description: {e}[/yellow]"
        )
        return None
    except FileNotFoundError:
        console.print(
            "[yellow]Warning: zaira command not found. Install zaira to fetch Jira descriptions.[/yellow]"
        )
        return None


def new_command(
    jira_item: str = typer.Argument(
        ...,
        help="Jira item identifier (e.g. PROJ-123).",
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
    root = get_bas_spec_root()
    ensure_dirs(root)
    ongoing = root / ONGOING_DIR

    # Fetch Jira description if no description provided
    jira_description = None
    if not description:
        console.print(
            f"[cyan]Fetching description from Jira item {jira_item}...[/cyan]"
        )
        jira_description = _fetch_jira_description(jira_item)
        if jira_description:
            console.print("[green]Successfully fetched Jira description[/green]")

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

    folder_name = make_spec_name(jira_item, slug)
    spec_dir = ongoing / folder_name

    if spec_dir.exists():
        console.print(f"[red]Spec directory already exists: {spec_dir}[/red]")
        raise typer.Exit(1)

    spec_dir.mkdir(parents=True)

    # Build prompt text
    # Priority: Jira description > provided description > empty
    if jira_description:
        prompt_text = jira_description
    elif description:
        prompt_text = description
    else:
        prompt_text = ""

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
        "bs-new",
        "proposal-template.md",
        name=folder_name,
        jira_item=jira_item,
        date=today,
        prompt=prompt_text,
        generated_with="bs-new",
    )
    (spec_dir / "proposal.md").write_text(proposal_content, encoding="utf-8")

    console.print(f"\nCreated new spec: [bold cyan]{folder_name}[/bold cyan]")
    console.print(f"  Location: {spec_dir}")
    console.print(f"  Phase: [cyan]proposal[/cyan]")
    console.print(f"\nNext: Review and fill in proposal.md, then run:")
    console.print(f"  uv run bas_spec continue {folder_name}")
