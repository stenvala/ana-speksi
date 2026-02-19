"""Core models and constants for ana-speksi."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Directory layout
# ---------------------------------------------------------------------------

ana-speksi_DIR = "ana-speksi"
ONGOING_DIR = "ongoing"
TRUTH_DIR = "truth"
ARCHIVE_DIR = "archive"
TECHNICAL_DEBT_DIR = "technical-debt"

# Subdirectories under truth/
TRUTH_DATA_MODELS_DIR = "data-models"
TRUTH_ENUMS_DIR = "enums"

SUBDIRS = [ONGOING_DIR, TRUTH_DIR, ARCHIVE_DIR, TECHNICAL_DEBT_DIR]


# ---------------------------------------------------------------------------
# Phases
# ---------------------------------------------------------------------------


class Phase(str, Enum):
    """Workflow phases in order."""

    PROPOSAL = "proposal"
    STORIFY = "storify"
    RESEARCH = "research"
    TECHIFY = "techify"
    TASKIFY = "taskify"
    CODIFY = "codify"
    DOCUFY = "docufy"


class DocStatus(str, Enum):
    """Status of a spec document."""

    EMPTY = "empty"
    DRAFT = "Draft"
    ACCEPTED = "Accepted"


PHASE_ORDER = list(Phase)


PHASE_DESCRIPTIONS: dict[Phase, str] = {
    Phase.PROPOSAL: "Create high-level proposal (proposal.md)",
    Phase.STORIFY: "Create functional specifications per user story",
    Phase.RESEARCH: "Conduct technical research and create technical specs",
    Phase.TECHIFY: "Create technical specifications per story",
    Phase.TASKIFY: "Create implementation tasks per story",
    Phase.CODIFY: "Implement code changes based on tasks",
    Phase.DOCUFY: "Archive completed spec and update ground truth",
}


# ---------------------------------------------------------------------------
# Spec metadata
# ---------------------------------------------------------------------------


@dataclass
class StoryStatus:
    """Status of a single user story."""

    folder: str
    name: str
    has_functional_spec: bool = False
    has_technical_spec: bool = False
    has_data_model: bool = False
    has_api_contract: bool = False
    has_test_plan: bool = False
    has_manual_test_plan: bool = False
    has_tasks: bool = False
    tasks_total: int = 0
    tasks_done: int = 0
    functional_spec_status: DocStatus = DocStatus.EMPTY
    technical_spec_status: DocStatus = DocStatus.EMPTY
    tasks_status: DocStatus = DocStatus.EMPTY


@dataclass
class SpecStatus:
    """Status of an ongoing spec."""

    name: str
    path: Path
    phase: Phase
    has_proposal: bool = False
    has_index: bool = False
    has_research: bool = False
    proposal_status: DocStatus = DocStatus.EMPTY
    stories: list[StoryStatus] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Naming helpers
# ---------------------------------------------------------------------------


def make_spec_name(ticket_id: str, short_name: str) -> str:
    """Create a spec folder name like TICKET-123.add-user-auth."""
    return f"{ticket_id}.{short_name}"


def slugify(text: str) -> str:
    """Convert text to kebab-case slug."""
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-+", "-", text)
    return text.strip("-")


# ---------------------------------------------------------------------------
# Agent frameworks
# ---------------------------------------------------------------------------


class AgentFramework(str, Enum):
    """Supported agentic frameworks."""

    CLAUDE = "claude"
    CURSOR = "cursor"
    COPILOT = "copilot"


AGENT_SKILL_PATHS: dict[AgentFramework, str] = {
    AgentFramework.CLAUDE: ".claude/skills",
    AgentFramework.CURSOR: ".cursor/rules",
    AgentFramework.COPILOT: ".github/skills",
}

AGENT_COMMAND_PATHS: dict[AgentFramework, str] = {
    AgentFramework.CLAUDE: ".claude/commands",
    AgentFramework.CURSOR: ".cursor/commands",
    AgentFramework.COPILOT: ".github/prompts",
}
