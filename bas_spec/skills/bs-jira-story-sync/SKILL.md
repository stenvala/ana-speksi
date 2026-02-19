---
name: bs-jira-story-sync
description: Sync stories to Jira by creating or updating Jira items for each story in a spec.
phase: storify
---

Sync stories to Jira by creating or updating Story-type Jira items for each story in a spec.

**Input**: The spec name (e.g., `APG-593.budgeting`).

**Prerequisites**

- The spec must have an index.md with stories defined (run bs-storify first)
- The zaira CLI must be installed and configured (`zaira init`)
- The parent Jira item (epic) must exist (extracted from spec folder name)

**Steps**

1. **Check current Jira story status**

   Run:

   ```
   uv run bas_spec jira-stories <spec-name> --toon
   ```

   This returns a JSON object showing which stories have Jira items linked
   and which do not. Review the output to understand current state.

2. **For stories WITHOUT Jira items**

   Before creating, ask the user:
   - Do you want to use the same Jira project for all stories?
   - If yes, which project key? (default: derived from parent item prefix)

   Run:

   ```
   uv run bas_spec jira-create-story <spec-name> --project <PROJECT_KEY> --toon
   ```

   The `--project` / `-p` option overrides the target Jira project. If omitted,
   the project is derived from the parent item.

   This command:
   - Creates a Story-type Jira item for each unlinked story
   - Sets parent to the top-level Jira item (epic) from proposal.md
   - Converts functional-spec.md content from markdown to Jira wiki markup
   - Copies mandatory fields from parent (components, fixVersions, labels)
   - Updates index.md with the new Jira item reference

   For a specific story only:

   ```
   uv run bas_spec jira-create-story <spec-name> <story-folder> --project <PROJECT_KEY>
   ```

3. **For stories WITH existing Jira items**

   Run:

   ```
   uv run bas_spec jira-update-story <spec-name> --toon
   ```

   This command:
   - For each story with a linked Jira item, prompts whether to update
     the Jira description with content from functional-spec.md
   - Converts markdown to Jira wiki markup
   - Replaces the existing description if confirmed

   Use `--yes` to skip confirmation prompts:

   ```
   uv run bas_spec jira-update-story <spec-name> --yes
   ```

   For a specific story only:

   ```
   uv run bas_spec jira-update-story <spec-name> <story-folder>
   ```

4. **Verify sync status**

   Run again:

   ```
   uv run bas_spec jira-stories <spec-name>
   ```

   All stories should now show "linked" status.

**index.md Format**

After syncing, each story section in index.md will have a Jira item reference:

```markdown
#### 01-configure-budget-structure

**Jira Item**: APG-594

**Implementation**: Not Started

- [Draft] [functional-spec.md](specs/01-configure-budget-structure/functional-spec.md)
...
```

The top-level Jira item (epic) can also be tracked:

```markdown
**Jira Item**: APG-593
```

**Guardrails**

- Do NOT create Jira items without user confirmation
- Do NOT update existing Jira descriptions without prompting (unless --yes)
- Stories are created as Story type, not Task or Sub-task
- Parent is set via the `parent` field on the child story (not via link types)
- Mandatory fields are copied from parent to maintain consistency
- Markdown is converted to Jira wiki markup for descriptions

**Troubleshooting**

- If zaira is not found: Run `uv pip install zaira` and `zaira init`
- If link type fails: Check `zaira info` for available link types in your Jira instance
- If fields fail to copy: Some fields may require different permissions
