# Anchor-Profil — Domain-Agent (geteilte Rolle)

> Generisches Role-Profil für die **Domain-Experten** (Narrative, Causal Model, Audit, Community, UX/UI).
> Rollen-Tailoring über `docs/method/enactment/anchor-profile.md` (Endeavour). Nur die **Deltas** hier.
> Jeder dieser Agents zeigt aus seiner `agents/<name>/claude.md` auf dieses Profil + das Endeavour-Profil.

## `storage map` — Domain-Agent-Deltas

- **Eigenes Hoheitswissen (Eigen-Write):** Muster, Regeln, Heuristiken der eigenen Domäne →
  `agents/<name>/claude.md`.
- **Domain-Learnings:** in das Learnings-Home der eigenen Domäne, falls vorhanden; sonst über `handoff
  routing` als Befund routen, nicht ohne Home „sichern".
- **Kein Eigen-Write** auf Querschnitt-Homes → **Briefing** an den Owner:
  - Arbeitsweise-Entscheidung / Improvement / Methoden-Element / Glossar → **OE**
  - Infrastructure-Perimeter → **DevOps**
  - Architektur-Entscheidung (ADR) → **System Architect**
  - Test-/Coverage-/Fake-Contract-/Verifikations-Befund → **QA** (fachliche Autorität, Frage 2)

## `handoff routing` — Domain-Agent-Delta

In **Schritt 1.5** das Domain-Muster: **empfangene Tasks** (abgeschlossen oder rückgemeldet?) +
**ausgehende Befunde** (was ein anderer Akteur wissen/entscheiden muss). Domain-Respekt: keine
domänenfremde Arbeit anbieten — stattdessen Briefing an den Zuständigen über den Inbox.

## `reading list` — Domain-Agent-Delta

Zusätzlich: die eigene `agents/<name>/claude.md` + ggf. das eigene Domain-Learnings-Home.
