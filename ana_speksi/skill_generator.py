"""Skill generation logic -- writes skill/prompt files for each agent framework."""

from __future__ import annotations

import shutil
from pathlib import Path

from rich.console import Console

from ana_speksi.config import inject_config_into_skill, load_config
from ana_speksi.models import AgentFramework, AGENT_SKILL_PATHS, AGENT_COMMAND_PATHS, Phase
from ana_speksi.resources import (
    SKILLS_DIR,
    list_skills,
    parse_skill_frontmatter,
    read_skill,
)

console = Console()

# Phase mapping for skills -- since frontmatter `phase` gets stripped by IDE
# linters, we maintain the mapping in code as the single source of truth.
SKILL_PHASES: dict[str, str] = {
    "as-new": "proposal",
    "as-storify": "storify",
    "as-techify": "research",
    "as-taskify": "taskify",
    "as-codify": "codify",
    "as-docufy": "docufy",
}

# Inverse mapping: Phase -> skill name
_PHASE_TO_SKILL: dict[Phase, str] = {
    Phase.PROPOSAL: "as-new",
    Phase.STORIFY: "as-storify",
    Phase.RESEARCH: "as-techify",
    Phase.TECHIFY: "as-techify",
    Phase.TASKIFY: "as-taskify",
    Phase.CODIFY: "as-codify",
    Phase.DOCUFY: "as-docufy",
}


def phase_to_skill(phase: Phase) -> str:
    """Map a phase to the skill name that executes it."""
    return _PHASE_TO_SKILL.get(phase, "as-continue")


def _wrap_frontmatter(
    framework: AgentFramework,
    name: str,
    description: str,
    body: str,
) -> str:
    """Wrap skill body with framework-specific YAML frontmatter."""
    if framework == AgentFramework.CURSOR:
        return (
            f"---\nname: {name}\ndescription: {description}\n"
            f"globs: []\nalwaysApply: false\n---\n\n{body}\n"
        )
    # Claude skills, Copilot skills -- same format
    return f"---\nname: {name}\ndescription: {description}\n---\n\n{body}\n"


def _make_command_stub(
    framework: AgentFramework,
    name: str,
    description: str,
) -> str:
    """Create a simple command stub that invokes the corresponding skill."""
    body = f"Invoke the skill `{name}` with arguments: $ARGUMENTS"
    if framework == AgentFramework.CURSOR:
        return f"---\ndescription: {description}\n---\n\n{body}\n"
    if framework == AgentFramework.COPILOT:
        return f"---\ndescription: {description}\n---\n\n{body}\n"
    # Claude commands
    return f"---\nname: {name}\ndescription: {description}\n---\n\n{body}\n"


def _copy_resources(src_skill_name: str, dest_dir: Path) -> None:
    """Copy the resources/ folder for a skill into the destination directory."""
    src = SKILLS_DIR / src_skill_name / "resources"
    if not src.exists() or not any(src.iterdir()):
        return
    dest = dest_dir / "resources"
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(src, dest)


def generate_skills(project_root: Path, frameworks: list[AgentFramework]) -> None:
    """Generate skill and command files for the selected agent frameworks."""
    config = load_config(project_root / "ana-speksi")
    for framework in frameworks:
        _generate_for_framework(project_root, framework, config)


def _generate_for_framework(
    project_root: Path,
    framework: AgentFramework,
    config: dict,
) -> None:
    """Generate all skills for a single framework."""
    skill_base = project_root / AGENT_SKILL_PATHS[framework]
    command_base = project_root / AGENT_COMMAND_PATHS[framework]

    for skill_name in list_skills():
        raw = read_skill(skill_name)
        meta, body = parse_skill_frontmatter(raw)
        name = meta.get("name", skill_name)
        description = meta.get("description", "")
        phase = SKILL_PHASES.get(name)

        # Inject project config (context + phase rules)
        body = inject_config_into_skill(body, config, phase)

        if framework == AgentFramework.CLAUDE:
            # Skill
            skill_dir = skill_base / name
            skill_dir.mkdir(parents=True, exist_ok=True)
            (skill_dir / "SKILL.md").write_text(
                _wrap_frontmatter(framework, name, description, body),
                encoding="utf-8",
            )
            _copy_resources(skill_name, skill_dir)
            # Command -- simple stub
            command_base.mkdir(parents=True, exist_ok=True)
            (command_base / f"{name}.md").write_text(
                _make_command_stub(framework, name, description),
                encoding="utf-8",
            )

        elif framework == AgentFramework.COPILOT:
            # Skill
            skill_dir = skill_base / name
            skill_dir.mkdir(parents=True, exist_ok=True)
            (skill_dir / "SKILL.md").write_text(
                _wrap_frontmatter(framework, name, description, body),
                encoding="utf-8",
            )
            _copy_resources(skill_name, skill_dir)
            # Prompt -- simple stub
            command_base.mkdir(parents=True, exist_ok=True)
            (command_base / f"{name}.prompt.md").write_text(
                _make_command_stub(framework, name, description),
                encoding="utf-8",
            )

        elif framework == AgentFramework.CURSOR:
            # Rule
            skill_base.mkdir(parents=True, exist_ok=True)
            (skill_base / f"{name}.md").write_text(
                _wrap_frontmatter(framework, name, description, body),
                encoding="utf-8",
            )
            # Command -- simple stub
            command_base.mkdir(parents=True, exist_ok=True)
            (command_base / f"{name}.md").write_text(
                _make_command_stub(framework, name, description),
                encoding="utf-8",
            )

    console.print(f"  Generated skills for [cyan]{framework.value}[/cyan]")


def detect_frameworks(project_root: Path) -> list[AgentFramework]:
    """Detect which agent frameworks are already set up in the project."""
    detected: list[AgentFramework] = []
    framework_markers = {
        AgentFramework.CLAUDE: ".claude",
        AgentFramework.CURSOR: ".cursor",
        AgentFramework.COPILOT: ".github",
    }
    for framework, marker_dir in framework_markers.items():
        if (project_root / marker_dir).exists():
            detected.append(framework)
    return detected
