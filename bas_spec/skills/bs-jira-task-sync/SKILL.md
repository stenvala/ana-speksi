````skill
---
name: bs-jira-task-sync
description: Sync tasks to Jira by creating or updating Jira sub-task items for each story/task in a spec.
phase: storify
---

Sync tasks to Jira by creating or updating Sub-task type Jira items for each story in a spec.
Use this skill when the parent Jira item is a **Story** (not an Epic).

**Input**: The spec name (e.g., `APG-594.configure-budget`).

**Prerequisites**

- The spec must have an index.md with stories defined (run bs-storify first)
- The zaira CLI must be installed and configured (`zaira init`)
- The parent Jira item (story) must exist (extracted from spec folder name)

**Steps**

1. **Check current Jira task status**

   Run:

   ```
   uv run bas_spec jira-stories <spec-name> --item-type subtask --toon
   ```

   This returns a JSON object showing which stories/tasks have Jira items linked
   and which do not. Review the output to understand current state.

2. **For tasks WITHOUT Jira items**

   Before creating, ask the user:
   - Do you want to use the same Jira project for all tasks?
   - If yes, which project key? (default: derived from parent item prefix)

   Run:

   ```
   uv run bas_spec jira-create-story <spec-name> --item-type subtask --project <PROJECT_KEY> --toon
   ```

   The `--project` / `-p` option overrides the target Jira project. If omitted,
   the project is derived from the parent item.

   The `--item-type subtask` flag tells the command to create Sub-task type items
   instead of Story type items.

   This command:
   - Creates a Sub-task type Jira item for each unlinked task
   - Sets parent to the top-level Jira item (story) from proposal.md
   - Converts functional-spec.md content from markdown to Jira wiki markup
   - Copies mandatory fields from parent (components, fixVersions, labels)
   - Updates index.md with the new Jira item reference

   For a specific task only:

   ```
   uv run bas_spec jira-create-story <spec-name> <story-folder> --item-type subtask --project <PROJECT_KEY>
   ```

3. **For tasks WITH existing Jira items**

   Run:

   ```
   uv run bas_spec jira-update-story <spec-name> --item-type subtask --toon
   ```

   This command:
   - For each task with a linked Jira item, prompts whether to update
     the Jira description with content from functional-spec.md
   - Converts markdown to Jira wiki markup
   - Replaces the existing description if confirmed

   Use `--yes` to skip confirmation prompts:

   ```
   uv run bas_spec jira-update-story <spec-name> --item-type subtask --yes
   ```

   For a specific task only:

   ```
   uv run bas_spec jira-update-story <spec-name> <story-folder> --item-type subtask
   ```

4. **Verify sync status**

   Run again:

   ```
   uv run bas_spec jira-stories <spec-name> --item-type subtask
   ```

   All tasks should now show "linked" status.

**index.md Format**

After syncing, each task section in index.md will have a Jira item reference:

```markdown
#### 01-configure-budget-structure

**Jira Item**: APG-595

**Implementation**: Not Started

- [Draft] [functional-spec.md](specs/01-configure-budget-structure/functional-spec.md)
...
```

The top-level Jira item (story) can also be tracked:

```markdown
**Jira Item**: APG-594
```

**Guardrails**

- Do NOT create Jira items without user confirmation
- Do NOT update existing Jira descriptions without prompting (unless --yes)
- Tasks are created as Sub-task type, not Story or Task
- Parent is set via the `parent` field on the child sub-task (not via link types)
- Mandatory fields are copied from parent to maintain consistency
- Markdown is converted to Jira wiki markup for descriptions

**Difference from bs-jira-story-sync**

| Aspect | bs-jira-story-sync | bs-jira-task-sync |
|--------|--------------------|--------------------|
| Parent item | Epic | Story |
| Created item type | Story | Sub-task |
| `--item-type` flag | `story` (default) | `subtask` |

**Troubleshooting**

- If zaira is not found: Run `uv pip install zaira` and `zaira init`
- If link type fails: Check `zaira info` for available link types in your Jira instance
- If fields fail to copy: Some fields may require different permissions
- If Sub-task creation fails: Check that your Jira project supports the Sub-task issue type

````
