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
- `agents/<name>/start.sh` — startet die Session mit den richtigen Permissions
- `agents/<name>/claude.md` — Hoheitswissen und domänenspezifische Regeln (wird von Claude Code als CLAUDE.md erkannt und automatisch geladen)

---

## Step 1 — Clarify the domain

Before touching any file, answer these questions (ask the user if unclear):

- **Name**: What is the agent called? (e.g. `narrative`, `qa`, `ux`)
- **Domain**: Which directories/files does this agent own (write access)?
- **Read-only**: What does the agent need to read but not write?
- **Conflicts**: Does the domain overlap with an existing agent?

The domain defines the `--allowedTools` permissions. Be specific — narrow domains are safer.

---

## Step 2 — Create the agent directory and start script

OE owns `agents/` vollständig — kein DevOps Briefing nötig.

```bash
mkdir -p agents/<name>
```

Create `agents/<name>/start.sh`:

```bash
#!/bin/bash
# <Agent Name> — Agent startup script
#
# Domain: <one-line description>
#
# Grants write access to:
#   - <path>     (<reason>)
#   - agents/<name>/    (self-write — own knowledge file)
#
# Read/Analyse permissions are granted project-wide in .claude/settings.json.
# OE Perimeter: This file is maintained by OE only.

cd "$(dirname "$0")/../.." || exit 1

claude \
  --allowedTools "Edit(<domain-path>/)" \
  --allowedTools "Write(<domain-path>/)" \
  --allowedTools "Edit(agents/<name>/)" \
  --allowedTools "Write(agents/<name>/)"
```

```bash
chmod +x agents/<name>/start.sh
```

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

Dein Agent-Verzeichnis: agents/<name>/
  - start.sh     → startet deine Session: bash agents/<name>/start.sh
  - claude.md    → dein Hoheitswissen (wird automatisch von Claude Code geladen)

Was du ohne Rückfrage darfst:
  - Lesen: alles (Read, git diff/log/status/show, grep, ls, find, semgrep)
  - Schreiben: nur dein Domain (steht in agents/<name>/claude.md)

Was eine Rückfrage braucht: alles außerhalb deines Domains.

Infrastruktur-Änderungen (CI, Dependencies, Scripts, settings.json):
  → DevOps Briefing schicken (Format in CLAUDE.md unter "DevOps Briefing Protocol")
  → DevOps entscheidet wie es umgesetzt wird

Gemeinsame Coding-Standards: CLAUDE.md (für alle Agents gleich)
Dein Hoheitswissen erweitern: trage domain-spezifisches Wissen in agents/<name>/claude.md ein
```

---

## Reference

- Infrastructure Perimeter and DevOps Briefing Protocol: `CLAUDE.md § Agent Roles & Boundaries`
- Base permissions for all agents: `.claude/settings.json`
- Existing agent directories: `agents/`
