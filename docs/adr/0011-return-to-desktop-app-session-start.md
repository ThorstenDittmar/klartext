# 0011 — Return to the Desktop App for Session Start (Gated)

**Status:** Accepted (Gate) — decision made, execution conditional on the Gate below
**Decided by:** User (2026-06-13), direction set; conditions authored by System Architect
**Author / Sign-off:** System Architect
**Supersedes:** ADR-0010 §1 "Terminal start via central launcher" and the rejected alternative "Desktop app start". ADR-0010 §2 (worktree isolation), §3 (generational sessions) and §4 (shared layer pinned) remain in force and are carried forward unchanged.
**Evidence:** `docs/superpowers/improvement/environment/claude-code-app.md` — Environment Work Product, **frozen v1**, DevOps-verified 2026-06-13, version-bound to Claude.app **v1.12603.1** (Build 3df4fd).

## Context

ADR-0010 mandated **terminal start via `scripts/start-agent.sh`** as the only viable session
entry point. Its decisive justification was that the desktop app could not start a session in the
repository root — recorded in the rejected alternative "Desktop app start" as *"structurally
impossible upstream … no `--cwd` flag, folder selection never changes shell cwd."* That conclusion
was drawn from a single black-box test on 2026-06-10.

On 2026-06-13 DevOps re-tested the app empirically on **v1.12603.1** against an isolated clone
(`~/klartext-apptest`). The result, frozen as an Environment Work Product, refutes the premise:

- **Primary cwd = repo** ✓ — via the **working-directory picker** (the folder-name chip →
  *„Ordner öffnen…"*), **not** the `📁+` button (which only adds an *additional* dir and leaves the
  primary at `$HOME` — the cause of every earlier failed attempt).
- **Project `settings.json` + hooks load** ✓ — `/compact` fired the PostCompact hook with the branch
  correctly resolved (⇒ `CLAUDE_PROJECT_DIR` was set).
- **Allowlist enforcement is project-local, deny-by-default** ✓ — an allowlisted command ran without
  a prompt; a non-matched command prompted with badge `Projekt (lokal)`.
- **`/clear` works and fires `SessionStart`** ✓ — reported as `source=startup`, lazily on the next prompt.

The app passes cwd through (`startSession({cwd})`). The earlier observation "folder selected, still
`$HOME`" had two real causes: (a) the wrong button (additional dir, not primary picker), and
(b) TCC — `~/Desktop`/`~/Documents`/`~/Downloads` need a macOS file-access grant; Home-root does not.

**Important framing (no fault):** the ADR-0010 migration was **correct at the time** — it was taken
under the old eternal-session-from-Home model (pre-April redesign), where the observed behaviour was
real. It is **no longer alternativlos**, not "was always wrong." This ADR re-opens only the
session-start mechanism; it does not relitigate the operating model.

## Decision

**The agent sessions return to the Claude desktop app for session start, once the Gate below is met.**

Rationale:
- The decisive blocker for the app path (no repo cwd ⇒ no settings/hooks/allowlists) **no longer
  exists** on v1.12603.1. The four mechanics ADR-0010 demanded of terminal start — cwd in repo,
  settings + hooks loaded, allowlists active, hooks firing on real lifecycle events — are now all
  reproducible **in the app**.
- The app additionally restores ergonomics the terminal path gave up (session list, in-app UX) and
  supports the `/clear` generation-change ritual natively.
- **Migration cost is low and reversible:** the worktree layout, branches, shared memory, and file
  inbox (ADR-0010 §2/§4) are environment-agnostic — both terminal and app point the same picker at the
  same `~/klartext-worktrees/<slug>/`. Switching entry point does not touch the isolation guarantees.

This decision changes **only the session-start entry point** (ADR-0010 §1). It explicitly does **not**
change:
- **§2 Worktree per colleague** — isolation that solved RC5 (cross-agent data destruction) stays. The
  app points its picker at the existing `~/klartext-worktrees/<slug>/`; no native app worktrees for
  long-lived agents (still rejected, ADR-0010).
- **§3 Generational sessions** — fresh-session-from-disk over eternal compaction stays. In the app the
  generation change is `/clear` (discards context) rather than ending the OS process; the Pre-Restart
  ritual is unchanged.
- **§4 Shared layer pinned** — auto-memory, file inbox, compact log stay exactly as pinned. **The file
  inbox remains the cross-agent channel** under this ADR — see Open Questions.

## Gate — conditions for a clean return

The return is **blocked** until every condition is satisfied. This list is the basis of the DevOps
briefing.

| # | Condition | Owner | Status |
|---|---|---|---|
| G1 | **`SessionStart` hook that loads `agents/<name>/claude.md`** from the worktree path, with a matcher that **includes `startup`** (the app reports `/clear` as `source=startup`, lazily on next prompt). Today `settings.json` has only a PostCompact hook — identity reload on session/`/clear` is **missing**. | DevOps | **OPEN — blocking** |
| G2 | **Local-mode invariant** — sessions run only in the app's **Local** environment. Cloud / Remote Control do not see `~/klartext-worktrees` or `.claude/settings.json`. To be asserted as an operating invariant (and, where possible, a startup/health check). | DevOps + OE | OPEN |
| G3 | **TCC placement** — worktrees stay out of `~/Desktop`/`~/Documents`/`~/Downloads` (those need a macOS grant). `~/klartext-worktrees/<slug>/` (Home-root) is fine and already in use. Document as a placement rule. | DevOps | Met by current layout; document |
| G4 | **Allowlist patterns match the real invocation form** — `Bash(semgrep*)` covers the bare call but **not** the real `api/.venv/bin/semgrep` path the pre-commit `entry` uses (a **relative**, repo-rooted path — not absolute), so the genuine invocations would prompt. Refine allowlist patterns to the actual (venv-relative) form, anchored — **no leading wildcard** (`Bash(*…*)` would un-anchor the pattern and weaken deny-by-default; rejected). An infra test ties the pattern to the pre-commit `entry` so the two cannot drift. | DevOps + SA | **DONE** — PR #96 (SA sign-off 2026-06-13, option A: relative-only, anchored) |
| G5 | **Version binding + Canary** — these facts hold for **v1.12603.1 only**. The manual Canary in the Work Product must be re-run after **any** app update; a failing Canary presumes this ADR's premise invalid until re-verified. | DevOps | Standing obligation |
| G6 | **Managed-Settings / MDM watch** — the `serverManagedSettings` (MDM, "first-wins") layer is **inactive today** but is the single place a future central policy could override our allowlist/hooks. Record as a risk/watch, not a blocker. | SA | Watch (non-blocking) |

**Sequencing (strictly serial):** this ADR-gate first → then DevOps builds G1/G4 (and asserts G2/G3)
→ then OE delivers the operating-model update + the `team.yaml` app/terminal flip. No step starts
before the prior one lands.

## Open Questions

- **Cross-agent messaging in the app.** ADR-0010 §4 moved to the **file inbox** because terminal
  sessions were invisible to app messaging. Back in the app, in-app messaging (`send_message`, session
  list) may be available again. This ADR **keeps the file inbox** as the channel — it is durable,
  worktree-independent, and CI-tested — and does **not** re-enable app messaging by default. Whether to
  layer app messaging back on top is a **separate decision (SA + OE + user)**, out of scope here.
- **`/clear` vs. process restart as the generation boundary.** ADR-0010 §3 framed the generation change
  as ending the session process. In the app, `/clear` discards context within a living process and fires
  `SessionStart`. Functionally equivalent for the False-Persistence guarantee (fresh state from disk),
  but the operating ritual wording is OE's to update.

## Consequences

**Positive**
- The single hard blocker behind the terminal mandate is gone; the app path is verified, not inferred.
- Native session list and in-app UX return; `/clear` gives a first-class generation-change ritual.
- All ADR-0010 safety guarantees (worktree isolation, generational sessions, shared/pinned layer)
  carry forward untouched — this is an entry-point swap, not an operating-model change.

**Negative / Risks**
- **Hard dependency on G1:** without the `startup`-matcher `SessionStart` hook, an app session boots
  **without** loading its `agents/<name>/claude.md` — identity drift. The return must not proceed before
  G1 lands. (This is why the gate is serial.)
- **Version-bound (G5):** the decision rests on v1.12603.1 behaviour. An app update can silently break
  cwd/hooks/`/clear`; the manual Canary is the only detector and depends on human discipline.
- **Allowlist mismatch (G4):** until patterns match the venv-absolute form, the real pre-commit
  invocations prompt — friction that can erode the deny-by-default posture if worked around.
- **MDM latent override (G6):** dormant today; a future managed-settings policy is the one layer that
  could centrally disable our hooks/allowlist without our consent.

**Ongoing obligations**
- The Environment Work Product is the **single source** for these app facts; this ADR cites it rather
  than copying it. When the Canary fails, this ADR's "Accepted" status is **presumed suspended** until
  the Work Product is re-frozen for the new version.
- `scripts/start-agent.sh` and the per-agent `start.sh` wrappers are **not deleted** — they remain the
  terminal fallback while G1–G4 are pending and as the documented rollback path.

## Rollback

Reversible at low cost: re-select terminal start via `scripts/start-agent.sh` (kept intact). The
worktrees, branches, shared memory, and inbox are unchanged by the entry-point choice, so a rollback
touches only how a session is launched — no data migration.
