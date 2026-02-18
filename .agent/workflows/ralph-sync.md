---
description: Synchronize project state using Ralph Patterns (prd.json & progress.txt)
---

# 🤖 Ralph Sync Workflow

Use this workflow after every major task completion to ensure the AI's "Long Term Memory" and "Project State" are perfectly synchronized.

## Steps

1. **Scan `prd.json`**:
   - Locate the current active User Story.
   - Update `passes` to `true` if the acceptance criteria are met.
   - Add technical `notes` about the implementation.

2. **Update `progress.txt`**:
   - Append a new log entry with the current date.
   - Categorize updates: `[FEATURE]`, `[FIX]`, `[SYSTEM]`, `[DISCOVERY]`.
   - Document any critical lessons learned or gotchas discovered.

3. **Verify Git State**:
   - Ensure all changes are staged and committed with a prefix matching the PRD ID (e.g., `EP-005: SaaS Refactor`).

4. **Self-Correction**:
   - If a task failed, update the `notes` in `prd.json` with the blocker and create a new follow-up story if necessary.
