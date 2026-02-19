"""bas_spec jira-create-story -- create Jira stories or subtasks for specs."""

from __future__ import annotations

import re
from pathlib import Path

import typer
from rich.console import Console

import toons
import zaira
from bas_spec.status import get_bas_spec_root, list_ongoing_specs
from bas_spec.commands.jira_stories import (
    _extract_jira_item_from_index,
    _extract_story_jira_items,
)

console = Console()


def _convert_markdown_to_jira(markdown: str) -> str:
    """Convert markdown to Jira wiki markup.

    Basic conversions:
    - # Header -> h1. Header
    - ## Header -> h2. Header
    - **bold** -> *bold*
    - *italic* -> _italic_
    - - bullet -> * bullet
    - 1. numbered -> # numbered
    - [text](url) -> [text|url]
    - ```code``` -> {code}code{code}
    """
    text = markdown

    # Headers
    text = re.sub(r"^######\s+(.+)$", r"h6. \1", text, flags=re.MULTILINE)
    text = re.sub(r"^#####\s+(.+)$", r"h5. \1", text, flags=re.MULTILINE)
    text = re.sub(r"^####\s+(.+)$", r"h4. \1", text, flags=re.MULTILINE)
    text = re.sub(r"^###\s+(.+)$", r"h3. \1", text, flags=re.MULTILINE)
    text = re.sub(r"^##\s+(.+)$", r"h2. \1", text, flags=re.MULTILINE)
    text = re.sub(r"^#\s+(.+)$", r"h1. \1", text, flags=re.MULTILINE)

    # Code blocks (must be before inline processing)
    text = re.sub(r"```(\w*)\n(.*?)```", r"{code:\1}\n\2{code}", text, flags=re.DOTALL)
    text = re.sub(r"`([^`]+)`", r"{{\\1}}", text)

    # Bold and italic (be careful with order)
    text = re.sub(r"\*\*([^*]+)\*\*", r"*\1*", text)
    text = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"_\1_", text)

    # Links
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"[\1|\2]", text)

    # Bullet lists (- item -> * item)
    text = re.sub(r"^(\s*)-\s+", r"\1* ", text, flags=re.MULTILINE)

    # Numbered lists (1. item -> # item)
    text = re.sub(r"^(\s*)\d+\.\s+", r"\1# ", text, flags=re.MULTILINE)

    return text


def _get_parent_jira_fields(jira_client, jira_item: str) -> dict | None:
    """Fetch mandatory fields from parent Jira item using zaira."""
    try:
        issue = jira_client.issue(jira_item)
        f = issue.fields

        fields = {}
        if f.project:
            fields["project"] = f.project.key
        if f.components:
            fields["components"] = [c.name for c in f.components]
        if f.fixVersions:
            fields["fixVersions"] = [v.name for v in f.fixVersions]
        if f.labels:
            fields["labels"] = list(f.labels)
        return fields
    except Exception as e:
        console.print(f"[yellow]Warning: Could not fetch parent fields: {e}[/yellow]")
        return None


def _read_functional_spec_description(spec_path: Path, story_folder: str) -> str | None:
    """Read and extract description from functional-spec.md."""
    func_spec = spec_path / "specs" / story_folder / "functional-spec.md"
    if not func_spec.exists():
        return None

    content = func_spec.read_text(encoding="utf-8")

    # Remove YAML front matter if present
    if content.startswith("---"):
        end = content.find("---", 3)
        if end > 0:
            content = content[end + 3 :].strip()

    # Remove the title line
    lines = content.split("\n")
    if lines and lines[0].startswith("#"):
        lines = lines[1:]

    # Remove metadata lines at the start (like **Parent**, **Created**, etc.)
    filtered_lines = []
    in_metadata = True
    for line in lines:
        if in_metadata and (line.startswith("**") or line.strip() == ""):
            continue
        in_metadata = False
        filtered_lines.append(line)

    return "\n".join(filtered_lines).strip()


def _create_jira_story(
    jira_client,
    parent_jira: str,
    story_name: str,
    description: str,
    parent_fields: dict | None,
    project_override: str | None = None,
    item_type: str = "story",
) -> str | None:
    """Create a Jira story or subtask with parent set to the parent item."""
    if project_override:
        project = project_override
    elif parent_fields and parent_fields.get("project"):
        project = parent_fields["project"]
    else:
        project = parent_jira.split("-")[0]

    # Convert markdown to Jira wiki markup
    jira_description = _convert_markdown_to_jira(description)

    # Determine issue type name based on item_type
    issue_type_name = "Sub-task" if item_type == "subtask" else "Story"

    # Build fields for issue creation
    fields = {
        "project": {"key": project},
        "issuetype": {"name": issue_type_name},
        "summary": story_name,
        "description": jira_description,
        "parent": {"key": parent_jira},
    }

    try:
        issue = jira_client.create_issue(fields=fields)
        new_key = issue.key

        # Copy mandatory fields from parent if available
        if parent_fields:
            update_fields = {}
            if parent_fields.get("components"):
                update_fields["components"] = [
                    {"name": c} for c in parent_fields["components"]
                ]
            if parent_fields.get("fixVersions"):
                update_fields["fixVersions"] = [
                    {"name": v} for v in parent_fields["fixVersions"]
                ]
            if parent_fields.get("labels"):
                update_fields["labels"] = parent_fields["labels"]

            if update_fields:
                try:
                    jira_client.issue(new_key).update(fields=update_fields)
                except Exception as e:
                    console.print(
                        f"[yellow]Warning: Could not copy fields to {new_key}: {e}[/yellow]"
                    )

        return new_key
    except Exception as e:
        console.print(f"[red]Failed to create Jira story: {e}[/red]")
        return None


def _update_index_with_jira_item(
    index_path: Path, story_folder: str, jira_item: str
) -> bool:
    """Update index.md to add Jira item to a story section."""
    if not index_path.exists():
        return False

    content = index_path.read_text(encoding="utf-8")

    # Find the story section and add Jira item after it
    # Pattern: #### story-folder\n\n**Implementation**: ...
    # We want to add **Jira Item**: VALUE after the #### line

    pattern = re.compile(rf"(####\s+{re.escape(story_folder)}\s*\n)\n", re.MULTILINE)

    def replacement(match):
        return f"{match.group(1)}\n**Jira Item**: {jira_item}\n"

    new_content, count = pattern.subn(replacement, content)

    if count > 0:
        index_path.write_text(new_content, encoding="utf-8")
        return True
    return False


def jira_create_story_command(
    spec_name: str = typer.Argument(
        ...,
        help="Spec name (e.g., APG-593.budgeting).",
    ),
    story_folder: str = typer.Argument(
        None,
        help="Specific story folder to create Jira for (optional, creates for all unlinked).",
    ),
    as_toon: bool = typer.Option(
        False,
        "--toon",
        help="Output in TOON format for AI agents.",
    ),
    project: str = typer.Option(
        None,
        "--project",
        "-p",
        help="Override the Jira project key (default: derived from parent item).",
    ),
    item_type: str = typer.Option(
        "story",
        "--item-type",
        "-t",
        help="Type of Jira item to create: 'story' (parent=epic) or 'subtask' (parent=story).",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Show what would be created without actually creating.",
    ),
) -> None:
    """Create Jira stories or subtasks for specs that don't have them linked.

    Creates Story or Sub-task type items in Jira, sets parent to the
    epic (for stories) or story (for subtasks), and updates index.md
    with the Jira item reference.

    Use --item-type subtask when the parent is a Story and you want
    to create Sub-task items.
    """
    root = get_bas_spec_root()
    specs = list_ongoing_specs(root)

    spec = next((s for s in specs if s.name == spec_name), None)
    if not spec:
        console.print(f"[red]Spec not found: {spec_name}[/red]")
        raise typer.Exit(1)

    index_path = spec.path / "index.md"

    # Get parent Jira from folder name
    parent_jira = None
    if "." in spec.name:
        parent_jira = spec.name.split(".")[0]

    if not parent_jira:
        console.print("[red]Cannot determine parent Jira item from spec name.[/red]")
        raise typer.Exit(1)

    # Get existing story Jira mappings
    story_jiras = _extract_story_jira_items(index_path)

    # Determine which stories need Jira items
    stories_to_create = []
    for story in spec.stories:
        if story_folder and story.folder != story_folder:
            continue
        if story_jiras.get(story.folder) is None:
            stories_to_create.append(story)

    if not stories_to_create:
        console.print("[green]All stories already have Jira items linked.[/green]")
        return

    # Initialize Jira client
    jira_client = zaira.client()

    # Fetch parent fields for copying mandatory fields
    item_label = "subtask" if item_type == "subtask" else "story"
    console.print(f"[cyan]Fetching fields from parent {parent_jira}...[/cyan]")
    parent_fields = _get_parent_jira_fields(jira_client, parent_jira)

    results = []

    for story in stories_to_create:
        # Extract human-readable name from folder (remove NN- prefix)
        story_name = re.sub(r"^\d+-", "", story.folder).replace("-", " ").title()

        # Read description from functional spec
        description = _read_functional_spec_description(spec.path, story.folder)
        if not description:
            console.print(
                f"[yellow]Warning: No functional spec found for {story.folder}[/yellow]"
            )
            description = f"Story: {story_name}"

        if dry_run:
            console.print(
                f"\n[cyan]Would create Jira {item_label} for: {story.folder}[/cyan]"
            )
            console.print(f"  Parent: {parent_jira}")
            console.print(f"  Summary: {story_name}")
            console.print(f"  Description length: {len(description)} chars")
            results.append(
                {
                    "story_folder": story.folder,
                    "action": "would_create",
                    "item_type": item_type,
                    "parent": parent_jira,
                    "summary": story_name,
                }
            )
            continue

        console.print(f"\n[cyan]Creating Jira {item_label} for: {story.folder}[/cyan]")
        new_jira = _create_jira_story(
            jira_client,
            parent_jira,
            story_name,
            description,
            parent_fields,
            project,
            item_type,
        )

        if new_jira:
            console.print(f"[green]Created: {new_jira}[/green]")

            # Update index.md
            if _update_index_with_jira_item(index_path, story.folder, new_jira):
                console.print(f"[green]Updated index.md with {new_jira}[/green]")
            else:
                console.print(
                    f"[yellow]Warning: Could not update index.md for {story.folder}[/yellow]"
                )

            results.append(
                {
                    "story_folder": story.folder,
                    "action": "created",
                    "jira_item": new_jira,
                    "parent": parent_jira,
                }
            )
        else:
            results.append(
                {
                    "story_folder": story.folder,
                    "action": "failed",
                    "parent": parent_jira,
                }
            )

    if as_toon:
        console.print(toons.dumps({"results": results}))
