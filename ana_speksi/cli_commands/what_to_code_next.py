"""The ``what-to-code-next`` command."""

from __future__ import annotations

import toons
import typer

from ana_speksi.cli_commands._helpers import console
from ana_speksi.status import (
    extract_next_task,
    get_ana_speksi_root,
    get_spec_status,
    list_story_files,
)


def what_to_code_next_command(
    name: str = typer.Argument(
        None,
        help="Name of the spec to analyze (e.g., add-user-auth or 001-add-user-auth).",
    ),
    story: str = typer.Option(
        None,
        "--story",
        "-s",
        help="Specific story folder to analyze.",
    ),
    as_toon: bool = typer.Option(False, "--toon", help="Output as TOON."),
) -> None:
    """Determine the next task to implement in a spec during codify phase."""
    root = get_ana_speksi_root()
    ongoing_dir = root / "ongoing"

    if not ongoing_dir.exists():
        console.print("[red]Error: No ongoing specs found.[/red]")
        return

    spec_path = None
    if name:
        candidates = [
            d
            for d in ongoing_dir.iterdir()
            if d.is_dir()
            and (d.name == name or d.name.endswith(name) or name in d.name)
        ]
        if candidates:
            spec_path = candidates[0]
        else:
            console.print(f"[red]Error: Spec '{name}' not found.[/red]")
            return
    else:
        specs_list = [d for d in ongoing_dir.iterdir() if d.is_dir()]
        if not specs_list:
            console.print("[red]Error: No specs found.[/red]")
            return
        if len(specs_list) > 1:
            console.print("[yellow]Multiple specs found, please specify one:[/yellow]")
            for s in sorted(specs_list):
                console.print(f"  {s.name}")
            return
        spec_path = specs_list[0]

    spec_status = get_spec_status(spec_path)

    story_status = None
    if story:
        story_status = next(
            (
                s
                for s in spec_status.stories
                if s.folder == story or story in s.folder
            ),
            None,
        )
        if not story_status:
            console.print(f"[red]Error: Story '{story}' not found in spec.[/red]")
            return
    else:
        for s in spec_status.stories:
            if s.has_tasks and s.tasks_done < s.tasks_total:
                story_status = s
                break

    if not story_status:
        console.print(
            "[yellow]No pending tasks found in this spec. All tasks are completed![/yellow]"
        )
        return

    tasks_file = spec_path / "specs" / story_status.folder / "tasks.md"
    if not tasks_file.exists():
        console.print(
            f"[red]Error: tasks.md not found for story {story_status.folder}[/red]"
        )
        return

    content = tasks_file.read_text(encoding="utf-8")
    next_task_info = extract_next_task(content)

    story_dir = spec_path / "specs" / story_status.folder
    story_files_info = list_story_files(story_dir)

    if as_toon:
        output = {
            "spec_name": spec_status.name,
            "story_folder": story_status.folder,
            "story_name": story_status.name,
            "current_progress": f"{story_status.tasks_done}/{story_status.tasks_total}",
            "next_task": next_task_info,
            "story_files": story_files_info,
        }
        console.print(toons.dumps(output))
    else:
        console.print(f"\n[bold]Spec:[/bold] {spec_status.name}")
        console.print(f"[bold]Story:[/bold] {story_status.folder}")
        console.print(
            f"[bold]Progress:[/bold] {story_status.tasks_done}/{story_status.tasks_total} tasks complete"
        )
        console.print()

        if story_files_info:
            console.print("[bold]Available story files:[/bold]")
            for file_info in story_files_info:
                console.print(
                    f"  - {file_info['name']}: {file_info['description']}"
                )
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

        console.print(
            "\n[bold yellow]Remember:[/bold yellow] After implementing this task, "
            "update [bold]tasks.md[/bold] to mark it as complete."
        )
