"""ana_speksi as-continue -- advance a spec to the next phase."""

from __future__ import annotations

import toons

import typer
from rich.console import Console

from ana_speksi.models import Phase, PHASE_DESCRIPTIONS, SpecStatus
from ana_speksi.commands.accept import get_acceptance_status
from ana_speksi.status import (
    get_ana_speksi_root,
    list_ongoing_specs,
    get_spec_status,
    print_status,
    print_status_json,
)

console = Console()


def continue_command(
    name: str = typer.Argument(
        None,
        help="Name of the spec to continue (e.g. 001-add-user-auth).",
    ),
    as_toon: bool = typer.Option(
        False,
        "--toon",
        help="Output status as TOON (token-friendly format for AI agents).",
    ),
) -> None:
    """Continue working on a spec by advancing to the next phase."""
    root = get_ana_speksi_root()
    specs = list_ongoing_specs(root)

    if not specs:
        console.print("[yellow]No ongoing specs found. Run as-new first.[/yellow]")
        raise typer.Exit(1)

    # Find the requested spec
    spec = None
    if name:
        for s in specs:
            if s.name == name or s.name.endswith(f"-{name}"):
                spec = s
                break
        if not spec:
            console.print(f"[red]Spec not found: {name}[/red]")
            console.print("Available specs:")
            for s in specs:
                console.print(f"  - {s.name} (phase: {s.phase.value})")
            raise typer.Exit(1)
    else:
        if len(specs) == 1:
            spec = specs[0]
        else:
            console.print("Multiple ongoing specs found. Specify which one:")
            for s in specs:
                console.print(f"  - {s.name} (phase: {s.phase.value})")
            raise typer.Exit(1)

    needing_work = _stories_needing_work(spec)
    acceptance = get_acceptance_status(spec)

    if as_toon:
        data = print_status_json(root)
        # Add next phase info and acceptance gate status
        for s in data["ongoing"]:
            if s["name"] == spec.name:
                s["next_phase"] = spec.phase.value
                s["next_phase_description"] = PHASE_DESCRIPTIONS.get(spec.phase, "")
                s["next_skill"] = _phase_to_skill(spec.phase)
                s["total_story_count"] = len(spec.stories)
                s["stories_needing_work"] = needing_work
                s["acceptance_gate"] = {
                    "satisfied": len(acceptance["files_to_accept"]) == 0,
                    "files_to_accept": acceptance["files_to_accept"],
                    "already_accepted": acceptance["already_accepted"],
                }
                break
        console.print(toons.dumps(data))
        return

    # Check acceptance gate for non-TOON output
    if acceptance["files_to_accept"]:
        console.print(f"\n[bold]Spec: {spec.name}[/bold]")
        console.print(f"Current phase: [cyan]{spec.phase.value}[/cyan]")
        console.print(
            "\n[red]Acceptance gate not satisfied.[/red] "
            "The following files need acceptance:"
        )
        for f in acceptance["files_to_accept"]:
            console.print(f"  - {f}")
        console.print("\nRun [bold cyan]as-accept[/bold cyan] to accept them first.")
        return

    console.print(f"\n[bold]Spec: {spec.name}[/bold]")
    console.print(f"Current phase: [cyan]{spec.phase.value}[/cyan]")
    console.print(f"Description: {PHASE_DESCRIPTIONS.get(spec.phase, '')}")
    if needing_work:
        console.print(
            f"\nStories needing work: {len(needing_work)} of {len(spec.stories)}"
        )
        for story in needing_work:
            console.print(f"  - {story['folder']}")
    console.print(
        f"\nInvoke skill: [bold cyan]{_phase_to_skill(spec.phase)}[/bold cyan]"
    )
    console.print(
        f"\nThe AI agent should now execute the {_phase_to_skill(spec.phase)} skill."
    )
    console.print("Read the skill instructions for detailed steps.")


def _stories_needing_work(spec: SpecStatus) -> list[dict]:
    """Return stories that need work in the current phase."""
    if spec.phase in (Phase.PROPOSAL, Phase.STORIFY):
        return []

    result = []
    for s in spec.stories:
        needs_work = False
        if spec.phase in (Phase.RESEARCH, Phase.TECHIFY):
            needs_work = not s.has_technical_spec
        elif spec.phase == Phase.TASKIFY:
            needs_work = not s.has_tasks
        elif spec.phase == Phase.CODIFY:
            needs_work = s.tasks_done < s.tasks_total or s.tasks_total == 0
        elif spec.phase == Phase.DOCUFY:
            needs_work = True

        if needs_work:
            result.append({"folder": s.folder, "name": s.name})

    return result


def _phase_to_skill(phase: Phase) -> str:
    """Map a phase to the skill name that executes it."""
    mapping = {
        Phase.PROPOSAL: "as-new",
        Phase.STORIFY: "as-storify",
        Phase.RESEARCH: "as-techify",
        Phase.TECHIFY: "as-techify",
        Phase.TASKIFY: "as-taskify",
        Phase.CODIFY: "as-codify",
        Phase.DOCUFY: "as-docufy",
    }
    return mapping.get(phase, "as-continue")
