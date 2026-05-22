# ADR 0002: Test Data Management via Object Mother

**Status:** Accepted  
**Datum:** 2026-05-22  
**Autoren:** Thorsten Dittmar

---

## Kontext

klartext.jetzt arbeitet mit komplexen Domänenobjekten (`Narrative`, `Scene`, `Claim`, später `Wirkmodell`, `Modellelement` u.a.). Tests auf allen vier Ebenen (Domain, Service, Repository, Router) benötigen reproduzierbare, aussagekräftige Testdaten.

Zwei Standardansätze wurden evaluiert:

**1. Externe Fixture-Dateien** (JSON, YAML, SQL)  
Daten liegen als Dateien vor und werden direkt in die Datenbank geladen oder an die Klasse übergeben. Bekannt aus Django-Fixtures und SQL-Seed-Skripten.

**2. `factory_boy`**  
Die in der Python-Community verbreitetste Library für Testdatengenerierung. Inspiriert von FactoryBot (Ruby). Bietet Sequences, Traits, Sub-Factories und direkte ORM-Integration.

---

## Entscheidung

Wir verwenden das **Object Mother**-Muster: dedizierte Klassen in `tests/mothers/`, eine pro Domänenentität, mit benannten Factory-Methoden für typische Testszenarien.

```
tests/
  mothers/
    narrative_mother.py   ← NarrativeMother
    claim_mother.py       ← ClaimMother
    scene_mother.py       ← SceneMother
```

Jede Mother-Klasse bietet mindestens drei Methoden:

```python
class NarrativeMother:
    @staticmethod
    def minimal() -> Narrative:
        """Simplest valid narrative — for tests that don't care about structure."""

    @staticmethod
    def complete() -> Narrative:
        """Fully populated narrative — for serialisation and mapping tests."""

    @staticmethod
    def collection() -> list[Narrative]:
        """A varied set of narratives — for list, filter and pagination tests."""
```

Pytest-Fixtures in `conftest.py` wrappen die Mothers für Scope-Management und Teardown:

```python
@pytest.fixture
def minimal_narrative() -> Narrative:
    return NarrativeMother.minimal()
```

Externe Dateien in `tests/fixtures/` bleiben erhalten — ausschließlich für inhärent dateibasierte Testdaten (Markdown-Narrative, gemockte Claude-API-Antworten).

---

## Begründung

**Gegen externe Fixture-Dateien als primären Ansatz:**  
Feldnamen-Änderungen an Domänenobjekten brechen Fixture-Dateien still — kein Compiler, kein Typchecker schlägt an. Bei einem aktiv wachsenden Datenmodell ist das ein hohes Risiko.

**Gegen `factory_boy`:**  
`factory_boy` ist primär für ORM-gestützte Modelle optimiert (Django, SQLAlchemy). Klartext.jetzt verwendet bewusst keinen ORM — Domänenobjekte sind pure Python-Klassen, der Datenbankzugriff läuft über Repository-Klassen mit expliziten `from_record()`-Methoden. Der zentrale Vorteil von `factory_boy` (ORM-Integration) entfällt damit. Eine externe Dependency einzuführen, deren Hauptvorteil man nicht nutzt, ist nicht gerechtfertigt.

**Für Object Mother:**
- Passt zur OOP-Architektur des Projekts (Klassen, keine losen Funktionen)
- Typsicher — Refactorings an Domänenobjekten erzeugen sofort Compilerfehler
- Kein zusätzlicher Dependency
- Selbstdokumentierend: `NarrativeMother.complete()` beschreibt den Testfall
- Äquivalent zum Smalltalk-Protokoll `examples`/`explain` auf Klassenseite — aber als separate Testklasse, damit Produktionscode sauber bleibt

---

## Konsequenzen

**Positiv:**
- Testdaten sind typsicher und refactoring-resistent
- Klarer Ort für alle Testdaten-Konstruktion
- Kein neues Dependency

**Negativ / offen:**
- Sequences (eindeutige Werte über mehrere Objekte hinweg) müssen manuell implementiert werden, wenn nötig
- Bei Einführung eines ORM wäre ein Wechsel zu `factory_boy` sinnvoll — dann ADR überarbeiten

---

## Verwandte Entscheidungen

- [ADR 0001: Inhaltliche Qualitätsprüfung der Detektoren](0001-detector-quality-testing.md)
