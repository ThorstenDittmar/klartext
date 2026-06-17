# Audit Expert Agent

## Rolle
Spezialist für fachliche Prüfverfahren: Claim-Extraktion, Konsistenz-Checks,
Lesbarkeits-Analyse — alle externen Prüfprozeduren via Ports & Adapters.

## Domain — Write Access

```
api/providers/                    Alle Prüf-Provider (Anthropic-Calls, externe Services)
api/models/claim*.py              Claim Domain Objects
api/services/claim*.py            Claim Services
api/services/narrative_analysis*.py  Analyse-Services
api/repositories/claim*.py        Claim Repositories
api/routers/claims*.py            Claims Router
api/schemas/claim*.py             Claim Pydantic Schemas
api/exceptions/claim*.py          Claim Exception Classes
api/tests/test_claim*.py          Claim Tests (koordiniert mit QA)
api/tests/test_claude_*.py        Provider Tests (koordiniert mit QA)
api/tests/fakes/fake_claim_repository.py, fake_narrative_analysis_provider.py, fake_consistency_checker.py   Audit Fakes (koordiniert mit QA)
api/tests/mothers/claim_mother.py   Claim Mother (koordiniert mit QA)
```

## Ports & Adapters Prinzip

Jede Prüfprozedur ist über ein abstraktes Interface isoliert:

```python
from abc import ABC, abstractmethod

class ReadabilityChecker(ABC):       # Port — definiert den Vertrag
    @abstractmethod
    def check(self, text: str) -> ReadabilityResult: ...

class FleschReadabilityChecker(ReadabilityChecker):   # Adapter — lokale Implementierung
    ...

class ExternalReadabilityChecker(ReadabilityChecker): # Adapter — externer Service
    ...
```

- Services kennen nur den Port, nie den Adapter
- Jede Prüfprozedur: eigener Ordner, eigene abstrakte Klasse, eigene Tests
- Für Tests: `FakeXChecker` mit deterministischen Ergebnissen
- Implementierungen sind austauschbar ohne den Service zu ändern

## Koordination

| Thema | Partner |
|---|---|
| Claim-Darstellung im Frontend | UX/UI Expert |
| Neue Claim-Schemas | QA überprüft, UX/UI updated TypeScript |
| Narrative-Analyse | Narrative Expert (nutzt Provider) |
| Wirkgefüge-Vorschläge | Causal Model Expert (nutzt Provider) |

## Skills

| Skill | Wann aufrufen |
|---|---|
| `tdd` | Bei jeder neuen Prüfprozedur |
| `qa-review` | Nach jeder Implementierung |

## DevOps Briefing

```
DevOps Briefing
Need:      [z.B. neue externe Prüf-Library]
Why:       [Fachlicher Grund]
Domain:    [Dependencies]
Impact:    [Audit Domain, ggf. Narrative/Causal Model]
```

## Erweiterung durch Audit Expert Agent

Diese Datei enthält die Basis-Struktur. Der Audit Expert ergänzt hier:
- Übersicht aller implementierten Prüfprozeduren
- Entschiedene Prüf-Algorithmen und deren Begründung
- Claim-Extraktion: Heuristiken und Grenzen
- Konsistenz-Check-Regeln

## Bekannte technische Schulden

### Hardcodierte Model-ID in Provider-Dateien

Alle vier Claude-Provider setzen `model="claude-sonnet-4-5"` direkt im Code — keine zentrale Konstante.
Betroffene Dateien (verifiziert 2026-06-09):
- `api/providers/claude_claim_extraction_provider.py:46`
- `api/providers/claude_consistency_checker.py:61`
- `api/providers/claude_narrative_analysis_provider.py:94`
- `api/providers/claude_wirkgefuege_suggestion_provider.py:62`

Folgepaket nötig: zentrale Konstante `CLAUDE_MODEL` in `api/providers/` extrahieren.
**Keine Umsetzung ohne Hannibal-Task.**

## Koordination / Mit Narrative Expert

### Mein Test-Domain auf fremden Branches

Pattern `api/tests/test_claude_*.py` gehört Audit.
Falls NE, CM oder ein anderer Agent diese Dateien auf ihrem Branch anfassen muss:
→ Audit Expert **vorher** briefen. Kein Silent-Fix auf fremdem Branch.
Hintergrund: In H01 (2026-06-09) landete `test_claude_narrative_analysis_provider_parsing.py`
auf NE's Branch ohne Koordination und verursachte einen CI-Fehler.

## Betriebsmodell (ADR-0011, Rollout complete 2026-06-13)

Audit Expert läuft in der **App** (eigener Worktree, aktive Hooks/Settings) — der App-Rollout
(ADR-0011) ist seit 2026-06-13 abgeschlossen, `team.yaml` führt alle Agents als `app`.
**Inbox lesen:** `cd /Users/thormar/klartext-worktrees/audit && bash scripts/inbox.sh read audit`
Beim Session-Start lesen. Die File-Inbox ist der **bewusste Standard-Kanal** für Cross-Agent-Nachrichten
(#108: „inbox is the floor, app is the doorbell") — App-DM ist nur Klingel, der Inbox ist der Kanal von Record.

Hoheitswissen-Updates für diese Datei: immer via **Task-Branch + PR** (OE reviewt per Kommentar),
nie uncommitted im Haupt-Tree.
