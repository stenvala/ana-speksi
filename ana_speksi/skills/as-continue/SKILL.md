---
name: as-continue
description: Continue working on an ana-speksi change by advancing to the next phase.
phase: null
---

Continue working on an ana-speksi change by advancing to the next phase.

**Input**: Optionally the spec name (e.g., `add-user-auth`). If a numeric prefix
was auto-generated, you can use either the short name or the full name
(e.g., `add-user-auth` or `001-add-user-auth`).

**Steps**

1. **Determine the spec to continue**

   If no name is provided, run:

   ```
   uv run ana-speksi status --toon
   ```

   Show available specs and ask the user to choose.

2. **Check current phase**

   Run:

   ```
   uv run ana-speksi status --toon
   ```

   Parse the output to determine the current phase of the selected spec.

3. **Check acceptance gate**

   Run:

   ```
   uv run ana-speksi accept --toon
   ```

   If `files_to_accept` is NOT empty, stop and inform the user:

   > "Cannot advance to next phase. The following files need acceptance:
   >
   > - [list files from files_to_accept]
   >
   > Run `/as-accept` to accept them first."

   Do NOT proceed past the gate. Stop and wait for the user.

4. **Story selection (techify, taskify, codify, docufy only)**

   If the next phase is techify, taskify, codify, or docufy, check the
   `stories_needing_work` from the continue command output (or compute it
   from the status JSON: stories missing the artifact for the current phase).

   If there are **more than 1** story needing work, ask the user:

   > "There are N stories to process in this phase:
   >
   > 1. 01-story-name
   > 2. 02-story-name
   >    ...
   >
   > Process all stories, or select specific ones?
   > (Processing fewer stories at a time helps manage context window size.)"

   If the user selects specific stories, pass only those to the phase skill.
   The user can run `/as-continue` again later to process the remaining stories.

   If there is only 1 story needing work, skip this step and process it directly.

5. **Execute the appropriate phase skill**

   Based on the current phase, invoke the corresponding skill:

   | Current Phase             | Next Action                                 | Skill to Invoke |
   | ------------------------- | ------------------------------------------- | --------------- |
   | proposal (done)           | Create functional specs per story           | as-storify      |
   | storify (done)            | Conduct research and create technical specs | as-techify      |
   | research / techify (done) | Create tasks per story                      | as-taskify      |
   | taskify (done)            | Implement code changes                      | as-codify       |
   | codify (done)             | Archive and update truth                    | as-docufy       |

   Read the referenced skill file for detailed instructions on the phase.

   When invoking the skill, pass the selected stories (if the user chose
   specific ones in step 4). The phase skill will only process those stories.

6. **After each phase, update index.md**

   Update the status indicators and phase status in `index.md`.
   Only four artifact types carry status indicators (`[]`, `[Draft]`,
   `[Accepted]`): proposal.md, functional-spec.md, technical-spec.md,
   tasks.md. All other files are resources listed without status.
   index.md must always reflect the current state of the spec.
   Every artifact creation or completion must be tracked immediately.

**Guardrails**

- Always run `uv run ana-speksi status` first to know where you are
- Follow the phase-specific skill instructions exactly
- Do NOT skip phases
- Do NOT bypass acceptance gates
- No emojis in any output or files
- Code changes are ONLY allowed during the codify phase
