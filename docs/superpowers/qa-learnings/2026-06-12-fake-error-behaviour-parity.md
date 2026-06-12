# QA Gap: 2026-06-12 — Fake diverged from real repo on the error path

## What happened

While writing the DELETE-404 contract test (PR #82), a PATCH/DELETE symmetry test run
through the real service chain revealed that `FakeNarrativeUnitRepository.update()` was
**lenient** — it stored unconditionally and returned, even for an ID that was never added.
The real `SupabaseNarrativeUnitRepository.update()` is **strict**: it raises
`NarrativeUnitNotFoundError` on an empty PostgREST result (`if not result.data: raise ...`).

The fake had been made strict for `remove()` (DELETE-404 work) but `update()` was left
lenient — an asymmetry inside the same fake, while the real repo treats both verbs the same.
No test caught it because nothing exercised `update()` on an unknown ID through a path that
relied on the fake's not-found behaviour.

Discovered: during QA's own contract-test work (not production) — the symmetry test went RED.

## Missing test

`test_patch_and_delete_unknown_unit_are_symmetric_404` (router/contract, real service chain)
exposed it; guards added so it cannot regress:
- `test_update_unit_raises_not_found_for_unknown_id` (Service)
- `test_update_raises_not_found_for_unknown_id` (`@pytest.mark.integration`, real repo)

→ Category: **4 — Fake Contract Completeness** (with a Category 2 error-path angle)

## Why did qa-review miss this?

Known category, **too-narrow trigger.** Category 4 only watched for *silent placeholder
return values* (`return 0/[]/None/False`). A fake that returns a real value but **skips a
`raise` the real repo performs** is an equally silent divergence — the wording did not cover
behavioural (exception) parity, only value parity. The existing 2026-06-10 learning had even
noted the real repo's `update`-strict / `remove`-lenient asymmetry, but the fake-level mirror
of that asymmetry was never checked.

## Consequence

→ `~/.claude/skills/qa-review/qa-categories.md` — Category 4 extended with an
  **"Error-behaviour parity"** trigger: open the real `SupabaseXRepository` method, enumerate
  its `raise` statements, and require the fake to raise the same exceptions on the same
  conditions. Asymmetry within one fake (one method strict, another lenient) is a red flag.
→ Semgrep: **not cleanly applicable** — this is a cross-file semantic comparison (fake `raise`
  set vs. real-repo `raise` set). A blanket "fake mutating method must contain a `raise`" rule
  would false-positive on legitimately lenient reads (`find_by_id` returning `None`). Enforced
  via category wording, not a static rule. Revisit if this recurs (see pattern note below).

## Pattern note

First occurrence of *fake-vs-real behavioural divergence*. The 2026-06-10 entry is about the
contract-test pattern (real service vs fake service), a different shape. Not yet at the 3×
threshold that would justify a stronger/Semgrep enforcement — re-evaluate on the next recurrence.
