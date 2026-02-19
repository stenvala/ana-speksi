# bas-spec

Spec-driven development framework backed up with skills.

## Philosophy

bas-spec is a **spec-driven development framework** where every change flows through a structured specification process -- from proposal to implementation to archival. The framework is backed by **skills**: your repository contains agent skills that define how to do everything (CI/CD, API endpoints, database design, UI components, etc.). bas-spec orchestrates this workflow, ensuring that specifications drive the code and skills ensure consistency.

All interaction happens through **agent editor commands** (slash commands like `/bs-new`). The CLI exists only for initialization and housekeeping -- the real workflow is driven by your AI coding assistant.

## Installation

1. Clone bas-spec into your project root:

```bash
git clone https://github.com/anttiste_Basware/bas-spec.git bas-spec-package
```

2. Add the following to your project's `pyproject.toml`:

```toml
# Add bas-spec to your dependencies
[project]
dependencies = [
    # ... your other dependencies ...
    "bas-spec",
]

# Register bas-spec-package as a workspace member
[tool.uv.workspace]
members = ["bas-spec-package"]

# Point the bas-spec dependency to the local workspace package
[tool.uv.sources]
bas-spec = { workspace = true }
```

3. Install dependencies:

```bash
uv sync
```

## Setup

```bash
# 1. Initialize bas-spec in your project (generates skills + commands for your editor)
uv run bas_spec init

# 2. After updating bas-spec, regenerate skills without touching bas-spec/ folder
uv run bas_spec update
```

After init, your agent editor (Claude Code, GitHub Copilot, Cursor) has all the commands and skills available. Use them directly in the editor or CLI.

## Usage

All commands are used as slash commands in your AI coding assistant:

```
/bs-new "add user authentication"     # Start a new change
/bs-accept add-user-authentication    # Accept current phase outputs
/bs-continue add-user-authentication  # Advance to the next phase
/bs-codify add-user-authentication    # Start/continue implementation
/bs-docufy add-user-authentication    # Archive and update ground truth
/bs-from-changes --codebase           # Create truth from existing code
/bs-debt-analysis src/api             # Analyze technical debt
```

Check status anytime with:
```bash
uv run bas_spec status
```

## Workflow

```
/bs-new (proposal)
  |
  v
/bs-accept (accept proposal)
  |
  v
/bs-continue -> storify (functional specs per story)
  |
  v
/bs-accept (accept proposal + functional specs)
  |
  v
/bs-continue -> techify (research + technical specs)
  |
  v
/bs-accept (accept technical specs)
  |
  v
/bs-continue -> taskify (implementation tasks per story)
  |
  v
/bs-accept (accept tasks)
  |
  v
/bs-continue or /bs-codify (implementation -- ONLY phase with code changes)
  |
  v
/bs-continue or /bs-docufy (archive + update ground truth)
```

Each phase transition requires acceptance of the current phase's outputs
before advancing. Use `/bs-accept` to review and mark outputs as Accepted.
In `/bs-one-shot` mode, all outputs are auto-accepted.

## Directory Structure

```
bas-spec/
  ongoing/        # Specs currently being worked on
  truth/          # Ground truth -- hierarchical feature documentation
  archive/        # Completed specs (prefixed with date)
  technical-debt/ # Technical debt analyses
  config.yaml     # Project configuration
```

## Spec Structure (under ongoing/)

```
JIRA-123.feature-name/               # Folder name includes Jira epic ID
  proposal.md                        # High-level proposal
  index.md                           # Progress tracker (includes Jira item refs)
  research.md                        # Technical research
  specs/
    01-story-name/
      functional-spec.md             # Functional requirements (WHEN/THEN)
      technical-spec.md              # Technical design
      data-model.md                  # Data model changes (optional)
      api-contract.md                # API changes (optional)
      test-automation-plan.md        # Automated test plan (optional)
      manual-testing-plan.md         # Manual test plan (optional)
      tasks.md                       # Implementation tasks
    02-another-story/
      ...
```

## Agent Commands

These commands are available as slash commands in your AI coding assistant:

| Command | Description |
|---------|-------------|
| `/bs-new` | Start a new spec-driven change |
| `/bs-accept <name>` | Review and accept current phase outputs |
| `/bs-continue <name>` | Advance to the next phase |
| `/bs-jira-story-sync <name>` | Sync stories to Jira (create/update Jira items) |
| `/bs-codify <name>` | Start/continue implementation |
| `/bs-docufy <name>` | Archive and update ground truth |
| `/bs-one-shot <desc>` | Run all phases without stopping (auto-accepts all) |
| `/bs-from-changes` | Create truth from existing changes/codebase |
| `/bs-debt-analysis <target>` | Analyze technical debt (no code changes) |

## CLI Commands

These are run directly in the terminal for setup and status:

| Command | Description |
|---------|-------------|
| `uv run bas_spec init` | Initialize bas-spec (creates dirs, generates agent skills) |
| `uv run bas_spec update` | Regenerate skills and commands (does not touch bas-spec/) |
| `uv run bas_spec status` | Show status of all ongoing specs |
| `uv run bas_spec accept [name]` | Show acceptance status for a spec |
| `uv run bas_spec truth show` | Display the ground truth hierarchy |
| `uv run bas_spec truth rearrange <desc>` | Reorganize ground truth |
| `uv run bas_spec jira-stories <name>` | List Jira story associations for a spec |
| `uv run bas_spec jira-create-story <name>` | Create Jira stories for unlinked stories |
| `uv run bas_spec jira-update-story <name>` | Update Jira story descriptions from functional specs |

## Phase Skills

Each phase has a corresponding agent skill that provides detailed instructions:

| Phase | Skill | What It Does |
|-------|-------|-------------|
| Proposal | bs-new | Creates proposal.md with problem, stories, requirements |
| Accept | bs-accept | Reviews and marks phase outputs as Accepted |
| Storify | bs-storify | Creates functional specs with WHEN/THEN scenarios |
| Jira Sync | bs-jira-story-sync | Creates/updates Jira stories from functional specs |
| Research + Techify | bs-techify | Research + technical specs per story |
| Taskify | bs-taskify | Creates task lists referencing skills |
| Codify | bs-codify | Implements tasks (ONLY code change phase) |
| Docufy | bs-docufy | Archives spec, updates ground truth |

## Ad Hoc Workflows

### Retroactive Documentation

```
/bs-from-changes --staged        # From staged changes
/bs-from-changes --commit abc123 # From a specific commit
/bs-from-changes --codebase      # Initialize truth for entire codebase
```

### Technical Debt

```
/bs-debt-analysis src/api              # Analyze a folder
/bs-debt-analysis database-design      # Analyze against a skill
/bs-new --from-debt bas-spec/technical-debt/2026-02-10-src-api.md  # Then clear the debt
```

### Jira Integration

After creating functional specs with `/bs-storify`, sync stories to Jira:

```
/bs-jira-story-sync APG-593.budgeting  # Create/update Jira stories
```

Or use CLI commands directly:

```bash
uv run bas_spec jira-stories APG-593.budgeting        # List Jira associations
uv run bas_spec jira-create-story APG-593.budgeting   # Create missing Jira stories
uv run bas_spec jira-update-story APG-593.budgeting   # Update Jira descriptions
```

The Jira integration:
- Creates Story-type items linked to the parent epic
- Uses functional-spec.md content as the Jira description
- Copies mandatory fields (components, fixVersions, labels) from parent
- Updates index.md with Jira item references

Requires [zaira](https://github.com/vivainio/zaira) CLI to be installed and configured (`zaira init`).

## Supported Agent Frameworks

| Framework | Skills Location | Commands/Prompts Location |
|-----------|----------------|--------------------------|
| Claude Code | `.claude/skills/` | `.claude/commands/` |
| GitHub Copilot | `.github/skills/` | `.github/prompts/` |
| Cursor | `.cursor/rules/` | `.cursor/commands/` |

## Acceptance Workflow

Every spec document has a `**Status**` field that tracks its acceptance state:

| Status | Meaning |
|--------|---------|
| Draft | Document created, pending review |
| Accepted | Reviewed and approved by user |

Phase transitions are gated by acceptance:

| To Advance To | Must Accept |
|---|---|
| techify | proposal.md + all functional-spec.md |
| taskify | all technical-spec.md |
| codify | all tasks.md |

Use `/bs-accept` to review and mark outputs as Accepted. The AI agent will present
each file for review and ask for confirmation before changing status.

In `/bs-one-shot` mode, all documents are auto-accepted immediately after creation.

## Document Status in index.md

Progress is tracked in index.md using status indicators (not checkboxes):

```
- [] [research.md](research.md)                    # Not created yet
- [Draft] [functional-spec.md](path)               # Created, pending review
- [Accepted] [functional-spec.md](path)             # Reviewed and accepted
```

## Generated With

All key documents include a `**Generated with**` header field that tracks
which command created them (e.g., `bs-new`, `bs-storify`, `one-shot`).

## Key Principles

1. **Spec-driven**: Every change starts with a specification before code
2. **Skill-backed**: Every task references a development skill from the repo
3. **Acceptance-gated**: Phase transitions require explicit approval of outputs
4. **No branch management**: User handles git branching
5. **Code changes only in codify**: All other phases are documentation only
6. **Hierarchical truth**: Ground truth reflects how features build on each other
7. **No emojis**: Clean, professional documentation
8. **Templates are editable**: All markdown lives in skill files that users can customize

## Example Skills

bas-spec tasks reference skills that define how to implement things in your project. Here are typical skills you might have:

| Category | Skills | Purpose |
|----------|--------|---------|
| **Backend** | `backend-service`, `backend-router`, `backend-test` | Service layer, API routing, backend tests |
| **Frontend** | `frontend-component`, `frontend-service`, `frontend-store`, `frontend-dialog`, `frontend-forms` | UI components, services, state management, dialogs, forms |
| **Database** | `database-design`, `database-model`, `database-repository`, `database-schema-edit-*`, `database-setup-*` | Schema design, ORM models, data access, migrations |
| **Testing** | `backend-test`, `integration-test`, `e2e-test` | Unit, integration, and end-to-end testing |
| **Code Quality** | `code-simplifier`, `commit` | Refactoring, git commit conventions |
| **DevOps** | `ci-cd`, `infrastructure-as-code` | CI/CD pipelines, infrastructure provisioning |
| **Project** | `create-project`, `skill-creator` | Project scaffolding, creating new skills |

Skills are project-specific. You define them to match your stack and conventions.
