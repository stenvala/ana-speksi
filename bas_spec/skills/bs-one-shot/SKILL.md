---
name: bs-one-shot
description: Execute the entire bas-spec workflow without stopping between phases.
phase: null
---

Execute the entire bas-spec workflow from proposal through implementation
without stopping between phases.

**Input**: The user's description of what they want to build or change.

**Steps**

1. Execute bs-new (proposal)
   - After creating proposal.md, set `**Status**: Accepted` (auto-accept)
   - Set `**Generated with**: one-shot` in the header

2. Execute bs-storify (functional specs)
   - After creating each functional-spec.md, set `**Status**: Accepted` (auto-accept)
   - Set `**Generated with**: one-shot` in each functional-spec.md and index.md

3. Execute bs-techify (research + technical specs)
   - After creating each technical-spec.md, set `**Status**: Accepted` (auto-accept)
   - Set `**Generated with**: one-shot` in each technical-spec.md

4. Execute bs-taskify (task creation)
   - After creating each tasks.md, set `**Status**: Accepted` (auto-accept)
   - Set `**Generated with**: one-shot` in each tasks.md

5. Execute bs-codify (implementation)

6. Execute bs-docufy (archive + truth update)

Follow each phase's skill instructions in sequence. Do not stop between
phases unless an error occurs that requires user intervention.

**Auto-acceptance**: In one-shot mode, all acceptance gates are bypassed
because every document is immediately set to Accepted after creation.
This means no `/bs-accept` calls are needed.

**Generated with**: All key documents (proposal.md, functional-spec.md,
technical-spec.md, tasks.md, index.md) must have `**Generated with**: one-shot`
in their headers.

**Index format**: Only four artifact types carry status indicators in
index.md: proposal.md, functional-spec.md, technical-spec.md, tasks.md.
Use `[Accepted]` for these (since they are auto-accepted). All other
files are resources listed without status indicators. Do NOT use checkboxes.

**Guardrails**
- Code changes only during the codify phase
- Each phase must complete fully before the next begins
- If any phase produces results that seem wrong, pause and ask the user
- No emojis in any output or files
