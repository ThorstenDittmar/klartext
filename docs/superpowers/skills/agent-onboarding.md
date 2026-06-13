---
name: agent-onboarding
description: >
  Use when adding a new specialist agent to the klartext multi-agent system.
  OE skill — guides OE through domain definition, start script creation, knowledge file, CLAUDE.md update,
  and agent handoff.
---

# Agent Onboarding

This skill is used by **OE** when integrating a new specialist agent into the klartext
multi-agent system. OE owns `agents/` vollständig — start script, knowledge file, domain entry,
alles in OE-Hand. Kein DevOps Briefing nötig.

Each agent lives in its own directory: `agents/<name>/`
- `agents/<name>/start.sh` — thin wrapper, delegates to the central launcher `scripts/start-agent.sh`
- `agents/<name>/allowed-tools.txt` — the agent's tool allowlist (one entry per line, read by the launcher)
- `agents/<name>/claude.md` — Hoheitswissen und domänenspezifische Regeln (wird von Claude Code als CLAUDE.md erkannt und automatisch geladen)

**Operating model (since 2026-06-11, see the structural ADR):** every agent session is started
**from the terminal** via the central launcher — never via the desktop app (the app cannot set the
shell cwd; settings, hooks and allowlists would stay dead). The launcher provisions a persistent
worktree (`$HOME/klartext-worktrees/<name>/`, home branch `agent/<name>`) idempotently, rebases it
on `origin/main`, shows unread inbox messages and starts `claude` inside the worktree. Sessions are
**workdays, not lifetimes**: they end with a pre-restart ritual (pre-compact skill) and a successor
boots from disk. Cross-agent messages travel via the file inbox (`scripts/inbox.sh send/read`).

---

## Step 1 — Clarify the domain

Before touching any file, answer these questions (ask the user if unclear):

- **Name**: What is the agent called? (e.g. `narrative`, `qa`, `ux`)
- **Domain**: Which directories/files does this agent own (write access)?
- **Read-only**: What does the agent need to read but not write?
- **Conflicts**: Does the domain overlap with an existing agent?

The domain defines the entries in `allowed-tools.txt`. Be specific — narrow domains are safer.

---

## Step 2 — Create the agent directory, wrapper and allowlist

OE owns `agents/` vollständig — kein DevOps Briefing nötig.

```bash
mkdir -p agents/<name>
```

Create `agents/<name>/start.sh` (thin wrapper — all logic lives in the central launcher):

```bash
#!/bin/bash
# <Agent Name> — Agent startup script
#
# Domain: <one-line description>
#
# Allowlists live in agents/<name>/allowed-tools.txt (one entry per line),
# read by the central launcher scripts/start-agent.sh.

exec "$(dirname "$0")/../../scripts/start-agent.sh" <name>
```

Create `agents/<name>/allowed-tools.txt` (one tool grant per line):

```
Edit(docs/superpowers/plans/PENDING.md)
Write(docs/superpowers/plans/PENDING.md)
Edit(<domain-path>/)
Write(<domain-path>/)
Edit(agents/<name>/)
Write(agents/<name>/)
```

The PENDING.md lines are mandatory for every agent (pre-compact delegation tracking).

```bash
chmod +x agents/<name>/start.sh
```

**Important sequencing:** both files must be merged to `main` before the first session start —
the launcher reads the allowlist and the worktree checkout is based on `origin/main`.

**Landing path for knowledge-file changes (standard since 2026-06-12):** changes to
`agents/<name>/claude.md` land via own branch (in the agent's worktree) → PR → OE review
**comment** (formal GitHub approvals are single-account-impossible; the review comment IS the
sign-off artifact) → CI gate → merge.

**Team Roster (mandatory, same step):** add the new agent to `agents/team.yaml` (slug, display name,
`status: app`, `active: true`). The roster is the Work Product advancing the Team alpha and is
read by the start tooling — an agent missing here is invisible to it. Offboarding:
set `active: false` (keep the entry for history). Migration terminal↔app: flip `status` in the same
step as the generation change.

---

## Step 3 — Update CLAUDE.md

Add the new agent to the `## Agent Roles & Boundaries` table in `CLAUDE.md`:

```markdown
| <Agent Name> | <Domain description> |
```

If the agent owns paths that are not yet in any agent's domain, add them to the table.
Do NOT modify the Infrastructure Perimeter section without a separate DevOps decision.

---

## Step 4 — Create the agent knowledge file

Create `agents/<name>/claude.md` with the agent's domain knowledge.
Use `agents/devops/claude.md` or `agents/qa/claude.md` as reference.

Mindest-Inhalt:
- Rolle (ein Satz)
- Domain — Write Access (Pfade mit Erklärung)
- Domain — Read Only
- Domänenspezifische Standards
- Skills-Tabelle
- DevOps Briefing Template
- Abschnitt "Erweiterung durch <Agent>" — Platzhalter für Wissen das der Agent selbst einträgt

**Wichtig:** Die Datei heißt `claude.md` (lowercase). Claude Code erkennt sie automatisch
als CLAUDE.md und lädt sie beim Start — kein explizites Lesen nötig.

---

## Step 4b — Create agent skills (if needed)

If the agent needs project-specific skills, create them in:

- `docs/superpowers/skills/<skill-name>.md` — project-level skill (committed to repo)
- `~/.claude/skills/<skill-name>/` — user-level skill (richer format, local to machine)

Use the `skill-creator` skill to create or refine skill files.

---

## Step 5 — Commit

Commit all changes together:

```
git add agents/<name>/ CLAUDE.md docs/superpowers/skills/
git commit -m "Add <name> agent: start script, knowledge file, domain entry"
```

---

## Step 6 — Handoff message

Send the following to the new agent (adapt the placeholders):

```
Willkommen im klartext Team.

Du lebst in einer Terminal-Session in deinem eigenen Worktree
($HOME/klartext-worktrees/<name>/, Branch agent/<name>). Der User startet dich mit
`bash agents/<name>/start.sh` und beendet deine Session am natürlichen Arbeitsende —
deine Identität persistiert auf Platte, die Session ist dein Arbeitstag. Vor jedem
Session-Ende fährst du das pre-compact-Ritual (Pre-Restart) und hinterlegst deiner
Nachfolge-Session eine Handoff-Notiz im eigenen Postfach.

Dein Agent-Verzeichnis: agents/<name>/
  - start.sh           → dein Startweg (Terminal, nie Desktop-App)
  - allowed-tools.txt  → deine Permissions (vom Launcher gelesen)
  - claude.md          → dein Hoheitswissen (wird automatisch von Claude Code geladen)

Nachrichten an Kollegen: bash scripts/inbox.sh send <empfänger> <name> "..."
Dein Postfach lesen:     bash scripts/inbox.sh read <name>
Der User stupst den Empfänger an — er ist immer der Kanal.

Was du ohne Rückfrage darfst:
  - Lesen: alles (Read, git diff/log/status/show, grep, ls, find, semgrep)
  - Schreiben: nur dein Domain (steht in agents/<name>/claude.md)

Was eine Rückfrage braucht: alles außerhalb deines Domains.

Infrastruktur-Änderungen (CI, Dependencies, Scripts, settings.json):
  → DevOps Briefing schicken (Format in CLAUDE.md unter "DevOps Briefing Protocol")
  → DevOps entscheidet wie es umgesetzt wird

Gemeinsame Coding-Standards: CLAUDE.md (für alle Agents gleich)
Dein Hoheitswissen erweitern: trage domain-spezifisches Wissen in agents/<name>/claude.md ein

Wissens-Routing: Bei jedem pre-compact prüfst du ob Wissen entstanden ist, das einem
  anderen Agent gehört — Schritt 6 / Teil C führt dich durch den Prozess.
  Fremdwissen, Grenzwissen und Organisationswissen werden als Wissens-Briefings
  formuliert und dem User übergeben. Kein Agent schreibt direkt in fremde Dateien.
```

---

## Reference

- Infrastructure Perimeter and DevOps Briefing Protocol: `CLAUDE.md § Agent Roles & Boundaries`
- Base permissions for all agents: `.claude/settings.json`
- Existing agent directories: `agents/`
