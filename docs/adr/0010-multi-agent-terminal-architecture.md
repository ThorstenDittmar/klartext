# 0010 — Multi-Agent Terminal Architecture: Worktree-per-Agent + File Inbox + Central Compact-Log

**Status:** Accepted  
**Datum:** 2026-06-11  
**Entscheider:** User (2026-06-11); SA sign-off pending (SA app-based at decision time)

## Kontext

Der klartext Multi-Agent-Betrieb lief in einem einzigen geteilten Working Tree (`$HOME/klartext`)
mit Sessions, die per Desktop-App aus `$HOME` gestartet wurden. Dieser Aufbau verursachte
am 2026-06-10 drei Incident-Klassen in einem Tag:

1. **Uncommitted edits wurden durch `git reset`-Operationen anderer Agents zerstört** — OE verlor
   5 Register-Rows, CME 3 claude.md-Abschnitte, SA 4 Abschnitte. Recovery war Glück + Redundanz,
   kein Schutz (RC4/RC5-Klasse: documented vs. actual).

2. **Project settings und PostCompact-hooks luden nie** — Sessions starteten mit cwd `$HOME`,
   kein Git-Repo → `.claude/settings.json` und alle definierten Hooks blieben tot.
   Alle allowlist-Regeln in `start.sh` waren de facto wirkungslos: nie enforced.

3. **Compaction-Monitoring konnte nicht zuverlässig bewiesen werden** — der Hook-Layer war tot,
   die ersten zwei Monitoring-Trials scheiterten aus diesem Grund.

### Optionen evaluiert

| Option | Entscheidung | Grund |
|---|---|---|
| **Weiter: Eternal app sessions + shared tree** | REJECTED | False-persistence-Kette (RC4/RC5): committed knowledge ≠ disk knowledge; drei Agents verloren claude.md-Inhalte in einem Tag; root cause nicht behebbar ohne Isolation |
| **Desktop-App Folder-Select** | REJECTED | Strukturell unmöglich upstream: Folder-Pick setzt den Projektkontext der App, nie den Shell-cwd. Kein `--cwd`-Flag, kein shipped default-dir setting (GH #56688/#26287/#60151/#60099) — DevOps-Analyse bestätigt |
| **Agent Teams as memory/blackboard** | REJECTED | Ephemer by design: Team-dirs werden beim Session-Ende gelöscht. Tool-Missbrauch; schließt RC4 nicht |
| **Native app worktrees (app settings "worktree location")** | REJECTED | Für ephemere Sessions gebaut; `claude/`-Branches divergieren bei Eternal-Agents; DevOps-Recherche bestätigt Inkompatibilität |
| **Hybrid (high-write-risk terminal, Advisors in-app)** | Not chosen | Konvergiert zu Full-Terminal bei konsequenter Anwendung; Zweiklassengesellschaft im Team |
| **Full terminal via `start.sh` + Worktree-per-Agent + File Inbox** | **ACCEPTED** | Einziger Weg der Project-Settings, Hooks und Allowlists mechanisch enforced (statt rituell) — Enforcement-Hierarchy Regel |

## Entscheidung

**Jeder Agent läuft in einem eigenen langlebigen Git-Worktree, gestartet per Terminal via `scripts/start-agent.sh <slug>`.**

### Komponenten

**1. Worktree-per-Agent**
- Layout: `$HOME/klartext-worktrees/<slug>/` (außerhalb des Repos, nicht App-ephemer)
- Branch: `agent/<slug>` (persistent; rebase auf `origin/main` bei jedem Session-Start)
- Idempotente Provisionierung: `start-agent.sh` erstellt den Worktree beim ersten Start;
  existing Worktrees werden nie resettet — uncommitted WIP bleibt erhalten
- `agents/<name>/start.sh` = thin wrapper: `exec "$(dirname "$0")/../../scripts/start-agent.sh" <name>`
- Allowlists: `agents/<name>/allowed-tools.txt` (eine Zeile pro Tool); central launcher liest sie

**2. File Inbox als Messaging-Fallback**
- `scripts/inbox.sh send/read/unread` — dateibasierter Briefkasten in gepinntem shared memory
- Ablage: `~/.claude/klartext-team-memory/inbox/<slug>/`
- Semantik identisch zu App-DMs: User nudgt den Empfänger; der liest beim Session-Start
- Entkoppelt die Messaging-Schicht von der App-Infrastruktur (kein Lock-in auf experimental features)
- Architekturprinzip: **"isolate code, share comms/memory/audit"** — code layer per-agent (worktrees),
  shared layer zentral gepinnt (memory + inbox + compact-log)

**3. Central Compact-Log**
- `~/.claude/klartext-team-memory/compact-log.jsonl` — ein Log für alle Agents
- Branch-Feld im Log-Eintrag identifiziert den compacteten Agent
- Ein launchd-Monitor-Prozess deckt alle Worktrees ab; kein Monitor-Drift bei Rollout

**4. Generation Change als Norm**
- Statt Eternal-Session + `/compact`: Session endet → `start.sh` startet frischen Nachfolger
- Nachfolger liest von Disk: `claude.md` + domain knowledge + gepinnte Memory = vollständige Übergabe
- Pre-Compact wird zu Pre-Restart: Wissen sichern, dann Session beenden

## Konsequenzen

**Positiv:**
- Project settings, PostCompact-hooks und --allowedTools-Allowlists greifen mechanisch (Enforcement-Hierarchy level 1)
- WIP-Commits halten die volatile Schicht von Tagen auf Minuten
- Monitoring nachweislich funktional: Hook feuerte auf ersten echten `/compact` (2026-06-11, Trial 4)
- Uncommitted edits sind physisch isoliert — der RC5-Incident ist strukturell nicht reproduzierbar

**Negativ / Trade-offs:**
- Terminal-Sessions sind für die Desktop-App unsichtbar (kein Session-Listing, kein `ccd_session_mgmt`)
- Messaging über File-Inbox statt App-DMs: leicht mehr Friction (User muss Empfänger anstupsen)
- Rollout erfordert einen kontrollierten Generationswechsel aller 10 Sessions — einmalig, nicht dauerhaft

**Scope-Caveat:**
- Pilot: DevOps (2026-06-11). Rollout der anderen 9 Agents nach separatem Go
- SA sign-off auf dieses ADR ausstehend (SA läuft zum Entscheidungszeitpunkt noch app-basiert)
- Stage-2-Spec (Worktree-Lifecycle, Crashrecovery, Orphan-Check) liegt vor; Umsetzung nach Pilot-Beweis

## Referenzen

- Improvement-Register-Row (CI §3): "Structural change: `git worktree` per context + session-cwd repair"
- PRs: #70 (inbox.sh), #71 (compact-log central), #75 (start-agent.sh), #76 (thin wrappers + allowlists)
- `scripts/start-agent.sh` — zentrale Launcher-Logik
- `scripts/inbox.sh` — dateibasierter Briefkasten
- `agents/*/start.sh` — thin wrappers (OE-Domain)
- `agents/*/allowed-tools.txt` — per-agent Allowlists (OE-Domain)
