# ana-speksi

ana-speksi is a **spec-driven development framework** backed by agent skills. Every code change flows through a structured specification process -- from proposal to implementation to archival. The framework provides slash commands (`/as-new`, `/as-codify`, etc.) that orchestrate this workflow within AI coding assistants.

## Repository structure

- `ana_speksi/` -- Python package (CLI + skill templates)
  - `ana_speksi/skills/` -- Skill templates (the source of truth for all `as-*` skills)
  - `ana_speksi/commands/` -- CLI command implementations
- `.claude/skills/` -- Generated skills for Claude Code (output of `uv run ana-speksi init`)
- `README.md` -- Full documentation of the framework

## Skill updates

When asked to update a skill, this means modifying the **skill template** under `ana_speksi/skills/`. The files under `.claude/skills/` (and equivalent locations for other editors) are generated output -- do not edit them directly.

Each skill template lives in `ana_speksi/skills/<skill-name>/` and contains a `SKILL.md` plus optional `resources/` directories.
