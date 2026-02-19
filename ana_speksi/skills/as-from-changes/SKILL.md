---
name: as-from-changes
description: Create or update ground truth from existing changes (commits, PRs, diffs, codebase).
phase: null
---

Create or update ground truth based on existing changes (code, commits, PRs).

Use this when:
- Manual changes were made without a spec
- Initializing truth for an existing codebase
- Retroactively documenting changes

**Input**: The source of changes. Must be one of:
- `--staged` -- From git staged changes
- `--commit <hash>` -- From a specific commit
- `--pr <number>` -- From a pull request
- `--diff` -- From current git diff
- `--folder <path>` -- From a specific folder
- `--codebase` -- From the entire codebase (initialization)

If no source is specified, ask the user which source to use.

**Steps**

1. **Analyze the changes**

   Based on the source, carefully analyze:
   - What files changed and how
   - What functional behavior was added or modified
   - What technical decisions were made
   - What API endpoints were added or changed
   - What database tables or fields were affected

   **For `--codebase` (whole codebase documentation):**

   When documenting an entire codebase, the analysis scope expands to include:
   - Overall system architecture and component interactions
   - Technology stack and framework choices
   - Deployment topology and infrastructure
   - Cross-cutting concerns (authentication, logging, error handling)
   - Integration points between subsystems

2. **Identify relevant skills**

   Search the repository for development skills (look in `.claude/skills/`,
   `.cursor/skills/`, `.github/skills/`). List all skills relevant
   to the changes discovered. This information feeds into the technical specs.

3. **Create truth entries**

   For each logical feature or change identified, determine the right place
   in the `ana-speksi/truth/` hierarchy. Group related changes into coherent
   features. Each feature gets its own folder under `ana-speksi/truth/`.

   **For `--codebase` (whole codebase documentation):**

   When documenting an entire codebase, first create the `ana-speksi/truth/platform/`
   folder structure to document overall architecture and functionality. This folder
   captures system-wide documentation that spans multiple features.

   Create subfolders as appropriate for the codebase, such as:
   - `platform/` -- Root for platform-level documentation
     - `architecture.md` -- Overall system architecture with mermaid diagrams
     - `ui/` -- Frontend/UI architecture and patterns
     - `backend/` -- Backend services architecture
     - `async-workers/` -- Background jobs, queues, async processing
     - `ci-cd/` -- Build, deployment, and CI/CD pipelines
     - `infrastructure/` -- Cloud resources, networking, hosting
     - `integrations/` -- Third-party service integrations

   **Mermaid diagrams are strongly encouraged** for visual documentation:
   - System context diagrams (C4 style)
   - Component interaction diagrams
   - Sequence diagrams for key flows
   - Deployment diagrams
   - ER diagrams for data models

   Example architecture.md structure:
   ```markdown
   # Platform Architecture

   ## System Overview
   [Description of the system purpose and scope]

   ## High-Level Architecture
   ```mermaid
   graph TB
       subgraph Frontend
           UI[Web UI]
       end
       subgraph Backend
           API[API Service]
           Workers[Async Workers]
       end
       subgraph Data
           DB[(Database)]
           Queue[Message Queue]
       end
       UI --> API
       API --> DB
       API --> Queue
       Workers --> Queue
       Workers --> DB
   ```

   ## Technology Stack
   [List of technologies with rationale]

   ## Component Interactions
   [Detailed component diagrams]
   ```

   **Enhancing existing platform documentation:**

   When the user asks to enhance or update the overall architecture, revise
   all content under `ana-speksi/truth/platform/` based on current codebase state.
   Compare existing documentation against actual implementation and update:
   - Add newly discovered components or services
   - Update diagrams to reflect current architecture
   - Remove documentation for deprecated/removed components
   - Improve diagram clarity and detail level

   Create the following artifacts per feature:

   ### functional-spec.md

   Create using `resources/functional-spec-template.md`. Each functional spec
   must contain:
   - Story definition (As a / I want / So that) -- reconstruct from the code
   - Detailed description of what the feature does
   - Requirements with WHEN/THEN acceptance scenarios -- derive from actual
     behavior in the code, not aspirational
   - Edge cases observed in the implementation
   - UI/UX considerations (if applicable)
   - Constraints

   The WHEN/THEN scenarios must be testable and reflect the real behavior.

   ### technical-spec.md

   Create using `resources/technical-spec-template.md`. Each technical spec
   must contain:
   - Overview of the implementation approach
   - Relevant skills table (from step 2)
   - Architecture -- how the feature fits into the system
   - Data model references (link to `ana-speksi/truth/data-models/` entries)
   - API endpoints involved (summary; full contracts go in api-contract.md)
   - Implementation details -- key patterns, notable code locations
   - Testing strategy (automated and manual)
   - Security considerations (if applicable)

   ### api-contract.md (if applicable)

   If the feature involves API endpoints, create using
   `resources/api-contract-template.md`. Include:
   - Each endpoint with HTTP method, path, description
   - Request and response schemas (derive from actual code / OpenAPI spec)
   - Error responses
   - Authentication requirements

   ### Data models

   If the change involves database tables, create or update a domain file
   in `ana-speksi/truth/data-models/` using `resources/data-model-template.md`.
   Follow the conventions from the database related skills. Include:
   - Mermaid ER diagram
   - Full table structures with field types and constraints
   - Enumeration definitions
   - Business rules (MUST / MUST NOT language)
   - Relationships

   ### Enums

   If the change introduces or modifies enums, create or update files in
   `ana-speksi/truth/enums/` using `resources/enum-template.md`.

4. **Cross-reference**

   Ensure consistency across all created artifacts:
   - Functional specs reference their technical specs
   - Technical specs reference relevant data models and API contracts
   - Data model entries are referenced from technical specs
   - Enum files are referenced from data model entries

5. **Report**

   Show what truth entries were created or updated. Present a summary table:

   | Feature | Artifacts Created | Location |
   |---------|------------------|----------|
   | [name]  | [list]           | [path]   |

**Guardrails**
- Do NOT modify any code
- Think deeply about the hierarchical structure of truth
- Group related changes into coherent features
- Functional specs must have testable WHEN/THEN scenarios derived from real behavior
- Technical specs must reference relevant skills
- Data model entries must follow the `ana-speksi/truth/data-models/` structure exactly
- For `--codebase`, always create `platform/` folder with architecture documentation first
- Use mermaid diagrams extensively for visual documentation (architecture, flows, ER diagrams)
- When enhancing architecture, review and update all `platform/` content against current code
- No emojis in any output or files
