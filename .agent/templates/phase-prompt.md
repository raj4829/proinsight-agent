# Phase Prompt Template

Template for `.planning/phases/XX-name/{phase}-{plan}-PLAN.md` - executable phase plans.

**Naming:** Use `{phase}-{plan}-PLAN.md` format (e.g., `01-02-PLAN.md` for Phase 1, Plan 2)

---

## File Template

```markdown
---
phase: XX-name
type: execute
domain: [optional - if domain skill loaded]
---

<objective>
[What this phase accomplishes - from roadmap phase goal]

Purpose: [Why this matters for the project]
Output: [What artifacts will be created]
</objective>

<context>
@.planning/PROJECT.md
@.planning/ROADMAP.md
[If discovery exists:]
@.planning/phases/XX-name/DISCOVERY.md
[Relevant source files:]
@src/path/to/relevant.ts
</context>

<tasks>

<task type="auto">
  <name>Task 1: [Action-oriented name]</name>
  <files>path/to/file.ext, another/file.ext</files>
  <action>[Specific implementation - what to do, how to do it, what to avoid and WHY]</action>
  <verify>[Command or check to prove it worked]</verify>
  <done>[Measurable acceptance criteria]</done>
</task>

... (truncated for brevity)
</tasks>
...
```
