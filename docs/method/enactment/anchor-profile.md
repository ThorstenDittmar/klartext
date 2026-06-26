# Anchor-Profil — klartext (Endeavour)

> **Was das ist.** Das **Endeavour-Anchor-Profil** für klartext: die konkrete Tailoring-Schicht, aus der
> der generische `anchor`-Skill (`docs/method/enactment/skills/anchor.md`) seine projekt-spezifischen Homes
> zieht. Der Skill kennt KEINE Pfade — sie stehen hier. Gilt für **alle Rollen**; rollen-spezifische
> Ergänzungen/Überschreibungen stehen im jeweiligen `agents/<rolle>/anchor-profile.md`.
> **Owner:** OE · **Essence type:** Work Product (klartext-Enactment der anchor-Practice).
> **Sprache:** Deutsch (wie der Skill + die Agent-Hoheitswissen-Dateien, die es bedient); die vier
> Feldnamen halten die Skill-Vertrags-Begriffe (`storage map` · `handoff routing` · `seed mechanism` ·
> `reading list`).

---

## `storage map` — wohin welche Wissensart gesichert wird

| Wissensart | Home | Owner / Hinweis |
|---|---|---|
| Eigenes Hoheitswissen (Muster, Regeln, Heuristiken der Rolle) | `agents/<rolle>/claude.md` | die Rolle selbst |
| Entscheidung + Begründung zur Arbeitsweise | `docs/method/enactment/continuous-improvement.md` | **OE** (ohne Write-Access: Briefing an OE) |
| Verbesserungs-Kandidat | Improvement-Register in `docs/method/enactment/continuous-improvement.md` §3 (Zustand *Identified*) | **OE** |
| Prozess-/WoW-Learning | `docs/method/enactment/learnings/` | allgemein; QA-Learnings → `docs/superpowers/qa-learnings/` (QA) |
| Neues/geändertes Methoden-Element (Practice/Pattern) | L3-Karte `docs/method/library/practices/` (bzw. `patterns/`) + L2-Enactment `docs/method/enactment/practices/` + Element-Register `docs/method/enactment/method.md` — **im selben Schritt** | **nur OE**; andere: Briefing an OE |
| Begriff (generisch) | `docs/method/library/semat-glossary.md` (L3) | **OE** |
| Begriff (klartext-spezifisch) | `docs/method/enactment/semat-glossary-klartext.md` (L2) | **OE** |
| Architektur-Entscheidung | `docs/adr/NNNN-<titel>.md` (Status `Proposed`) | **System Architect** |
| Geparkter Befund (Kategorie 7) | benanntes Verwahr-Depot mit Freigabe-/Löschbedingung (Memory-Park-Pattern) | Park-Owner |
| Provenienz einer externen Referenz | `assets-local/README.md` | Finder |
| Cross-Session-Fakt / persistentes Gedächtnis | Memory-Datei unter `~/.claude/klartext-team-memory/` (+ Zeile in `MEMORY.md`) | je Memory besessen |
| Sonstiges Durables | `CLAUDE.md` (Root, SA), Code-Kommentar/Docstring, Commit-Message, GitHub-Issue | je Owner |

**Schreibrechte vorher prüfen** (laut `start.sh`/Domäne). Kein Home wählen, auf das die Session nicht
schreiben darf — stattdessen Briefing an den Owner über `handoff routing`.

## `handoff routing` — wie Wissen das Vorhaben verlässt (an einen anderen Akteur)

- **Durabler Inbox (der Boden):** `bash scripts/inbox.sh send <to> <from> "<betreff>"` (Body auf stdin).
  „**Inbox is the floor, app is the doorbell**" — alles Aktionsrelevante MUSS in den Inbox; die App-DM ist
  nur die Klingel, nie der Kanal für Inhalt (Kanal-Politik #108).
- **Empfänger ist der GATEKEEPER, nicht nur der Build-Owner:** Gate-/Approval-Requests an OE; Owner-Slug
  beim Senden prüfen.
- **Delegations-Tracking:** offene Delegationen direkt in `docs/superpowers/plans/PENDING.md`, Abschnitt
  „## Offene Delegationen", als Tabellenzeile. Das ist die **einzige Ausnahme** vom „User/Inbox als Kanal"-
  Prinzip — Tracking, nicht Domain-Wissen.
- **Kein Agent schreibt direkt in die `claude.md` / Memory / Profile eines anderen Akteurs** — Briefing über
  den Inbox an den Owner, der Owner zieht selbst nach.

## `seed mechanism` — wie die Nachfolge-Session geseedet wird (nur Restart)

- **Self-Message in den eigenen Inbox:**
  `bash scripts/inbox.sh send <self> <self> "Successor-Seed: <kurzer Betreff>"` (Body auf stdin).
- **Inhalt:** Stand (erledigt/in Arbeit/blockiert, mit PR-/Branch-/Commit-Bezügen) · offene Fäden ·
  **Wake-Prompt** (eine konkrete erste Anweisung; eine frische Session handelt nicht von selbst).
- **Verifikation:** `bash scripts/inbox.sh unread <self>` zeigt ≥1 — der Seed darf nicht selbst dem
  False-Persistence-Bug zum Opfer fallen.

## `reading list` — was bei jedem Sessionstart neu zu lesen ist

1. `CLAUDE.md` (Root) + `agents/<rolle>/claude.md` (Hoheitswissen) — lädt die Runtime/der SessionStart-Hook.
2. **Method-Set:** `docs/method/library/{semat-definition,semat-glossary,alpha-states}.md` (L3) +
   `docs/method/enactment/{continuous-improvement,method,semat-glossary-klartext}.md` (L2).
3. **A-jour vor Arbeit:** `klartext converge` (bzw. `git rebase origin/main`) — Aktualität ist ein
   Zeitstempel, der verfällt; vor dem Bewerten frisch gemergten Materials erneut convergen.
4. **Postfach:** `bash scripts/inbox.sh read <rolle>`.

---

*Rollen-spezifische Ergänzungen: `agents/<rolle>/anchor-profile.md` (OE/QA/Hannibal/DevOps eigene; die
Domain-Experten teilen `docs/method/enactment/anchor-profile.domain-agent.md`). Ein Role-Profil
**überschreibt/ergänzt** nur die Felder, in denen seine Homes von diesem Endeavour-Profil abweichen.*
