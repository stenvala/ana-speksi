---
name: as-new
description: Start a new ana-speksi change by creating a proposal. Use when the user wants to build something new or make a change.
phase: proposal
---

Start a new ana-speksi change by creating a proposal.

**Input**: The user's description of what they want to build or change, and a ticket ID.

**Steps**

1. **Get the ticket ID**

   If no ticket ID (e.g. PROJ-123) is provided, ask the user:

   > "What is the ticket ID for this change?"

   Do NOT proceed without a ticket ID.

2. **Understand the request**

   If no clear description is provided, ask the user:

   > "What do you want to build or change? Describe the problem and desired outcome."

   Do NOT proceed without understanding the request.

3. **Run the CLI to scaffold the spec**

   If the user has a description:

   ```
   uv run ana-speksi new "<ticket-id>" "<description>" --name "<short-name>"
   ```

   If no description is provided:

   ```
   uv run ana-speksi new "<ticket-id>" --name "<short-name>"
   ```

   The CLI will:
   - Create the folder under `ana-speksi/ongoing/<ticket-id>.<short-name>/`
   - Create an initial `proposal.md` from the template with the description in the Original Prompt section

4. **Review existing architecture**

   Before filling in the proposal, review the ground truth under `ana-speksi/truth/`:
   - Explore the hierarchy to understand the system's current architecture
   - Check `ana-speksi/truth/platform/` for detecting relevant components, services and patterns

   If no `ana-speksi/truth/` directory exists, note this and proceed without it.
   Understanding the existing architecture helps create more accurate proposals
   that align with the current system.

5. **Fill in proposal.md**

   Read the template at `ana-speksi/ongoing/<name>/proposal.md` and fill it in,
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

   The proposal must have `**Status**: Draft` and `**Generated with**: as-new`
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
