# Spec: Causal Model — aktueller Implementierungsstand

**Datum:** 2026-05-29
**Status:** Implementiert
**Scope:** CausalModel und Axiom — die Wirkgefüge-Seite des Systems.
Beschreibt was heute im Code existiert, nicht die Zielarchitektur.

---

## Überblick

Das CausalModel ist ein benannter Container für Axiome. Ein Axiom ist
eine axiomatisch gesetzte Grundannahme mit Label und Beschreibung.

Die aktuelle Implementierung ist eine bewusste Vereinfachung. Weder
die `CausalComponent`-Hierarchie noch `Slot`, `Relation`, `Zustand`
oder `EpistemicStatus` aus dem Kern-Designdokument sind implementiert.
Axiome entsprechen konzeptionell Elementen mit
`epistemic_status = AXIOMATIC` — sie sind aber als eigene Klasse
modelliert, nicht als Markierung auf einem allgemeinen Element.

---

## CausalModel

### CausalModelStatus

```python
class CausalModelStatus(str, Enum):
    PRIVATE    = "private"
    SHARED     = "shared"
    REVIEWABLE = "reviewable"
    INTERNAL   = "internal"
    CATALOG    = "catalogue"
    ARCHIVED   = "archived"
    REPLACED   = "superseded"
    WITHDRAWN  = "withdrawn"
```

Default beim Anlegen: `PRIVATE`.

### Attribute

| Attribut | Typ | Beschreibung |
|---|---|---|
| `id` | `str \| None` | UUID, nach Persistierung gesetzt |
| `title` | `str` | Nicht-leer, Pflichtfeld |
| `status` | `CausalModelStatus` | Default: `PRIVATE` |
| `axioms` | `list[Axiom]` | Geordnete Axiom-Liste |

### Factory Methods

```python
CausalModel.create(title: str) -> CausalModel
    # Pflicht: title nicht leer (CausalModelValidationError)
    # Status wird automatisch auf PRIVATE gesetzt

CausalModel.from_record(record: dict) -> CausalModel
    # Felder: id, title, status
```

### Mutation

```python
causal_model.add_axiom(axiom: Axiom) -> None
```

### Datenbank

Tabelle: `causal_models`

| Spalte | Typ | Anmerkung |
|---|---|---|
| `id` | UUID PK | |
| `title` | TEXT NOT NULL | |
| `status` | TEXT NOT NULL | Default `'private'`; CHECK enum |
| `created_at` | TIMESTAMPTZ | |

---

## Axiom

### Attribute

| Attribut | Typ | Beschreibung |
|---|---|---|
| `id` | `str \| None` | UUID, nach Persistierung gesetzt |
| `label` | `str` | Nicht-leer, Pflichtfeld |
| `description` | `str` | Nicht-leer, Pflichtfeld |

### Factory Methods

```python
Axiom.create(label: str, description: str) -> Axiom
    # Pflicht: label und description nicht leer (AxiomValidationError)

Axiom.from_record(record: dict) -> Axiom
    # Felder: id, label, description
```

### Datenbank

Axiome werden in `model_elements` gespeichert — der allgemeinen
Polymorphtabelle der Zielarchitektur. Aktuelle Nutzung:

Tabelle: `model_elements`

| Spalte | Typ | Wert bei Axiom |
|---|---|---|
| `id` | UUID PK | |
| `causal_model_id` | UUID NOT NULL | FK → `causal_models.id` |
| `typ` | TEXT | `'axiom'` |
| `label` | TEXT NOT NULL | Axiom-Bezeichnung |
| `description` | TEXT | Axiom-Beschreibung |
| `is_axiomatic` | BOOLEAN | `TRUE` |
| `lifecycle_status` | TEXT | Default `'draft'`; aktuell ungenutzt |

**Hinweis:** `model_elements` ist für alle Objektklassen A–H aus Kap. 7.4.3
konzipiert (`entity`, `causal_relation`, `slot`, etc.). Aktuell schreiben
wir ausschließlich `typ='axiom'`.

---

## Konsistenzprüfung

Die Konsistenzprüfung ist kein Teil des CausalModel-Domänenobjekts,
nutzt es aber als Eingabe.

```
POST /causal-models/{id}/check-consistency
Body: {scene_text: str}
```

Ablauf: Axiome des Modells + Szenentext → `ClaudeConsistencyChecker` →
`ConsistencyResult` mit `consistent: bool` und `conflicts: list`.

Der `ConsistencyChecker` ist ein Port (abstraktes Interface), implementiert
durch `ClaudeConsistencyChecker`.

---

## API-Endpunkte

```
GET  /causal-models                          Liste aller Modelle (id + title + status)
POST /causal-models                          Modell anlegen {title}
GET  /causal-models/{id}                     Modell mit Axiomen
POST /causal-models/{id}/axioms             Axiom hinzufügen {label, description}
POST /causal-models/{id}/check-consistency  Konsistenz prüfen {scene_text}
```

---

## Was fehlt (bewusste Vereinfachungen)

- Keine `CausalComponent`-Hierarchie (kein `Slot`, `Relation`, `Zustand`)
- Kein `EpistemicStatus` — Axiome sind eine eigene Klasse statt einer Markierung
- Kein `Scope` auf Modellelementen
- Keine `CausalModelFederation` / Verbundmodelle
- Kein `CausalMixin` für wiederverwendbare Fragmente
- Keine Versionierung des Modells
- Axiome sind nicht lösch- oder bearbeitbar (nur add)
