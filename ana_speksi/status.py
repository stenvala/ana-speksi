"""Status detection and spec scanning logic."""

from __future__ import annotations

import re
from pathlib import Path

from rich.console import Console
from rich.table import Table

from ana_speksi.models import (
    ARCHIVE_DIR,
    ANA_SPEKSI_DIR,
    ONGOING_DIR,
    TECHNICAL_DEBT_DIR,
    TRUTH_DIR,
    DocStatus,
    Phase,
    SpecStatus,
    StoryStatus,
)

console = Console()


def get_ana_speksi_root(cwd: Path | None = None) -> Path:
    """Return the ana_speksi root directory, searching upward from cwd."""
    start = cwd or Path.cwd()
    current = start
    while current != current.parent:
        candidate = current / ANA_SPEKSI_DIR
        if candidate.is_dir():
            return candidate
        current = current.parent
    return start / ANA_SPEKSI_DIR


def ensure_dirs(root: Path) -> None:
    """Ensure all required subdirectories exist."""
    from ana_speksi.models import TRUTH_DATA_MODELS_DIR, TRUTH_ENUMS_DIR

    dirs: list[Path] = []
    for sub in [ONGOING_DIR, TRUTH_DIR, ARCHIVE_DIR, TECHNICAL_DEBT_DIR]:
        d = root / sub
        d.mkdir(parents=True, exist_ok=True)
        dirs.append(d)
    # Truth subdirectories
    for truth_sub in [TRUTH_DATA_MODELS_DIR, TRUTH_ENUMS_DIR]:
        d = root / TRUTH_DIR / truth_sub
        d.mkdir(parents=True, exist_ok=True)
        dirs.append(d)
    # Create .gitkeep in each directory so they are tracked by git
    for d in dirs:
        gitkeep = d / ".gitkeep"
        if not gitkeep.exists():
            gitkeep.touch()


def detect_phase(spec_path: Path) -> Phase:
    """Detect the current phase of a spec by examining its contents."""
    proposal = spec_path / "proposal.md"
    index = spec_path / "index.md"
    research = spec_path / "research.md"
    specs_dir = spec_path / "specs"

    if not proposal.exists():
        return Phase.PROPOSAL

    # Proposal must be accepted before storify can proceed
    proposal_status = read_doc_status(proposal)
    if proposal_status != DocStatus.ACCEPTED:
        return Phase.PROPOSAL

    if not index.exists():
        return Phase.STORIFY

    # Check if functional specs exist
    stories = list_stories(spec_path)
    if not stories:
        return Phase.STORIFY

    all_functional_accepted = all(
        s.functional_spec_status == DocStatus.ACCEPTED for s in stories
    )
    if not all_functional_accepted:
        return Phase.STORIFY

    # Check research
    if not research.exists():
        return Phase.RESEARCH

    # Check technical specs
    all_technical_accepted = all(
        s.technical_spec_status == DocStatus.ACCEPTED for s in stories
    )
    if not all_technical_accepted:
        return Phase.TECHIFY

    # Check tasks
    all_tasks_accepted = all(s.tasks_status == DocStatus.ACCEPTED for s in stories)
    if not all_tasks_accepted:
        return Phase.TASKIFY

    # Check if all tasks are done
    all_tasks_done = all(
        s.tasks_done >= s.tasks_total and s.tasks_total > 0 for s in stories
    )
    if not all_tasks_done:
        return Phase.CODIFY

    return Phase.DOCUFY


def read_doc_status(file_path: Path) -> DocStatus:
    """Read the **Status**: value from a markdown file's header."""
    if not file_path.exists():
        return DocStatus.EMPTY
    content = file_path.read_text(encoding="utf-8")
    match = re.search(r"\*\*Status\*\*:\s*(\S+)", content)
    if not match:
        return DocStatus.DRAFT
    value = match.group(1)
    if value == "Accepted":
        return DocStatus.ACCEPTED
    return DocStatus.DRAFT


def list_stories(spec_path: Path) -> list[StoryStatus]:
    """List all stories in a spec directory."""
    specs_dir = spec_path / "specs"
    if not specs_dir.exists():
        return []

    stories = []
    for child in sorted(specs_dir.iterdir()):
        if not child.is_dir():
            continue
        story = StoryStatus(folder=child.name, name=child.name)
        story.has_functional_spec = (child / "functional-spec.md").exists()
        story.has_technical_spec = (child / "technical-spec.md").exists()
        story.has_data_model = (child / "data-model.md").exists()
        story.has_api_contract = (child / "api-contract.md").exists()
        story.has_test_plan = (child / "test-automation-plan.md").exists()
        story.has_manual_test_plan = (child / "manual-testing-plan.md").exists()
        story.has_tasks = (child / "tasks.md").exists()
        if story.has_tasks:
            story.tasks_total, story.tasks_done = count_tasks(child / "tasks.md")
        story.functional_spec_status = read_doc_status(child / "functional-spec.md")
        story.technical_spec_status = read_doc_status(child / "technical-spec.md")
        story.tasks_status = read_doc_status(child / "tasks.md")
        stories.append(story)
    return stories


def count_tasks(tasks_path: Path) -> tuple[int, int]:
    """Count total and completed tasks in a tasks.md file."""
    if not tasks_path.exists():
        return 0, 0
    content = tasks_path.read_text(encoding="utf-8")
    total = len(re.findall(r"- \[[ x]\]", content))
    done = len(re.findall(r"- \[x\]", content))
    return total, done


def get_spec_status(spec_path: Path) -> SpecStatus:
    """Get full status of a spec."""
    phase = detect_phase(spec_path)
    stories = list_stories(spec_path)
    return SpecStatus(
        name=spec_path.name,
        path=spec_path,
        phase=phase,
        has_proposal=(spec_path / "proposal.md").exists(),
        has_index=(spec_path / "index.md").exists(),
        has_research=(spec_path / "research.md").exists(),
        proposal_status=read_doc_status(spec_path / "proposal.md"),
        stories=stories,
    )


def list_ongoing_specs(root: Path) -> list[SpecStatus]:
    """List all ongoing specs with their status."""
    ongoing = root / ONGOING_DIR
    if not ongoing.exists():
        return []
    results = []
    for child in sorted(ongoing.iterdir()):
        if child.is_dir():
            results.append(get_spec_status(child))
    return results


def print_status(root: Path) -> None:
    """Print a rich status table of all ongoing specs."""
    specs = list_ongoing_specs(root)
    if not specs:
        console.print("[dim]No ongoing specs found.[/dim]")
        return

    for spec in specs:
        console.print(f"\n[bold]{spec.name}[/bold]")
        console.print(f"  Phase: [cyan]{spec.phase.value}[/cyan]")
        console.print(f"  Proposal: {'yes' if spec.has_proposal else 'no'}")
        console.print(f"  Index: {'yes' if spec.has_index else 'no'}")
        console.print(f"  Research: {'yes' if spec.has_research else 'no'}")

        if spec.stories:
            table = Table(show_header=True, header_style="bold")
            table.add_column("Story")
            table.add_column("Functional")
            table.add_column("Technical")
            table.add_column("Tasks")
            table.add_column("Progress")

            for story in spec.stories:
                func = "yes" if story.has_functional_spec else "no"
                tech = "yes" if story.has_technical_spec else "no"
                tasks = "yes" if story.has_tasks else "no"
                progress = (
                    f"{story.tasks_done}/{story.tasks_total}"
                    if story.has_tasks
                    else "-"
                )
                table.add_row(story.folder, func, tech, tasks, progress)

            console.print(table)


def print_status_json(root: Path) -> dict:
    """Return status as a dict (for TOON output consumed by AI agents)."""
    specs = list_ongoing_specs(root)
    result = []
    for spec in specs:
        stories_data = []
        for s in spec.stories:
            stories_data.append(
                {
                    "folder": s.folder,
                    "name": s.name,
                    "has_functional_spec": s.has_functional_spec,
                    "has_technical_spec": s.has_technical_spec,
                    "has_data_model": s.has_data_model,
                    "has_api_contract": s.has_api_contract,
                    "has_test_plan": s.has_test_plan,
                    "has_manual_test_plan": s.has_manual_test_plan,
                    "has_tasks": s.has_tasks,
                    "tasks_total": s.tasks_total,
                    "tasks_done": s.tasks_done,
                    "functional_spec_status": s.functional_spec_status.value,
                    "technical_spec_status": s.technical_spec_status.value,
                    "tasks_status": s.tasks_status.value,
                }
            )
        result.append(
            {
                "name": spec.name,
                "path": str(spec.path),
                "phase": spec.phase.value,
                "has_proposal": spec.has_proposal,
                "has_index": spec.has_index,
                "has_research": spec.has_research,
                "proposal_status": spec.proposal_status.value,
                "stories": stories_data,
            }
        )
    return {"ongoing": result}
