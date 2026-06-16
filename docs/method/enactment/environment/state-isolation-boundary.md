# Environment Work Product: State-Isolation Boundary (klartext ↔ co-resident projects)

> **Scope.** Where klartext's state physically lives, classified by the **project-scoped vs. global** boundary
> that keeps it isolated from a **co-resident project on the same machine** (e.g. semAIt). The basis for the
> #3a "user-global-state isolation" of the method/product cut.
> **Out of scope.** The governing practice (`../practices/environment-knowledge.md`); **#3b skill-distribution
> isolation** (the shared `~/.claude/skills/` surface — cut-dependent, **F3**); semAIt's own setup; product code.
> **Anti-pattern guarded.** Project-belonging state silently living in a **shared global path** → it bleeds into
> a co-resident project (or is overwritten by it), is unversioned, and has no clear owner (RC4 "documented vs.
> actual" + the wrong-home class).
> **Language.** English — documentation-language rule.
>
> **Status:** **living** — audited 2026-06-16 by **OE** (F1 #3a). One target-state row is **pending a DevOps
> mechanic** (the `launch.json` relocation, see the table). Re-run the **Canary** after that lands and on any
> Claude-app update. Owner OE (form + the boundary call); empirical layout audited by OE, mechanics = DevOps.

## Version-binding

- **Resource:** the `~/.claude/` user-state layout under the Claude Code desktop app family **v1.12603.x**
  (companion to `claude-code-app.md`, which establishes that the app loads **project-scoped** `.claude/`
  config when the session's selected folder is the project).
- **Observed:** 2026-06-16 by OE, against `~/.claude/` on this machine.
- **Holds while** the app keeps loading project-scoped `.claude/` + the autoMemory project-pin (cutover
  2026-06-15) stands. On an app update, re-run the Canary.

## The boundary — five classes

| Class | What | Files / paths | Isolation from a co-resident project |
|---|---|---|---|
| **Project-scoped** (belongs in the repo / project `.claude/`) | klartext config + the repo itself | `.claude/settings.json`, `.claude/launch.json` *(target — see below)*, hooks, the repo | **By project folder** — each project has its own; no collision |
| **Global-but-named** (deliberate, isolated) | the team substrate | `~/.claude/klartext-team-memory/` (autoMemory pin + inbox + MEMORY.md) | **klartext-named** + project-pinned (user-global keys removed at the 2026-06-15 cutover); a co-resident project pins its **own** dir. Durability = the F2 substrate backup |
| **Shared → isolate at distribution** | synced ritual skills | `~/.claude/skills/` (repo = SoT via `klartext skills sync`) | **Shared today** → **#3b / F3** (skill-distribution isolation; needs the L3 extraction first) |
| **Personal / machine-local** (not project state) | accumulated permission grants, env | `~/.claude/settings.local.json`, local env | Not project-belonging; a co-resident project accumulates its **own**. No action |
| **External, unchanged** (general-purpose) | downloaded plugins / standards | `~/.claude/plugins/` (superpowers, …), Essence Kernel/Language | **Referenced, never vendored**; a co-resident project gets **no write access** → stays byte-identical for all. See [[project-superpowers-external-dependency]] |

## The rule (autonomy vs. coherence, made explicit)

- **Each project owns its project-scoped state** in its own folder; co-residence is isolated **by the project
  folder**, not by per-file coordination.
- **Global state is legitimate only when it is either** (a) deliberately named per-project and pinned
  (`klartext-team-memory`), or (b) general-purpose and write-protected (`plugins/`). Anything else that is
  project-belonging but globally placed is **misplaced** and must move project-scoped.
- **semAIt seed:** semAIt seeds from klartext's **post-cut** state but must **re-point** its project-scoped
  config (autoMemory pin → its own memory dir; its own `.claude/launch.json`) — it must **not inherit
  klartext's pin or launch config**. It gets no write access to klartext's named-global or external state.

## Open / target state

- **`launch.json`** is currently at the global `~/.claude/launch.json` (a leftover from sessions historically
  started with the selected folder = `$HOME`). Per the Claude-app design it belongs at the **project**
  `klartext/.claude/launch.json` (portable args). **Target state pending the DevOps mechanic** (briefing filed
  2026-06-16): create the portable project-scoped file + remove the global leftover + the cutover `.bak`. Until
  then this row is "documented vs. actual" — the table's *Project-scoped* `launch.json` is the **target**.

## Canary (falsifiable — re-run after the launch.json fix + on app updates)

1. No project-belonging config is misplaced globally:
   `grep -rl '/Users/thormar/klartext' ~/.claude/*.json` → after the fix, returns **nothing** except
   `settings.local.json` (personal permission grants, expected).
2. The autoMemory pin is project-scoped: `~/.claude/settings.json` carries **no** `autoMemoryDirectory`
   (cutover), while the committed `.claude/settings.json` pins `~/.claude/klartext-team-memory`.
3. `klartext/.claude/launch.json` exists with **portable** (relative) args; `~/.claude/launch.json` is gone.

## Dependency chain

- **Upstream:** the app's project-scoped `.claude/` loading (`claude-code-app.md`); the autoMemory cutover
  (`[[project-automemory-migration-status]]`).
- **Downstream blast radius:** the `verify` skill / Claude_Preview (reads `launch.json`); the semAIt seed; the
  F2 substrate backup (covers the named-global team substrate); **#3b/F3** (the shared skills surface).
