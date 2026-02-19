"""bas_spec jira-stories -- list Jira story/subtask associations for specs."""

from __future__ import annotations

import re
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

import toons
from bas_spec.status import get_bas_spec_root, list_ongoing_specs

console = Console()


def _extract_jira_item_from_index(index_path: Path) -> str | None:
    """Extract the top-level Jira item from index.md."""
    if not index_path.exists():
        return None
    content = index_path.read_text(encoding="utf-8")
    # Look for **Jira Item**: VALUE pattern
    match = re.search(r"\*\*Jira Item\*\*:\s*([A-Z0-9]+-\d+)", content)
    return match.group(1) if match else None


def _extract_story_jira_items(index_path: Path) -> dict[str, str | None]:
    """Extract Jira items for each story from index.md.

    Returns a dict mapping story folder name to Jira item (or None if not set).
    """
    if not index_path.exists():
        return {}

    content = index_path.read_text(encoding="utf-8")
    stories = {}

    # Parse story sections: #### NN-story-name followed by optional **Jira Item**: VALUE
    # Pattern: #### story-name\n...**Jira Item**: VALUE (or absent)
    story_pattern = re.compile(r"####\s+(\d+-[^\n]+)\n(.*?)(?=####|\Z)", re.DOTALL)

    for match in story_pattern.finditer(content):
        story_name = match.group(1).strip()
        story_section = match.group(2)

        jira_match = re.search(r"\*\*Jira Item\*\*:\s*([A-Z0-9]+-\d+)", story_section)
        stories[story_name] = jira_match.group(1) if jira_match else None

    return stories


def jira_stories_command(
    spec_name: str = typer.Argument(
        None,
        help="Specific spec name to check (optional, defaults to all ongoing).",
    ),
    item_type: str = typer.Option(
        "story",
        "--item-type",
        "-t",
        help="Type of Jira item to manage: 'story' (parent=epic) or 'subtask' (parent=story).",
    ),
    as_toon: bool = typer.Option(
        False,
        "--toon",
        help="Output in TOON format for AI agents.",
    ),
) -> None:
    """List Jira story/subtask associations for specs.

    Shows which specs and stories have Jira items associated and which don't.
    Use --item-type subtask when the parent is a Story and items are Sub-tasks.
    """
    root = get_bas_spec_root()
    specs = list_ongoing_specs(root)

    if spec_name:
        specs = [s for s in specs if s.name == spec_name]
        if not specs:
            console.print(f"[red]Spec not found: {spec_name}[/red]")
            raise typer.Exit(1)

    if not specs:
        console.print("[dim]No ongoing specs found.[/dim]")
        return

    results = []

    for spec in specs:
        index_path = spec.path / "index.md"
        parent_jira = _extract_jira_item_from_index(index_path)

        # Also extract from folder name (format: JIRA-123.slug)
        folder_jira = None
        if "." in spec.name:
            folder_jira = spec.name.split(".")[0]

        story_jiras = _extract_story_jira_items(index_path)

        spec_result = {
            "name": spec.name,
            "path": str(spec.path),
            "item_type": item_type,
            "parent_jira_from_folder": folder_jira,
            "parent_jira_from_index": parent_jira,
            "stories": [],
        }

        for story in spec.stories:
            jira_item = story_jiras.get(story.folder)
            spec_result["stories"].append(
                {
                    "folder": story.folder,
                    "jira_item": jira_item,
                    "has_jira": jira_item is not None,
                    "functional_spec_path": str(
                        spec.path / "specs" / story.folder / "functional-spec.md"
                    ),
                }
            )

        results.append(spec_result)

    if as_toon:
        console.print(toons.dumps({"specs": results}))
        return

    item_label = "Sub-task" if item_type == "subtask" else "Story"

    # Rich output
    for spec_data in results:
        console.print(
            f"\n[bold]{spec_data['name']}[/bold] [dim]({item_label} mode)[/dim]"
        )
        console.print(
            f"  Parent Jira (from folder): {spec_data['parent_jira_from_folder'] or '[dim]not found[/dim]'}"
        )
        console.print(
            f"  Parent Jira (from index): {spec_data['parent_jira_from_index'] or '[dim]not set[/dim]'}"
        )

        if spec_data["stories"]:
            table = Table(show_header=True, header_style="bold")
            table.add_column("Story")
            table.add_column("Jira Item")
            table.add_column("Status")

            for story in spec_data["stories"]:
                jira = story["jira_item"] or ""
                status = (
                    "[green]linked[/green]"
                    if story["has_jira"]
                    else "[yellow]not linked[/yellow]"
                )
                table.add_row(story["folder"], jira, status)

            console.print(table)
        else:
            console.print("  [dim]No stories found[/dim]")
