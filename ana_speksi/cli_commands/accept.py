"""The ``accept`` command."""

from __future__ import annotations

import toons
import typer

from ana_speksi.acceptance import (
    get_acceptance_status,
    update_file_status,
    update_index_entry,
)
from ana_speksi.cli_commands._helpers import console, find_spec
from ana_speksi.status import (
    get_ana_speksi_root,
    list_ongoing_specs,
    update_index_task_counts,
)


def accept_command(
    name: str = typer.Argument(
        None,
        help="Name of the spec to accept (e.g. PROJ-123.add-user-auth).",
    ),
    as_toon: bool = typer.Option(
        False,
        "--toon",
        help="Output as TOON (token-friendly format for AI agents).",
    ),
) -> None:
    """Mark the current phase's outputs as Accepted."""
    root = get_ana_speksi_root()
    specs = list_ongoing_specs(root)

    if not specs:
        console.print("[yellow]No ongoing specs found.[/yellow]")
        raise typer.Exit(1)

    spec = find_spec(specs, name)
    acceptance = get_acceptance_status(spec)
    files_to_accept = acceptance["files_to_accept"]
    already_accepted = acceptance["already_accepted"]

    if acceptance["acceptance_target"] is None:
        console.print(
            f"[yellow]No acceptance action available for phase: {spec.phase.value}[/yellow]"
        )
        raise typer.Exit(1)

    if as_toon:
        console.print(toons.dumps(acceptance))
        return

    console.print(f"\n[bold]Spec: {spec.name}[/bold]")
    console.print(f"Phase: [cyan]{spec.phase.value}[/cyan]")
    console.print(f"Action: {acceptance['description']}")

    if already_accepted:
        console.print(f"\nAlready accepted ({len(already_accepted)}):")
        for f in already_accepted:
            console.print(f"  [green]{f}[/green]")

    if files_to_accept:
        console.print(f"\nAccepting {len(files_to_accept)} file(s):")
        index_path = spec.path / "index.md"
        for f in files_to_accept:
            updated = update_file_status(f)
            update_index_entry(index_path, f, spec.path)
            status = (
                "[green]done[/green]"
                if updated
                else "[yellow]no Draft status found[/yellow]"
            )
            console.print(f"  {f} -- {status}")
        count_updates = update_index_task_counts(spec.path)
        if count_updates:
            console.print("\nSynced task counts:")
            for story, total, done in count_updates:
                console.print(f"  {story}: {done}/{total}")
        console.print("\n[green]Acceptance complete.[/green]")
    else:
        console.print("\n[green]All relevant files are already accepted.[/green]")
