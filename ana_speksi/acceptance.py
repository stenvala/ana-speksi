"""Acceptance gate logic for ana_speksi."""

from __future__ import annotations

import re
from pathlib import Path

from ana_speksi.config import get_auto_confirm
from ana_speksi.models import DocStatus, Phase, SpecStatus
from ana_speksi.status import update_index_task_counts


# Maps the current detected phase to what should be accepted next.
_ACCEPTANCE_TARGETS: dict[Phase, dict] = {
    Phase.PROPOSAL: {
        "label": "proposal",
        "description": "Accept proposal before storify",
        "check_proposal": True,
        "check_functional_specs": False,
        "check_technical_specs": False,
        "check_tasks": False,
    },
    Phase.STORIFY: {
        "label": "functional specs",
        "description": "Accept all functional specs to advance past storify",
        "check_proposal": False,
        "check_functional_specs": True,
        "check_technical_specs": False,
        "check_tasks": False,
    },
    Phase.RESEARCH: {
        "label": "functional specs + proposal",
        "description": "Accept proposal and all functional specs to proceed to techify",
        "check_proposal": True,
        "check_functional_specs": True,
        "check_technical_specs": False,
        "check_tasks": False,
    },
    Phase.TECHIFY: {
        "label": "technical specs",
        "description": "Accept all technical specs to proceed to taskify",
        "check_proposal": False,
        "check_functional_specs": False,
        "check_technical_specs": True,
        "check_tasks": False,
    },
    Phase.TASKIFY: {
        "label": "tasks",
        "description": "Accept all tasks to proceed to codify",
        "check_proposal": False,
        "check_functional_specs": False,
        "check_technical_specs": False,
        "check_tasks": True,
    },
}


def get_acceptance_status(spec: SpecStatus) -> dict:
    """Return acceptance status for a spec (files_to_accept, already_accepted).

    This is a pure data function with no side effects -- used by other commands
    to check the acceptance gate before proceeding.
    """
    auto_confirm = get_auto_confirm()

    target = _ACCEPTANCE_TARGETS.get(spec.phase)
    if not target:
        return {
            "spec": spec.name,
            "phase": spec.phase.value,
            "auto_confirm": auto_confirm,
            "acceptance_target": None,
            "description": f"No acceptance action for phase: {spec.phase.value}",
            "files_to_accept": [],
            "already_accepted": [],
        }

    files_to_accept: list[str] = []
    already_accepted: list[str] = []

    if target["check_proposal"]:
        proposal_path = spec.path / "proposal.md"
        if spec.proposal_status == DocStatus.ACCEPTED:
            already_accepted.append(str(proposal_path))
        elif proposal_path.exists():
            files_to_accept.append(str(proposal_path))

    if target["check_functional_specs"]:
        for story in spec.stories:
            fp = spec.path / "specs" / story.folder / "functional-spec.md"
            if story.functional_spec_status == DocStatus.ACCEPTED:
                already_accepted.append(str(fp))
            elif fp.exists():
                files_to_accept.append(str(fp))

    if target["check_technical_specs"]:
        for story in spec.stories:
            fp = spec.path / "specs" / story.folder / "technical-spec.md"
            if story.technical_spec_status == DocStatus.ACCEPTED:
                already_accepted.append(str(fp))
            elif fp.exists():
                files_to_accept.append(str(fp))

    if target["check_tasks"]:
        for story in spec.stories:
            fp = spec.path / "specs" / story.folder / "tasks.md"
            if story.tasks_status == DocStatus.ACCEPTED:
                already_accepted.append(str(fp))
            elif fp.exists():
                files_to_accept.append(str(fp))

    return {
        "spec": spec.name,
        "phase": spec.phase.value,
        "auto_confirm": auto_confirm,
        "acceptance_target": target["label"],
        "description": target["description"],
        "files_to_accept": files_to_accept,
        "already_accepted": already_accepted,
    }


def update_file_status(file_path: str) -> bool:
    """Update **Status**: Draft to **Status**: Accepted in a file."""
    path = Path(file_path)
    if not path.exists():
        return False
    content = path.read_text(encoding="utf-8")
    new_content = re.sub(
        r"\*\*Status\*\*:\s*Draft",
        "**Status**: Accepted",
        content,
    )
    if new_content != content:
        path.write_text(new_content, encoding="utf-8")
        return True
    return False


def update_index_entry(index_path: Path, file_path: str, spec_path: Path) -> bool:
    """Update [Draft] to [Accepted] for a file entry in index.md."""
    if not index_path.exists():
        return False
    rel_path = Path(file_path).relative_to(spec_path)
    filename = Path(file_path).name
    content = index_path.read_text(encoding="utf-8")
    old = f"- [Draft] [{filename}]({rel_path})"
    new = f"- [Accepted] [{filename}]({rel_path})"
    if old in content:
        content = content.replace(old, new)
        index_path.write_text(content, encoding="utf-8")
        return True
    return False
