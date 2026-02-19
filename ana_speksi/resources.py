"""Resource file loading utilities for ana_speksi skills and templates."""

from __future__ import annotations

from pathlib import Path

SKILLS_DIR = Path(__file__).parent / "skills"


def get_skill_path(skill_name: str) -> Path:
    """Return the path to a skill's SKILL.md file."""
    return SKILLS_DIR / skill_name / "SKILL.md"


def get_resource_path(skill_name: str, filename: str) -> Path:
    """Return the path to a skill's resource file."""
    return SKILLS_DIR / skill_name / "resources" / filename


def read_skill(skill_name: str) -> str:
    """Read a skill's SKILL.md content."""
    return get_skill_path(skill_name).read_text(encoding="utf-8")


def read_resource(skill_name: str, filename: str) -> str:
    """Read a skill resource file."""
    return get_resource_path(skill_name, filename).read_text(encoding="utf-8")


def read_template(skill_name: str, filename: str, **kwargs: str) -> str:
    """Read a resource template and format it with the given kwargs."""
    content = read_resource(skill_name, filename)
    return content.format_map(kwargs)


def list_skills() -> list[str]:
    """Return a sorted list of all skill names (folder names under skills/)."""
    if not SKILLS_DIR.exists():
        return []
    return sorted(
        d.name for d in SKILLS_DIR.iterdir() if d.is_dir() and (d / "SKILL.md").exists()
    )


def parse_skill_frontmatter(content: str) -> tuple[dict[str, str], str]:
    """Parse YAML frontmatter from a skill file.

    Returns (metadata_dict, body) where metadata_dict has keys like
    name, description, phase.
    """
    if not content.startswith("---"):
        return {}, content

    parts = content.split("---", 2)
    if len(parts) < 3:
        return {}, content

    metadata: dict[str, str] = {}
    for line in parts[1].strip().splitlines():
        if ":" in line:
            key, _, value = line.partition(":")
            metadata[key.strip()] = value.strip()

    return metadata, parts[2].lstrip("\n")
