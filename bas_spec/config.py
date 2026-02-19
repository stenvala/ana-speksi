"""Config loading and injection for bas-spec."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from bas_spec.status import get_bas_spec_root


def load_config(root: Path | None = None) -> dict[str, Any]:
    """Load bas-spec/config.yaml and return its contents.

    Returns an empty dict if the file does not exist or cannot be parsed.
    """
    if root is None:
        root = get_bas_spec_root()

    config_path = root / "config.yaml"
    if not config_path.exists():
        return {}

    try:
        import yaml

        return yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    except Exception:
        return {}


def get_context(config: dict[str, Any]) -> str | None:
    """Return the project context string from config, or None."""
    ctx = config.get("context")
    if ctx and isinstance(ctx, str) and ctx.strip():
        return ctx.strip()
    return None


def get_rules_for_phase(config: dict[str, Any], phase: str) -> list[str]:
    """Return the rules list for a given phase from config."""
    rules = config.get("rules", {})
    if not isinstance(rules, dict):
        return []
    phase_rules = rules.get(phase, [])
    if isinstance(phase_rules, list):
        return [str(r) for r in phase_rules]
    return []


def inject_config_into_skill(
    skill_body: str,
    config: dict[str, Any],
    phase: str | None = None,
) -> str:
    """Inject config context and phase-specific rules into a skill body.

    Context is wrapped in <context>...</context> tags.
    Rules are wrapped in <rules>...</rules> tags.
    Both are prepended before the skill body.
    """
    sections: list[str] = []

    context = get_context(config)
    if context:
        sections.append(f"<context>\n{context}\n</context>")

    if phase:
        rules = get_rules_for_phase(config, phase)
        if rules:
            rules_text = "\n".join(f"- {r}" for r in rules)
            sections.append(f"<rules>\n{rules_text}\n</rules>")

    if sections:
        return "\n\n".join(sections) + "\n\n" + skill_body
    return skill_body
