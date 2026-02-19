"""CLI entry point for bas-spec."""

import typer

from bas_spec.commands.accept import accept_command
from bas_spec.commands.init import init_command
from bas_spec.commands.new import new_command
from bas_spec.commands.continue_cmd import continue_command
from bas_spec.commands.codify import codify_command
from bas_spec.commands.docufy import docufy_command
from bas_spec.commands.one_shot import one_shot_command
from bas_spec.commands.status import status_command
from bas_spec.commands.from_changes import from_changes_command
from bas_spec.commands.debt_analysis import debt_analysis_command
from bas_spec.commands.update import update_command
from bas_spec.commands.truth import truth_app
from bas_spec.commands.jira_stories import jira_stories_command
from bas_spec.commands.jira_create_story import jira_create_story_command
from bas_spec.commands.jira_update_story import jira_update_story_command

app = typer.Typer(
    name="bas-spec",
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
app.command("jira-stories")(jira_stories_command)
app.command("jira-create-story")(jira_create_story_command)
app.command("jira-update-story")(jira_update_story_command)


if __name__ == "__main__":
    app()
