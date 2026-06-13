# 0010 — Agent Operating Model: Terminal Start, Worktree Isolation, Generational Sessions

**Status:** Accepted · **§1 + "Desktop app start" rejection partially superseded by [ADR-0011](0011-return-to-desktop-app-session-start.md) (2026-06-13)** — §2 worktree isolation, §3 generational sessions, §4 shared layer remain in force.  
**Decided by:** User (2026-06-11)  
**Author / Sign-off:** System Architect  
**Technical source:** DevOps specification — Improvement Register §3 "Structural change: git worktree per context + session-cwd repair"  
**External evidence:** `docs/superpowers/improvement/2026-06-10-external-review-brief.md` + `2026-06-10-external-review-response.md`

## Context

The klartext project uses 10 specialized Claude Code agents as long-living sessions. Until 2026-06-10
the shared operating model had three structural failure modes, discovered in a single day.

**1. Shared working tree (RC5)**  
All 10 agents operated on one working tree (`/Users/thormar/klartext`). Any `git reset`, `checkout`,
or branch deletion is tree-global — it reaches uncommitted edits of every other agent regardless of
file-ownership discipline. Three data losses on 2026-06-10: OE (5 register rows, 13:46), Causal Model
Expert (3 claude.md sections, branch deleted), System Architect (4 claude.md sections, mechanism unknown).
All three recovered independently — by luck and redundancy, not protection.

**2. Sessions never starting in the repo root (RC4 variant)**  
All sessions started via the Claude desktop app from `$HOME`. Consequences:  
- Project `.claude/settings.json` (including PostCompact hooks) never loaded  
- Per-agent allowlists in `agents/<name>/start.sh` were never active  
- The compact-monitor hook chain never fired in a real session  

Forensic evidence: memory-key analysis proved no session ever ran from the repo root.
The first real hook firing happened on the terminal probe (2026-06-11).

**3. Eternal sessions compacting into unreliable summaries (False Persistence)**  
Sessions that compact indefinitely replace verified artifact state with unverified summaries.
Three independent instances of False Persistence were documented on 2026-06-10.
External review: *"Paradox formuliert: Die kompaktierte ewige Session ist die mit dem
unzuverlässigeren Gedächtnis."* A fresh session that boots from disk has exclusively
artifact-verified knowledge; a compacted session has summaries.

Root causes: RC5 (destructive git ops in shared tree) · RC4 "documented vs. actual" ·
False Persistence sub-class.

## Decision

The User decided on a new operating model with four pillars. All four were validated by a
DevOps pilot (2026-06-11); rollout to all 10 agents proceeds at natural session boundaries,
riskiest agent first.

### 1. Terminal start via central launcher

> **Superseded by [ADR-0011](0011-return-to-desktop-app-session-start.md) (2026-06-13, gated).** The
> decisive premise below — that the desktop app cannot start a session in the repo root — was empirically
> refuted on Claude.app v1.12603.1 (Environment Work Product, DevOps). The launcher is retained as the
> terminal fallback and rollback path; it is no longer the only viable entry point. The mechanics proof
> (4/4) below remains a true record of the terminal probe.

All agent sessions start via:

```
scripts/start-agent.sh <slug>
```

The central launcher carries all startup logic (cwd, allowlist injection). The 10
`agents/<name>/start.sh` remain as thin one-line wrappers — single logic home, no ten-way
drift, documented identity entry point per colleague preserved.

Allowlists are read from `agents/<name>/allowed-tools.txt` before the `cd` into the worktree,
so they are always read from the canonical main-tree version.

**Proof:** Terminal probe 2026-06-11 — mechanics 4/4 pass: cwd in repo ✓ · project settings
+ PostCompact hooks loaded ✓ · memory pinned ✓ · hook fired on real `/compact` (first time
in project history) ✓.

### 2. Worktree per colleague

Each agent gets its own isolated working directory:

```
$HOME/klartext-worktrees/<slug>/
```

Persistent home branch: `agent/<slug>`. Code lands on main only via PR gate — merge-protocol
rule 5 fulfills its sunset clause.

Lifecycle rules (DevOps domain):
- Provisioning is idempotent: exists → reuse, never reset
- Teardown via `worktree remove` + `prune`, never `rm -rf`
- Crash recovery via `worktree repair`; orphan check as health step

**Consequence:** RC5 is solved structurally. A `git reset` by one agent is physically impossible
in another agent's worktree. No rule or discipline required — the strongest enforcement is the
kind that needs no rule.

**Architecture principle:** "Isolate code, share comms/memory/audit."

### 3. Generational sessions as the normal mode

*Colleague* = `claude.md` + domain knowledge + memory + role.  
*Session* = a working day.  
*Generational change* = end of day, not end of identity.

Proactive restart replaces compaction:

1. Pre-Restart ritual (formerly Pre-Compact) — artifact-verified, well before context threshold
2. Session ended by user
3. Fresh session booted via launcher into the same worktree
4. Fresh session reads disk (claude.md + pinned memory) — exclusively artifact-verified state

**Pilot proof:** DevOps generation change 2026-06-11. Successor seed: full pre-restart ritual
+ handoff note in own inbox. New session booted via launcher; channel proof artifact-verified
(inbox message received and read). First colleague with real cwd, firing hooks, active allowlists
and worktree isolation.

WIP-commit discipline: with an own worktree, frequent small commits are safe (no shared tree
risk). The volatile in-session layer shrinks from days to minutes.

### 4. Shared layer centrally pinned

Shared infrastructure lives under `~/.claude/klartext-team-memory/`:

| Component | Purpose |
|---|---|
| Auto-memory (team blackboard) | Pinned via `autoMemoryDirectory`; content copied from original (rollback); bootstrapped in `setup.sh`; CI-validated on fresh runner |
| File inbox (`inbox/<slug>/`) | `scripts/inbox.sh send\|read\|unread`; replaces app messaging; user nudges recipient — same semantics as `send_message`, no unsolicited delivery |
| Compact log | Centrally pinned; one launchd instance covers all worktrees; branch field identifies which agent compacted |

App messaging (`send_message`, session list) is not used: terminal sessions do not appear
in the app session list and cannot receive app messages. The file inbox is the durable
substitute with equivalent semantics.

## Rejected Alternatives

The decision record includes rejected paths as first-class method knowledge (user requirement, 2026-06-10).

| Alternative | Verdict | Reason |
|---|---|---|
| **Eternal sessions (never restart)** | Rejected | Every compaction replaces verified history with an unverified summary — the False Persistence sub-class. The longer a session lives, the more its "memory" diverges from artifact state. External reference: Paperclip implements "persistent agents" as disk state loaded into fresh context per heartbeat, not eternal sessions. Identity is durable; sessions are not. |
| **Desktop app start** | ~~Rejected~~ **Superseded by [ADR-0011](0011-return-to-desktop-app-session-start.md)** | *Original 2026-06-11 reasoning, preserved as the record:* "Structurally impossible upstream. Folder selection sets the project association but never changes shell cwd. GH issues #56688 / #26287 / #60151 / #60099 confirm: no `--cwd` flag, no shipped default-directory setting. Live test 2026-06-10 (fresh app session, folder actively selected via picker): shell remains in `$HOME`." **Refuted 2026-06-13 on v1.12603.1:** the app passes cwd through (`startSession({cwd})`); the 2026-06-10 observation came from the wrong button (`📁+` additional-dir instead of the primary working-directory picker) + TCC, not a structural limit. See ADR-0011. |
| **Agent Teams as team memory** | Rejected | Agent Teams directories are ephemeral coordination infrastructure, not a persistence layer. Using them as a team blackboard is tool misuse — the content has no persistence contract. |
| **Native app worktrees for long-lived agents** | Rejected / Superseded by self-managed worktrees | The app creates native worktrees for ephemeral sessions. For long-lived agents they produce diverging `claude/` branches and have no lifecycle discipline (idempotent provisioning, crash recovery, orphan cleanup). Self-managed worktrees under `$HOME/klartext-worktrees/<slug>/` keep lifecycle control in our hands — standard git, not a workaround. |
| **Shared working tree with ritual protection** | Rejected / Superseded by worktree isolation | Three data losses in one day despite mature rituals and a passed merge-protocol stress test on the same day. External review: *"Das Grundproblem ist nicht Disziplin, sondern Physik"* — tree-global git operations violate file-ownership rules without any agent misbehaving. Ritual enforcement is permanently inferior to physical isolation per our own enforcement hierarchy (mechanical > ritual). |
| **Hybrid: high-risk agents terminal, advisors in app** | Superseded by uniform terminal | Proposed as a fallback if the file inbox proved unworkable. Discarded after the inbox was validated (PR #70, 5 infra tests passing). Uniform terminal with file inbox is simpler, consistent, and avoids split enforcement. |

## Consequences

**Positive:**
- RC5 solved structurally — cross-agent data destruction is physically impossible
- Settings, hooks, and allowlists are real for the first time; enforcement is mechanical
- PostCompact hook chain proven end-to-end (first real firing: 2026-06-11)
- Fresh sessions load exclusively artifact-verified state; False Persistence dissolved by design
- WIP commits are safe and cheap; volatile layer shrinks from days to minutes
- Rollout playbook documented and proven via DevOps pilot

**Negative / Risks:**
- Terminal sessions are not visible in the app and cannot receive app messages — file inbox covers semantics at the cost of slightly more friction compared to `send_message`
- Fresh sessions require a wake prompt before they act — the successor seed or launcher must include the initial task (pilot finding: a fresh session waits for the user's first message)
- Mixed mode during rollout: the 9 remaining agents migrate at natural endpoints; interim period has heterogeneous session environments
- **Stop-and-wait throughput:** every inbox handover waits for a user nudge before the recipient acts. Effective throughput in multi-agent runs is a function of user availability, not agent readiness. In sequential chains (e.g. 4 agents in a DELETE-404-style run), each step adds a human relay delay. This is a known, accepted trade-off: the user as channel is a deliberate safety invariant, not an accident. Evidence: Hannibal's retro input on the DELETE-404 run (2026-06-12). Mitigation: keep chains short; batch handoffs where semantics allow.

**Ongoing obligations:**
- `scripts/start-agent.sh` is the single startup logic home; allowlist or cwd changes go through the launcher, not individual wrappers
- Worktree lifecycle (provision, teardown, repair, orphan check) is DevOps domain
- File inbox semantics are identical to `send_message` semantics: user nudges the recipient; no unsolicited delivery without the user as channel
