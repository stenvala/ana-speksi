"""bas_spec jira-update-story -- update Jira story/subtask descriptions from functional specs."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.prompt import Confirm

import toons
import zaira
from bas_spec.status import get_bas_spec_root, list_ongoing_specs
from bas_spec.commands.jira_stories import (
    _extract_story_jira_items,
)
from bas_spec.commands.jira_create_story import (
    _read_functional_spec_description,
    _convert_markdown_to_jira,
)

console = Console()


def _update_jira_description(jira_client, jira_item: str, description: str) -> bool:
    """Update the description of a Jira issue."""
    jira_description = _convert_markdown_to_jira(description)

    try:
        issue = jira_client.issue(jira_item)
        issue.update(fields={"description": jira_description})
        return True
    except Exception as e:
        console.print(f"[red]Failed to update {jira_item}: {e}[/red]")
        return False


def jira_update_story_command(
    spec_name: str = typer.Argument(
        ...,
        help="Spec name (e.g., APG-593.budgeting).",
    ),
    story_folder: str = typer.Argument(
        None,
        help="Specific story folder to update (optional, processes all linked stories).",
    ),
    as_toon: bool = typer.Option(
        False,
        "--toon",
        help="Output in TOON format for AI agents.",
    ),
    yes: bool = typer.Option(
        False,
        "--yes", "-y",
        help="Skip confirmation prompts and update all.",
    ),
    item_type: str = typer.Option(
        "story",
        "--item-type", "-t",
        help="Type of Jira item being updated: 'story' or 'subtask'.",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Show what would be updated without actually updating.",
    ),
) -> None:
    """Update Jira story/subtask descriptions from functional specs.

    For each story with a linked Jira item, prompts whether to update
    the Jira description with the content from functional-spec.md.
    Use --item-type subtask when working with Sub-task items.
    """
    root = get_bas_spec_root()
    specs = list_ongoing_specs(root)

    spec = next((s for s in specs if s.name == spec_name), None)
    if not spec:
        console.print(f"[red]Spec not found: {spec_name}[/red]")
        raise typer.Exit(1)

    index_path = spec.path / "index.md"

    # Get existing story Jira mappings
    story_jiras = _extract_story_jira_items(index_path)

    # Determine which stories to process
    stories_to_update = []
    for story in spec.stories:
        if story_folder and story.folder != story_folder:
            continue
        jira_item = story_jiras.get(story.folder)
        if jira_item:
            stories_to_update.append((story, jira_item))

    if not stories_to_update:
        item_label = "subtasks" if item_type == "subtask" else "stories"
        console.print(f"[yellow]No {item_label} with Jira items found to update.[/yellow]")
        return

    # Initialize Jira client
    jira_client = zaira.client()

    results = []

    for story, jira_item in stories_to_update:
        # Read description from functional spec
        description = _read_functional_spec_description(spec.path, story.folder)
        if not description:
            console.print(f"[yellow]No functional spec content for {story.folder}, skipping.[/yellow]")
            results.append({
                "story_folder": story.folder,
                "jira_item": jira_item,
                "action": "skipped",
                "reason": "no_functional_spec",
            })
            continue

        console.print(f"\n[bold]{story.folder}[/bold] -> {jira_item}")
        console.print(f"  Functional spec: {len(description)} characters")

        if dry_run:
            console.print(f"  [cyan]Would update {jira_item} description[/cyan]")
            results.append({
                "story_folder": story.folder,
                "jira_item": jira_item,
                "action": "would_update",
            })
            continue

        # Prompt for confirmation unless --yes flag
        if not yes and not as_toon:
            should_update = Confirm.ask(
                f"  Update {jira_item} description with functional-spec content?",
                default=False
            )
            if not should_update:
                console.print(f"  [dim]Skipped[/dim]")
                results.append({
                    "story_folder": story.folder,
                    "jira_item": jira_item,
                    "action": "skipped",
                    "reason": "user_declined",
                })
                continue

        # Update the Jira issue
        if _update_jira_description(jira_client, jira_item, description):
            console.print(f"  [green]Updated {jira_item}[/green]")
            results.append({
                "story_folder": story.folder,
                "jira_item": jira_item,
                "action": "updated",
            })
        else:
            results.append({
                "story_folder": story.folder,
                "jira_item": jira_item,
                "action": "failed",
            })

    if as_toon:
        console.print(toons.dumps({"results": results}))
