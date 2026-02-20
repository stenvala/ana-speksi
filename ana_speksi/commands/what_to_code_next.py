"""ana_speksi what-to-code-next -- determine the next task to implement."""

from __future__ import annotations

import re
from pathlib import Path

import toons
import typer
from rich.console import Console

from ana_speksi.status import get_ana_speksi_root, get_spec_status

console = Console()


def what_to_code_next_command(
    name: str = typer.Argument(
        None,
        help="Name of the spec to analyze (e.g., add-user-auth or 001-add-user-auth).",
    ),
    story: str = typer.Option(
        None,
        "--story",
        "-s",
        help="Specific story folder to analyze (e.g., 01-user-authentication). If not provided, analyzes the first story with pending tasks.",
    ),
    as_toon: bool = typer.Option(
        False,
        "--toon",
        help="Output as TOON.",
    ),
) -> None:
    """Determine the next task to implement in a spec during codify phase.

    This command analyzes the tasks.md file and returns information about
    the next incomplete task(s) that need to be implemented.
    """
    root = get_ana_speksi_root()
    ongoing_dir = root / "ongoing"

    if not ongoing_dir.exists():
        console.print("[red]Error: No ongoing specs found.[/red]")
        return

    # Find the spec
    spec_path = None
    if name:
        # Try exact match or partial match
        candidates = [
            d for d in ongoing_dir.iterdir()
            if d.is_dir() and (d.name == name or d.name.endswith(name) or name in d.name)
        ]
        if candidates:
            spec_path = candidates[0]
        else:
            console.print(f"[red]Error: Spec '{name}' not found.[/red]")
            return
    else:
        # List available specs
        specs = [d for d in ongoing_dir.iterdir() if d.is_dir()]
        if not specs:
            console.print("[red]Error: No specs found.[/red]")
            return
        if len(specs) > 1:
            console.print("[yellow]Multiple specs found, please specify one:[/yellow]")
            for s in sorted(specs):
                console.print(f"  {s.name}")
            return
        spec_path = specs[0]

    # Get spec status
    spec_status = get_spec_status(spec_path)

    # Find story to analyze
    story_status = None
    if story:
        story_status = next(
            (s for s in spec_status.stories if s.folder == story or story in s.folder),
            None,
        )
        if not story_status:
            console.print(
                f"[red]Error: Story '{story}' not found in spec.[/red]"
            )
            return
    else:
        # Find first story with pending tasks
        for s in spec_status.stories:
            if s.has_tasks and s.tasks_done < s.tasks_total:
                story_status = s
                break

    if not story_status:
        console.print(
            "[yellow]No pending tasks found in this spec. All tasks are completed![/yellow]"
        )
        return

    # Read tasks.md and extract next incomplete task
    tasks_file = spec_path / "specs" / story_status.folder / "tasks.md"
    if not tasks_file.exists():
        console.print(f"[red]Error: tasks.md not found for story {story_status.folder}[/red]")
        return

    content = tasks_file.read_text(encoding="utf-8")
    next_task_info = extract_next_task(content)

    # List story directory files
    story_dir = spec_path / "specs" / story_status.folder
    story_files = list_story_files(story_dir)

    if as_toon:
        output = {
            "spec_name": spec_status.name,
            "story_folder": story_status.folder,
            "story_name": story_status.name,
            "current_progress": f"{story_status.tasks_done}/{story_status.tasks_total}",
            "next_task": next_task_info,
            "story_files": story_files,
        }
        console.print(toons.dumps(output))
    else:
        console.print(f"\n[bold]Spec:[/bold] {spec_status.name}")
        console.print(f"[bold]Story:[/bold] {story_status.folder}")
        console.print(
            f"[bold]Progress:[/bold] {story_status.tasks_done}/{story_status.tasks_total} tasks complete"
        )
        console.print()

        # Show available files in story directory
        if story_files:
            console.print("[bold]Available story files:[/bold]")
            for file_info in story_files:
                console.print(f"  • {file_info['name']}: {file_info['description']}")
            console.print()

        if next_task_info:
            console.print("[bold]Next Task:[/bold]")
            console.print(next_task_info.get("task_text", ""))
            if next_task_info.get("description"):
                console.print("\n[bold]Details:[/bold]")
                console.print(next_task_info["description"])
            if next_task_info.get("context"):
                console.print("\n[bold]Context:[/bold]")
                console.print(next_task_info["context"])
        else:
            console.print("[yellow]No incomplete tasks found.[/yellow]")

        console.print("\n[bold yellow]Remember:[/bold yellow] After implementing this task, update [bold]tasks.md[/bold] to mark it as complete.")


def list_story_files(story_dir: Path) -> list[dict]:
    """List all files in the story directory with descriptions.

    Returns a list of dicts with 'name' and 'description' for each file.
    """
    file_descriptions = {
        "functional-spec.md": "User story requirements and acceptance criteria",
        "technical-spec.md": "Technical design and implementation strategy",
        "tasks.md": "Implementation tasks checklist (track progress here)",
        "data-model.md": "Data structures and database schema",
        "api-contract.md": "API endpoints, request/response formats",
        "test-automation-plan.md": "Automated testing strategy and test cases",
        "manual-testing-plan.md": "Manual testing procedures and scenarios",
    }

    files = []
    if story_dir.exists():
        for file in sorted(story_dir.iterdir()):
            if file.is_file() and file.suffix == ".md":
                description = file_descriptions.get(
                    file.name,
                    "Story resource file"
                )
                files.append({
                    "name": file.name,
                    "description": description,
                })
    return files


def extract_next_task(content: str) -> dict | None:
    """Extract the next incomplete task from tasks.md content.

    Returns a dict with:
    - task_text: the task title/description
    - description: expanded description if available (under ### Details)
    - context: context/implementation notes if available (under ### Implementation Context)
    """
    lines = content.split("\n")
    current_task = None
    task_details = {}

    for i, line in enumerate(lines):
        # Look for unchecked task boxes
        if re.match(r"^- \[ \]", line):
            # Found the next incomplete task
            task_text = line.replace("- [ ] ", "").strip()
            current_task = {
                "task_text": task_text,
                "description": None,
                "context": None,
            }

            # Look ahead for details and context
            j = i + 1
            current_section = None
            section_content = []

            while j < len(lines):
                next_line = lines[j]

                # Stop at next task
                if re.match(r"^- \[[ x]\]", next_line):
                    break

                # Check for section headers
                if next_line.startswith("### "):
                    # Save previous section if any
                    if current_section and section_content:
                        content_text = "\n".join(section_content).strip()
                        if current_section == "Details":
                            current_task["description"] = content_text
                        elif current_section == "Context" or current_section == "Implementation Context":
                            current_task["context"] = content_text

                    # Start new section
                    current_section = next_line.replace("### ", "").strip()
                    section_content = []
                elif current_section and next_line.strip():
                    section_content.append(next_line)

                j += 1

            # Save last section
            if current_section and section_content:
                content_text = "\n".join(section_content).strip()
                if current_section == "Details":
                    current_task["description"] = content_text
                elif current_section == "Context" or current_section == "Implementation Context":
                    current_task["context"] = content_text

            return current_task

    return None
