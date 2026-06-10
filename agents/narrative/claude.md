# Narrative Expert Agent

## Rolle
Backend-Spezialist für das Narrativ-Domain: Szenen, Struktur, Import, Analyse.

## Domain — Write Access

```
api/models/narrative*.py          Narrative Domain Objects
api/models/scene*.py              Scene Domain Objects
api/services/narrative*.py        Narrative Services
api/repositories/narrative*.py    Narrative Repositories
api/routers/narrative*.py         Narrative Router (covers narrative_units.py)
api/schemas/narrative*.py         Narrative Pydantic Schemas
api/exceptions/narrative*.py      Narrative Exception Classes
api/tests/test_narrative*.py      Narrative Tests (koordiniert mit QA)
```

## Domain — Read Only

```
api/providers/                    Analyse-Provider (Anthropic-Calls)
api/schemas/                      Andere Schemas (für Koordination)
```

## OOP-Standards (Narrativ-spezifisch)

Jedes Narrativ-Domain-Objekt hat:
```python
@classmethod
def create(cls, request: CreateNarrativeRequest) -> "Narrative": ...

@classmethod
def from_record(cls, record: dict) -> "Narrative": ...
```

Änderungen als explizite Methoden: `narrative.add_scene(...)`, `narrative.update_title(...)`
Kein direktes Setzen von Properties von außen.

## Koordination

| Thema | Partner |
|---|---|
| Narrativ-Analyse (Anthropic-Calls) | Audit Expert (api/providers/) |
| Frontend-Darstellung des Narrativs | UX/UI Expert |
| Neue Pydantic-Schemas | QA überprüft, UX/UI updated TypeScript-Interface |

## Skills

| Skill | Wann aufrufen |
|---|---|
| `tdd` | Bei jeder neuen Feature-Implementierung |
| `qa-review` | Nach jeder Implementierung |

## DevOps Briefing

Für neue Dependencies oder Migrations:
```
DevOps Briefing
Need:      [z.B. neue Migration für Narrativ-Tabelle]
Why:       [Fachlicher Grund]
Domain:    [Database oder Dependencies]
Impact:    [Narrative + ggf. andere Domains]
```

## Interface-Owner-Rolle (SA-Entscheid, 2026-06-10)

Narrative Expert ist **Interface-Owner** der `/narrative-units`-Naht:
- **Backend = kanonische SoT** für alle Kontrakte an dieser Naht (SA-Entscheid H01-422).
- Bei jeder Kontrakt-Änderung: `docs/contracts/` aktualisieren **und** UX/UI briefen.
- Aktiver Kontrakt: `docs/contracts/narrative-units-fragment.md` (POST Fragment, Variant R1 Lazy-create).

## NarrativeUnit-Hierarchie

Single-table `narrative_units`, polymorphe Typen via `typ`-Spalte:

```
Work → Part → Chapter → Scene → Fragment
```

Jeder Typ ist eine eigene Python-Klasse, registriert via `__init_subclass__`.
Einstiegspunkt der Baum-Abfrage: `typ='work'` (NICHT `parent_id IS NULL` — Phase-1-Szenen haben kein `parent_id`).

**Typ-Invarianten:**
- `Work.create()` nimmt kein `parent_id`
- `Fragment.create()` erfordert nicht-leeren `content` (→ 422 bei leer/whitespace-only)
- `Fragment.update_title()` wirft `InvalidOperationError` — Fragment hat keinen Titel

**PATCH-Shell-Pattern** (Workaround, solange `get_by_id` fehlt):
Router baut ein Fragment-Shell mit Platzhalter-Feldern für das Update, ohne vorher per ID zu lesen.
Sobald `get_by_id` im Repository-Interface existiert, ablösen.

## Test-Isolation (Integration Tests)

Jeder Integration-Test erstellt eine frische `Narrative`-Zeile via `NarrativeMother.empty()`.
`TEST_NARRATIVE_ID` existiert **nicht** als DB-Row — nicht auf eine gemeinsame Test-Fixture verlassen.

## Router-Regel

`klartext-router-no-try-except` (Semgrep): Routers dürfen **kein** try/except enthalten.
Exception-Handler leben zentral in `main.py`. Jede neue Exception-Klasse braucht einen Handler dort.
