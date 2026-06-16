# Environment Work Product: Claude Code Desktop App

> **Scope.** Our version-bound knowledge about the **Claude Code desktop app** as a development environment for
> the agent sessions — what it does, how it loads our settings, and what operating decisions depend on that.
> **Out of scope.** The governing practice (`../practices/environment-knowledge.md`); the operating decision
> *whether* to (partly) return to the app (SA + OE + user; ADR-0010 revision); product code.
> **Anti-pattern guarded.** A stale app fact silently driving a decision (RC4) — the exact failure of the
> superseded ADR-0010 premise below.
> **Language.** English — documentation-language rule.
>
> **Status:** **frozen v2** (2026-06-13) — re-frozen after an **auto-memory fact-cluster** was added (the tested
> `autoMemoryDirectory` override fact + the per-cwd / trusted-only constraints + Canary **(e)** + the team-memory
> dependency row; lab-verified, see §Version-binding). **Four-eyes complete:** empirical content owned/verified by
> **DevOps** (freeze sign-off 2026-06-13); **form + home reviewed and signed off by OE** 2026-06-13. **v1** froze
> the cwd / settings / `/clear` / enforcement facts the same day; **v2** adds the memory cluster. Holds for app
> **v1.12603.x** only; re-run the **Canary** on any app update. (Freeze version lives here, not in the `method.md`
> register — the register stores only non-derivable facts.)

## Version-binding

- **Resource:** Claude Code desktop app (Local mode).
- **Version / build:** **v1.12603.1**, Build **3df4fd**.
- **Observed:** 2026-06-13 by **DevOps**, against an isolated clone (`~/klartext-apptest`, on `main`).
- **Holds for this version only.** On any app update, run the **Canary** below before relying on these facts.
- **Auto-memory cluster:** verified 2026-06-13 by **DevOps** in an isolated lab (`~/memlab`: throwaway git
  projects with sentinel `MEMORY.md` files), app **v1.12603.x** + Claude Code CLI **2.1.177**, via fresh app
  sessions (real trust dialog) driven by the user. Same Resource (the app), same day; bound to this app family.

## Facts

### Tested — freezable

- **Primary cwd = repo** ✓ — via the **working-directory picker** (the *"thormar"/folder-name → „Ordner
  öffnen…"* chip), **not** the `📁+` button (that only adds an *additional dir*; primary stays Home — the
  cause of every earlier failed attempt).
- **Project `settings.json` + hooks load** ✓ — `/compact` fired the PostCompact hook; log line
  `2026-06-13T08:44:10 | manual | main` with the branch correctly resolved ⇒ `CLAUDE_PROJECT_DIR` was set for
  the hook.
- **Folder remembered across sessions** ✓ — a new session shows the folder pre-selected (`📁 klartext-apptest`
  + `main | Worktree` toggle). (#46176 does **not** apply to v1.12603.1.)
- **`/clear` works in the app** ✓ — no skill-picker; resets context (the false-persistence fix: `/clear`
  *discards*, vs `/compact` which summarizes).
- **`/clear` fires `SessionStart`** ✓ — the app reports it as **`source=startup`** (not `clear`) and **lazily**
  (only on the next prompt). **3/3 reproduced**, also with an open/committed diff.
- **Allowlist enforcement is project-local** ✓ — `semgrep --version` (matches `Bash(semgrep*)`) ran with **no
  prompt** ⇒ the allowlist loaded; a non-matched command (the venv absolute path `…/api/.venv/bin/semgrep`)
  raised a prompt badged **`Projekt (lokal)`** ⇒ the project policy is the active layer, **deny-by-default**.
  This is prompt-level behaviour (upgraded from *inferred* on DevOps' freeze sign-off, 2026-06-13).
- **Project-scope `autoMemoryDirectory` is honored and overrides user-global** ✓ — an `autoMemoryDirectory` in
  the **committed** `.claude/settings.json` (the `~/`-form expands) is read by the app **after the folder's
  trust dialog** and **wins over** the user-global `~/.claude/settings.json` (precedence **project > user**).
  Lab `~/memlab`, **3 cases** reproduced: (1) project-scope pin honored; (2) removing the user-global keys
  isolates a foreign project; (3) the committed pin is self-sufficient with no user-global key. **Refutes** the
  schemastore schema's *"ignored if set in checked-in project settings, for security"* claim — the first-party
  docs (honored-after-trust) are correct.

### Observed, untested — carry, do not rely on

- **Native Worktree toggle** present next to the folder — **observed, not tested** (we used external worktrees
  under `~/klartext-worktrees/<slug>/`, which are 1:1 compatible: point the picker at them).
- **"Änderungen übernehmen"** makes the app **auto-create a branch + commit** (`chore/…`), **not on `main`** —
  observed; relevant for the PR workflow (don't expect work to land on `main` directly).

### Inferred — not yet proven by behaviour

- _None for v1 — every load-bearing fact above is **tested** or explicitly **observed-untested**._

### Constraints / dormant risks

- **Environment must be "Local"** — the app knows Local / Cloud / Remote Control; only **Local** sees
  `~/klartext-worktrees` + `.claude/settings.json`. Invariant for agent sessions. (Session-list filters —
  status / project / group-by — are pure view, no effect.)
- **TCC (macOS privacy):** Home-root is fine; **`~/Desktop`, `~/Documents`, `~/Downloads` need a macOS grant**
  for the app. Keep worktrees out of those unless granted.
- **Managed-Settings layer** (`serverManagedSettings` / MDM, "first-wins") **exists but is NOT active** today
  (our project hooks loaded + fired). The single place a future team-admin policy could centrally override our
  allowlist/hooks. Keep in mind.
- **Auto-memory default is per-cwd, NOT per-repo** — an *unset* `autoMemoryDirectory` resolves to
  `~/.claude/projects/<sanitized-cwd>/memory/`; **git worktrees do NOT share it** (each worktree is a different
  cwd). A shared team blackboard therefore needs an **explicit committed pin** (byte-identical in every
  worktree). Contradicts the app docs' *"worktrees share one default"* wording — measured, not assumed.
- **Committed memory pin honored only in TRUSTED worktrees** — an untrusted worktree silently ignores the pin
  and falls back to the per-cwd default (a lonely store, not the blackboard). Same trust gate as the hooks;
  accept it on first open. This is the new fragility introduced by moving the pin off user-global.

## Canary — manual post-update checklist

Run **after every app update** (the app cannot be scripted — this is by hand). If **any** step breaks, this
Work Product is **presumed invalid**: the app-path and the `/clear` ritual are at risk until re-verified.

- [ ] **(a) cwd** — new session, working-directory picker on a repo → `pwd` = repo root (**not** `$HOME`).
- [ ] **(b) settings load** — `/compact` → PostCompact hook writes a compact-log line (= `settings.json` loaded).
- [ ] **(c) `/clear` reset** — `/clear` → the next prompt fires `SessionStart` (`source=startup`).
- [ ] **(d) enforcement active** — a non-allowlisted command prompts (badge `Projekt (lokal)` = project policy
  is the active, deny-by-default layer). Covers the allowlist, not just hook loading.
- [ ] **(e) team memory pin honored** — a session in a repo with a committed `autoMemoryDirectory` recalls
  **that** directory's `MEMORY.md` (sentinel check), **not** the user-global one — after trust. Confirms the
  project-scope pin still beats user-global (else the team blackboard silently shatters per-cwd).

## Dependency chain — what hangs on these facts

| Decision / mechanism | Depends on |
|---|---|
| Operating decision "App instead of Terminal" | (a) cwd + (b) settings load |
| Daily `/clear` generation-change ritual | `/clear` reset + Canary (c) |
| Automatic identity reload (`agents/<name>/claude.md`) | `SessionStart` hook with a matcher that **includes `startup`** (the app reports `/clear` as `startup`) |
| Enforcement (allowlists / hooks) | `settings.json` loading (= correct cwd) |
| Worktree placement | TCC: keep worktrees out of `~/Desktop` / `~/Documents` / `~/Downloads` |
| Shared team auto-memory blackboard (all worktrees) | committed `autoMemoryDirectory` honored (after trust) **and** per-cwd default NOT shared ⇒ explicit pin required (PR #99) |

## Superseded

- **ADR-0010 premise — "cwd in der App strukturell unmöglich"** → **REFUTED** for v1.12603.1. Root error:
  concluded *"structurally impossible upstream"* from **one** black-box test that used the **wrong button**
  (`📁+` instead of the primary working-directory picker); the app code in fact passes cwd through
  (`startSession({cwd})`). The migration was **correct at the time** (old eternal-session-from-Home model,
  pre-April redesign) — but **no longer alternativlos**. **ADR-0010 revision is SA's domain** (briefing
  pending); this Work Product only records the empirical refutation.
