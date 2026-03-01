"""CLI entry point for ana_speksi.

Commands are defined in ``ana_speksi.cli_commands``.  This module only
creates the Typer app and wires them together.
"""

from __future__ import annotations

import typer

from ana_speksi.cli_commands.accept import accept_command
from ana_speksi.cli_commands.continue_cmd import continue_command
from ana_speksi.cli_commands.init import init_command
from ana_speksi.cli_commands.status import status_command
from ana_speksi.cli_commands.sync_counts import sync_counts_command
from ana_speksi.cli_commands.truth import truth_app
from ana_speksi.cli_commands.update import update_command
from ana_speksi.cli_commands.what_to_code_next import what_to_code_next_command

app = typer.Typer(
    name="ana_speksi",
    help="Skill-driven spec development framework.",
    no_args_is_help=True,
)

# Infrastructure
app.command("init")(init_command)
app.command("update")(update_command)

# Utility
app.command("status")(status_command)
app.command("accept")(accept_command)
app.command("continue")(continue_command)
app.command("sync-counts")(sync_counts_command)
app.command("what-to-code-next")(what_to_code_next_command)

# Sub-apps
app.add_typer(truth_app, name="truth")


if __name__ == "__main__":
    app()
