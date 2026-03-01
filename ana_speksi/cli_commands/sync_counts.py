"""The ``sync-counts`` command."""

from __future__ import annotations

import toons
import typer

from ana_speksi.cli_commands._helpers import console
from ana_speksi.status import (
    get_ana_speksi_root,
    list_ongoing_specs,
    update_index_task_counts,
)


def sync_counts_command(
    name: str = typer.Argument(
        None,
        help="Name of the spec to sync (e.g. PROJ-123.add-user-auth).",
    ),
    as_toon: bool = typer.Option(
        False,
        "--toon",
        help="Output as TOON (token-friendly format for AI agents).",
    ),
) -> None:
    """Update task counts in index.md by reading actual tasks.md files."""
    root = get_ana_speksi_root()
    specs = list_ongoing_specs(root)

    if not specs:
        console.print("[yellow]No ongoing specs found.[/yellow]")
        raise typer.Exit(1)

    targets = specs
    if name:
        targets = [s for s in specs if s.name == name or s.name.endswith(f"-{name}")]
        if not targets:
            console.print(f"[red]Spec not found: {name}[/red]")
            raise typer.Exit(1)

    results = []
    for spec in targets:
        updated = update_index_task_counts(spec.path)
        results.append({"spec": spec.name, "updated": updated})

    if as_toon:
        toon_data = []
        for r in results:
            toon_data.append(
                {
                    "spec": r["spec"],
                    "updated": [
                        {"story": s, "total": t, "done": d}
                        for s, t, d in r["updated"]
                    ],
                }
            )
        console.print(toons.dumps({"synced": toon_data}))
    else:
        for r in results:
            console.print(f"\n[bold]{r['spec']}[/bold]")
            if r["updated"]:
                for story, total, done in r["updated"]:
                    console.print(f"  {story}: {done}/{total} tasks complete")
            else:
                console.print("  [dim]No changes needed.[/dim]")
