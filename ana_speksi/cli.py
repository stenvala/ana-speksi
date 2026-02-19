"""CLI entry point for ana-speksi."""

import typer

from ana_speksi.commands.accept import accept_command
from ana_speksi.commands.init import init_command
from ana_speksi.commands.new import new_command
from ana_speksi.commands.continue_cmd import continue_command
from ana_speksi.commands.codify import codify_command
from ana_speksi.commands.docufy import docufy_command
from ana_speksi.commands.one_shot import one_shot_command
from ana_speksi.commands.status import status_command
from ana_speksi.commands.from_changes import from_changes_command
from ana_speksi.commands.debt_analysis import debt_analysis_command
from ana_speksi.commands.update import update_command
from ana_speksi.commands.truth import truth_app

app = typer.Typer(
    name="ana-speksi",
    help="Skill-driven spec development framework.",
    no_args_is_help=True,
)

app.command("init")(init_command)
app.command("status")(status_command)
app.command("new")(new_command)
app.command("accept")(accept_command)
app.command("continue")(continue_command)
app.command("codify")(codify_command)
app.command("docufy")(docufy_command)
app.command("one-shot")(one_shot_command)
app.command("from-changes")(from_changes_command)
app.command("debt-analysis")(debt_analysis_command)
app.command("update")(update_command)
app.add_typer(truth_app, name="truth")


if __name__ == "__main__":
    app()
