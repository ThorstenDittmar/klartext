---
name: systematic-debugging
description: Use when debugging any bug or unexpected behavior. Loads superpowers:systematic-debugging and appends a qa-retro step to capture any test gaps discovered during debugging.
---

# Systematic Debugging

## Step 1: Load superpowers debugging skill

Before proceeding, invoke the `superpowers:systematic-debugging` skill.
All rules defined there apply without exception.

## Step 2: QA Retrospective (after the fix)

After the bug is fixed and the fix test is green:

**Ask:** should the QA agent have written a test for this during the original implementation?

- **Yes:** invoke `qa-retro` to document the blind spot and update the QA system.
- **No (e.g. environment issue, data issue, not a code gap):** no action needed.

The `qa-retro` step is not optional when the answer is yes — it is how the QA system
learns. A bug fixed without updating the QA system means the same bug can happen again.
