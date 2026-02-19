---
name: as-accept
description: Mark the current phase's outputs as Accepted. Run before advancing to the next phase.
phase: null
---

Mark the current phase's outputs as Accepted so the workflow can advance.

**Input**: Optionally the spec name (e.g., `add-user-auth`). If not provided,
auto-detects if there is a single ongoing spec.

**Steps**

1. **Preview what will be accepted**

   Run:

   ```
   uv run ana_speksi accept --toon
   ```

   (or with a spec name: `uv run ana_speksi accept <name> --toon`)

   The output tells you:
   - Which spec and phase you are in
   - Which files need to be accepted
   - Which files are already accepted

2. **Ask for confirmation**

   Ask the user:

   > "The following files will be marked as Accepted:
   >
   > - [list files]
   >
   > Do you want to accept all of these?"

3. **Apply acceptance**

   Run:

   ```
   uv run ana_speksi accept
   ```

   (or with a spec name: `uv run ana_speksi accept <name>`)

   The command will:
   - Update `**Status**: Draft` to `**Status**: Accepted` in each file
   - Update `[Draft]` to `[Accepted]` in index.md

4. **Commit the acceptance (mandatory)**

   After acceptance, a commit is required. First check git status:

   ```
   git status
   ```

   If there are unstaged files, inform the user and help them stage:

   > "There are unstaged files. Please stage all files before committing:
   >
   > ```
   > git add -A
   > ```
   >
   > Or stage specific files with `git add <file>`"

   Once all files are staged, ask the user to run:

   > "Please commit the acceptance using `/commit`
   >
   > Include in the commit message that this is an ana-speksi phase acceptance, e.g.:
   > `ana-speksi: accept <phase> phase for <spec-name>`"

**Acceptance Gates**

The following gates must be passed before advancing phases:

| Phase    | Must Accept                  |
| -------- | ---------------------------- |
| proposal | proposal.md                  |
| storify  | all functional-spec.md files |
| techify  | all technical-spec.md files  |
| taskify  | all tasks.md files           |

If any required file is not Accepted, `as-continue` will block the transition
and direct the user to run `as-accept` first.

**Guardrails**

- Do NOT modify any content other than the Status field
- Do NOT write any code
- Always present files for user review before marking Accepted
- No emojis in any output or files
