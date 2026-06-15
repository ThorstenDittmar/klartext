---
name: qa-retro
description: Use when a bug is found that should have been caught by tests. Guides a structured retrospective, writes the missing test, identifies the blind spot, and documents a learning entry. Called automatically from systematic-debugging and the tdd bug-fix flow.
---

# QA Retrospective

A bug reached manual testing or production despite all checks passing.
This means the QA agent has a systematic blind spot. Make it visible and fix it.

## When to Use

- Automatically: at the end of a `systematic-debugging` session when a bug is fixed
- Automatically: at the end of a `tdd` bug-fix when a bug should have been caught earlier
- Manually (`/qa-retro`): when a bug is reported by a user or observed in production

## Step 1: Describe what happened

Answer these questions briefly:
1. What failed? (behavior, not implementation — "scope returned None instead of []")
2. When was it discovered? (manual test / user report / production)
3. Which test should have caught it? (category: Domain / Service / Repository / Router / Composition)

## Step 2: Write the missing test (RED)

Write the test that would have caught this bug. Follow TDD — the test must fail now.

```bash
pytest api/tests/test_<relevant_file>.py::test_<name> -v
```
Confirm: FAILED. Do not proceed until the test fails for the right reason.

## Step 3: Fix the code (GREEN)

Make the minimal change to pass the test. Do not add unrelated changes.

```bash
pytest api/tests/ -m "not integration" -v
```
Confirm: all tests PASS.

## Step 4: Identify the blind spot

Answer: why did the QA agent not write this test during the original implementation?

Choose one:
- **Unknown category** — the QA agent's 5 categories don't cover this type of test
- **Known category, wrong trigger** — the category exists but the trigger condition missed this case
  (example: composition tests only triggered on Slot/Relation diffs, not on CausalModel-only diffs)
- **Known category, agent failure** — the trigger was correct but the agent missed the case

## Step 5: Update the QA system

Based on the blind spot category:

| Blind spot type | Action |
|---|---|
| Unknown category | Add new category to `~/.claude/skills/qa-review/qa-categories.md` |
| Wrong trigger condition | Fix trigger in `qa-categories.md` or `domain-composition-rules.md` |
| Agent failure (repeated) | After 3+ failures in same category: sharpen the rule wording |
| Statically checkable pattern | Add new Semgrep rule to `.semgrep/rules/qa/` — filename: `qa-<name>.yaml` |

## Step 6: Write the learning entry

Save to `docs/superpowers/qa-learnings/YYYY-MM-DD-<short-description>.md`:

```markdown
# QA Gap: YYYY-MM-DD — <short description>

## What happened
<1-2 sentences: what failed, when discovered>

## Missing test
`<test function name>`
→ Category: <which of the 5 categories>

## Why did qa-review miss this?
<specific reason — which trigger condition was wrong or missing>

## Consequence
→ <what was changed: file name + what was updated>
→ Semgrep: <new rule if applicable, or "not applicable (semantic pattern)">
```

## Pattern recognition

After writing the entry, check `docs/superpowers/qa-learnings/` for the same category
appearing 3 or more times. If yes: the rule wording needs to be stronger, or a new
Semgrep rule is needed. Do not defer this — fix it now.

---

## Boundary reminder

All changes made in this skill stay within QA domain:
`api/tests/`, `.semgrep/rules/qa/`, `docs/superpowers/qa-learnings/`, `~/.claude/skills/qa-*/`.

If a pattern requires a change outside this domain (e.g. a new CI step in `qa.yml`,
a dependency in `api/pyproject.toml`, or an arch-layer Semgrep rule), do not make
the change. Write a DevOps Briefing or brief System Architect instead.
See `qa-review/SKILL.md` → "QA Domain Boundaries" for the full protocol.
