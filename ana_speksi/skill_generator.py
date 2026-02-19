"""Skill generation logic -- writes skill/prompt files for each agent framework."""

from __future__ import annotations

import shutil
from pathlib import Path

from rich.console import Console

from ana-speksi.config import inject_config_into_skill, load_config
from ana-speksi.models import AgentFramework, AGENT_SKILL_PATHS, AGENT_COMMAND_PATHS
from ana-speksi.resources import (
    SKILLS_DIR,
    list_skills,
    parse_skill_frontmatter,
    read_skill,
)

console = Console()


def _wrap_frontmatter(
    framework: AgentFramework,
    name: str,
    description: str,
    body: str,
    *,
    is_command: bool = False,
) -> str:
    """Wrap skill body with framework-specific YAML frontmatter."""
    if framework == AgentFramework.CURSOR:
        if is_command:
            return f"---\ndescription: {description}\n---\n\n{body}\n"
        return (
            f"---\nname: {name}\ndescription: {description}\n"
            f"globs: []\nalwaysApply: false\n---\n\n{body}\n"
        )
    if is_command and framework == AgentFramework.COPILOT:
        return f"---\ndescription: {description}\n---\n\n{body}\n"
    # Claude skills, Claude commands, Copilot skills -- same format
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
        phase = meta.get("phase") if meta.get("phase") != "null" else None

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
            # Command
            command_base.mkdir(parents=True, exist_ok=True)
            (command_base / f"{name}.md").write_text(
                _wrap_frontmatter(framework, name, description, body, is_command=True),
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
            # Prompt
            command_base.mkdir(parents=True, exist_ok=True)
            (command_base / f"{name}.prompt.md").write_text(
                _wrap_frontmatter(
                    framework,
                    name,
                    description,
                    body,
                    is_command=True,
                ),
                encoding="utf-8",
            )

        elif framework == AgentFramework.CURSOR:
            # Rule
            skill_base.mkdir(parents=True, exist_ok=True)
            (skill_base / f"{name}.md").write_text(
                _wrap_frontmatter(framework, name, description, body),
                encoding="utf-8",
            )
            # Command
            command_base.mkdir(parents=True, exist_ok=True)
            (command_base / f"{name}.md").write_text(
                _wrap_frontmatter(
                    framework,
                    name,
                    description,
                    body,
                    is_command=True,
                ),
                encoding="utf-8",
            )

    console.print(f"  Generated skills for [cyan]{framework.value}[/cyan]")
