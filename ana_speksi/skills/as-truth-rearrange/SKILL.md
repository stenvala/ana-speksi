---
name: as-truth-rearrange
description: Rearrange the ground truth hierarchy.
phase: null
---

Rearrange the ground truth hierarchy based on user direction.

**Input**: User's description of how truth should be reorganized.

**Steps**

1. **Read current truth structure**

   List the current hierarchy under `ana-speksi/truth/`.

2. **Understand the desired structure**

   Ask the user what changes they want:
   - Moving features under other features
   - Splitting features
   - Merging features
   - Renaming

3. **Execute reorganization**

   Move folders and update any internal references (links in markdown files).

4. **Report**

   Show the before and after structure.

**Guardrails**
- Do NOT modify any code
- Preserve all content during moves
- Update internal markdown links
- No emojis in any output or files
