# ADR 0003: ConsistencyChecker via Ports & Adapters

**Status:** Accepted  
**Datum:** 2026-05-27  
**Autoren:** Thorsten Dittmar

---

## Kontext

Das Wirkmodell-Feature erfordert eine automatische Konsistenzprüfung: Gegeben eine Szene aus einem Narrativ und die Axiome eines Wirkmodells — widerspricht die Szene einem Axiom?

Diese Prüfung erfordert semantisches Verständnis, das weit über regelbasierte Ansätze hinausgeht. Der naheliegende Ansatz ist daher ein LLM-Aufruf (Claude). Gleichzeitig gibt es Anforderungen an Testbarkeit und spätere Erweiterbarkeit:

- Der `CausalModelService` darf keine direkte Abhängigkeit auf `anthropic.AsyncAnthropic` haben
- Unit-Tests des Service sollen deterministisch laufen — ohne echte API-Aufrufe
- Mittelfristig sind alternative Implementierungen denkbar (lokales Modell, Regelwerk für bestimmte Axiom-Typen, kombinierte Ansätze)

---

## Entscheidung

Die Konsistenzprüfung wird als **Ports & Adapters** implementiert:

- **Port** (`ConsistencyChecker`, ABC): definiert den Vertrag — `check(scene_text, axioms) → ConsistencyResult`
- **Adapter** (`ClaudeConsistencyChecker`): produktive Implementierung via Claude API
- **Fake** (`FakeConsistencyChecker`): deterministische Implementierung für Tests

```
api/
  providers/
    consistency_checker.py          ← Port + Ergebnistypen (ConsistencyResult, ConsistencyConflict)
    claude_consistency_checker.py   ← Adapter (Produktion)
  tests/
    fakes/
      fake_consistency_checker.py   ← Fake (Tests)
```

Der `CausalModelService` kennt nur den Port:

```python
class CausalModelService:
    def __init__(self, checker: ConsistencyChecker, ...) -> None:
        self._checker = checker
```

Die Verdrahtung erfolgt in `dependencies.py` via FastAPI `Depends()`.

---

## Begründung

**Gegen direkten Claude-Aufruf im Service:**  
Würde den Service direkt an `anthropic.AsyncAnthropic` koppeln. Tests wären langsam, teuer und nicht-deterministisch. Ein späterer Wechsel des Modells oder Anbieters würde den Service-Code berühren.

**Für Ports & Adapters:**  
Passt zur bereits etablierten Projektarchitektur (ClaimExtractor folgt demselben Muster). Der Service testet Logik — nicht die Claude-Integration. Die Claude-Integration wird separat in `tests/test_consistency_checker.py` als Spike/Infrastrukturtest validiert.

---

## Ergebnistypen

`ConsistencyResult` und `ConsistencyConflict` werden im Port-Modul definiert, nicht im Service oder Schema. Sie sind reine Datencontainer und können direkt in Pydantic-Response-Schemas gemappt werden.

```python
@dataclass
class ConsistencyConflict:
    axiom_label: str
    description: str
    suggestion: str | None = None

@dataclass
class ConsistencyResult:
    consistent: bool
    conflicts: list[ConsistencyConflict]
```

---

## Konsequenzen

**Positiv:**
- `CausalModelService` ist vollständig unit-testbar ohne Claude-API
- Implementierung kann ausgetauscht werden ohne Service-Logik zu berühren
- Konsistentes Muster mit `ClaimExtractor` (ADR nicht explizit, aber gleiches Prinzip)

**Negativ / offen:**
- Ein weiterer Indirektionsschritt gegenüber einem direkten Claude-Aufruf
- Prompt-Engineering für `ClaudeConsistencyChecker` (System-Prompt) erfordert manuelle Qualitätsprüfung — kann nicht durch Unit-Tests abgedeckt werden (→ ADR 0001)

---

## Verwandte Entscheidungen

- [ADR 0001: Inhaltliche Qualitätsprüfung der Detektoren](0001-detector-quality-testing.md)
- [ADR 0002: Test Data Management via Object Mother](0002-test-data-object-mother.md)
