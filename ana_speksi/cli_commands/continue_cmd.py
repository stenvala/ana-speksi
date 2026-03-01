"""The ``continue`` command."""

from __future__ import annotations

import toons
import typer

from ana_speksi.cli_commands._helpers import console, find_spec
from ana_speksi.acceptance import get_acceptance_status
from ana_speksi.models import PHASE_DESCRIPTIONS
from ana_speksi.skill_generator import phase_to_skill
from ana_speksi.status import (
    get_ana_speksi_root,
    list_ongoing_specs,
    print_status_json,
    stories_needing_work,
)


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

    spec = find_spec(specs, name)
    needing_work = stories_needing_work(spec)
    acceptance = get_acceptance_status(spec)

    if as_toon:
        data = print_status_json(root)
        for s in data["ongoing"]:
            if s["name"] == spec.name:
                s["next_phase"] = spec.phase.value
                s["next_phase_description"] = PHASE_DESCRIPTIONS.get(spec.phase, "")
                s["next_skill"] = phase_to_skill(spec.phase)
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
        f"\nInvoke skill: [bold cyan]{phase_to_skill(spec.phase)}[/bold cyan]"
    )
    console.print(
        f"\nThe AI agent should now execute the {phase_to_skill(spec.phase)} skill."
    )
    console.print("Read the skill instructions for detailed steps.")
