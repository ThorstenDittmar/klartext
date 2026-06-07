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
