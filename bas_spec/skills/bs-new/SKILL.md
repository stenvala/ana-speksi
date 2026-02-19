---
name: bs-new
description: Start a new bas-spec change by creating a proposal. Use when the user wants to build something new or make a change.
phase: proposal
---

Start a new bas-spec change by creating a proposal.

**Input**: The user's description of what they want to build or change, and a Jira item identifier.

**Steps**

1. **Get the Jira item**

   If no Jira item identifier (e.g. PROJ-123) is provided, ask the user:

   > "What is the Jira item for this change?"

   Do NOT proceed without a Jira item.

2. **Understand the request**

   If no clear description is provided, the CLI will automatically attempt to fetch
   the description from the Jira ticket using the zaira tool.

   If zaira is not available or the fetch fails, ask the user:

   > "What do you want to build or change? Describe the problem and desired outcome."

   Do NOT proceed without understanding the request.

3. **Run the CLI to scaffold the spec**

   If the user has a description:
   ```
   uv run bas_spec new "<jira-item>" "<description>" --name "<short-name>"
   ```

   If no description is provided (will fetch from Jira):
   ```
   uv run bas_spec new "<jira-item>" --name "<short-name>"
   ```

   The CLI will:
   - Attempt to fetch the Jira description using zaira if no description is provided
   - Create the folder under `bas-spec/ongoing/<jira-item>.<short-name>/`
   - Create an initial `proposal.md` from the template with the Jira description in the Original Prompt section

4. **Review existing architecture**

   Before filling in the proposal, review the ground truth under `bas-spec/truth/`:
   - Explore the hierarchy to understand the system's current architecture
   - Check `bas-spec/truth/platform/` for detecting relevant components, services and patterns

   If no `bas-spec/truth/` directory exists, note this and proceed without it.
   Understanding the existing architecture helps create more accurate proposals
   that align with the current system.

5. **Fill in proposal.md**

   Read the template at `bas-spec/ongoing/<name>/proposal.md` and fill it in,
   using insights from the architecture review in step 4:
   - **Original Prompt**: Copy the user's original request verbatim
   - **Problem Statement**: Articulate the problem clearly
   - **User Stories**: List high-level user stories with names and "why"
     - Do NOT include acceptance scenarios yet
     - Keep stories focused on user value
   - **Functional Requirements**: High-level requirements
     - Non-technical unless this is a purely technical change
   - **Success Criteria**: Measurable outcomes
   - **Out of Scope**: What is excluded
   - **Assumptions**: What we assume
   - **Dependencies**: External dependencies

   The proposal must have `**Status**: Draft` and `**Generated with**: bs-new`
   in the header. These are set by the template.

   Reference the proposal template in this skill's `resources/proposal-template.md`
   for the expected structure.

6. **STOP and present to user**

   Show the proposal and ask the user to review. The user may:
   - Accept it as-is
   - Request changes (edit proposal.md accordingly)
   - Ask clarifying questions

**Guardrails**

- Do NOT create any other artifacts beyond proposal.md
- Do NOT write any code
- Do NOT proceed to the next phase without user approval
- Keep the proposal non-technical unless the change is purely technical
- No emojis in any output or files
