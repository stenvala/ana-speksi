---
name: as-docufy
description: Archive a completed spec and update the ground truth.
phase: docufy
---

Archive a completed spec and update the ground truth.

**Input**: The spec name (e.g., `add-user-auth`).

**Steps**

1. **Verify all tasks are complete**

   Run:

   ```
   uv run ana-speksi status --toon
   ```

   Check that ALL tasks across ALL stories are marked as complete (`[x]`).
   If any tasks are incomplete, stop and inform the user:

   > "Cannot proceed with docufy. The following tasks are still incomplete:
   >
   > - [list incomplete tasks]
   >
   > Complete all tasks before archiving."

   Do NOT proceed if any tasks are incomplete.

2. **Check for deferred work (final-verdict.md)**

   Check if `final-verdict.md` exists at the spec root (same directory as `proposal.md`).

   If found:
   - Read the **Summary** section to identify which stories are deferred
   - Read the **Impact** section to understand implications for the current spec
   - Use these decisions to inform which specs are archived vs. kept in truth
   - Deferred stories should NOT be archived yet -- they may be continued in future iterations via `/as-continue`

   If NOT found:
   - Proceed normally -- all completed stories will be archived

   This step aligns with the `/as-final-verdict` skill which documents deferred work and implementation deviations.

3. **Update ground truth**

   **Story selection**: If `/as-continue` specified particular stories to
   process, only update truth for those stories. Otherwise, process all
   stories. The user can run `/as-continue` again to process more stories
   later. The spec is only archived (step 3) when all stories have been
   processed into truth.

   The truth directory (`ana-speksi/truth/`) contains a hierarchical system of
   features plus two special subdirectories:
   - `ana-speksi/truth/data-models/` -- Database design documentation per domain.
     Each file describes one domain's tables, relationships, constraints, seed
     data, and business rules. Use `resources/data-model-template.md` for the
     expected structure. Follow the conventions from the `database-model` skill
     and the existing examples under `docs/datamodels/`.
   - `ana-speksi/truth/enums/` -- All enumerations and their descriptions. Each
     file documents one enum: its values, which table/field uses it, and any
     notes. Use `resources/enum-template.md` for the expected structure.

   Analyze the completed spec and determine:
   - Does this extend an existing feature in truth?
   - Is this a new top-level feature?
   - Should this be a sub-feature of an existing one?
   - Does it introduce or modify data models? Update `truth/data-models/`.
   - Does it introduce or modify enums? Update `truth/enums/`.

   For the identified location in truth, create or update:
   - `functional-spec.md` -- consolidated functional specification
   - `technical-spec.md` -- consolidated technical specification
   - Sub-folders for sub-features if applicable

   **Extensions**: Check each story folder for `extension-*.md` files. These
   document additional functionality discovered and implemented during codify
   that was not in the original spec. Merge extension content into the truth
   alongside the regular specs -- extensions describe real functionality that
   was shipped and must be reflected in the ground truth.

   The truth is a living document that represents the current state of the
   system. Merge the new spec's content into the existing truth structure.

4. **Check for out-of-spec code changes**

   Ask the user:

   > "Were any code changes made outside of this spec's tasks (e.g., bug
   > fixes, refactors, or features implemented independently)?"

   If the user confirms there were out-of-spec changes:

   > "After docufy completes and the spec is archived, you should run
   > `/as-from-changes` to sync those code changes into the ground truth.
   > You can point it at the relevant pull request, branch, or diff."

   Proceed with archiving regardless -- this is informational only.

5. **Archive the spec**

   Move the spec folder from `ana-speksi/ongoing/<name>/` to
   `ana-speksi/archive/<date>-<name>/` where date is `yyyy-mm-dd` format.

6. **Report**

   Show what was archived and where truth was updated.

**Guardrails**

- Do NOT modify any code during this phase
- Truth must maintain a coherent hierarchical structure
- Archive preserves everything as-is
- No emojis in any output or files
