# Design: Kern-Objektmodell des Wirkgefüges

**Datum:** 2026-06-01  
**Status:** Entwurf — zur Review  
**Scope:** Innere Struktur und Verantwortungsverteilung der Kernklassen des Wirkgefüges. Ohne Narrativ-Anbindung, ohne Zeitscheiben.

---

## 1. Terminologie

| Begriff | Bedeutung |
|---|---|
| **Wirkgefüge** | Sprachlicher Oberbegriff für alle Konzepte, die sich mit dem kausalen Raum beschäftigen. Keine Klasse. |
| **CausalModel** | Die konkrete Top-Level-Klasse — eine versionierte, prüfbare Instanz eines Wirkmodells. |

---

## 2. Grundprinzipien

### Keine Claim-Klasse
Claims existieren nicht als eigenständige Klasse im Wirkgefüge. Jeder Claimtyp wird auf bestehende Strukturen zurückgeführt:

| Claimtyp | Übersetzung ins Modell |
|---|---|
| Empirisch | Slot + Zustand + epistemischer Status |
| Kausal | CausalRelation |
| Definitorisch | Metadaten des Slots + referentielle Integrität |
| Normativ | Precondition auf einer Relation |
| Prognostisch | Zurückgestellt → Zeitscheiben |
| Kontrafaktisch | Slot + Zustand mit `epistemic_status = AXIOMATIC` |
| Methodisch | Slot + Zustand mit `epistemic_status = AXIOMATIC`, optional Source |
| Unsicherheit | Attribut auf einem Element |

Der Begriff "Claim" bleibt dem Narrativ vorbehalten.

### Axiomatic als EpistemicStatus
Es gibt keine `Axiom`-Klasse und kein separates `axiomatic`-Flag. `AXIOMATIC` ist ein Wert des `EpistemicStatus`-Enums. Der **Axiomsraum** ist eine abgeleitete Menge — alle Elemente eines CausalModels, bei denen `epistemic_status = AXIOMATIC`.

### Veränderungen zurückgestellt
Zustände beschreiben feste Werte ("421 ppm", "handlungsfähig"). Veränderungen (steigend, sinkend) finden auf einer Zeitachse statt und werden erst bei der Modellierung von Zeitscheiben behandelt.

---

## 3. Klassenhierarchie

```
CausalComponent (abstrakt)
  ├── CausalLeaf (abstrakt)
  │     ├── Slot
  │     │     └── Entity
  │     └── Relation (abstrakt)
  │           ├── CausalRelation
  │           ├── ConflictRelation
  │           └── DefinitoryRelation
  ├── CausalMixin
  └── CausalComposite (abstrakt)
        ├── CausalModel
        └── CausalModelFederation

Außerhalb der CausalComponent-Hierarchie (keine Modellbausteine):
  Zustand       — Wert eines Slots, immer relativ zu einem Slot
  Precondition  — Bedingung auf einer Relation, kein eigenständiger Baustein
  Quelle        — externe Referenz, nicht Teil des Wirkgefüges
```

---

## 4. Klassen im Detail

### CausalComponent (abstrakt)
Die gemeinsame Basisklasse aller Modellelemente. Definiert das Protokoll, das alle Subklassen erfüllen müssen — unabhängig davon, ob sie atomar, zusammengesetzt oder ein Fragment sind.

**Funktion:** Jedes Element im Wirkgefüge ist ein CausalComponent. Das ermöglicht einheitliche Traversierung, Prüfung und Abfrage über alle Ebenen der Composite-Hierarchie hinweg.

**Protokoll (abstrakte Methoden):**
- `get_slots() → list[Slot]` — liefert alle Slots, die dieses Element enthält oder erreichbar macht
- `get_relations() → list[Relation]` — liefert alle Relationen, die dieses Element enthält oder erreichbar macht
- `get_namespace() → Namespace` — liefert den Namespace dieses Elements; CausalLeafs geben `∅` zurück
- `is_complete() → bool` — gibt an, ob das Element für sich allein prüfbar und vollständig ist

**Gemeinsame Attribute aller Subklassen:**
- `scope: Scope` — Gültigkeitsbedingungen (temporal, räumlich, disziplinär)
- `epistemic_status: EpistemicStatus` — Default: `INCOMPLETE` (siehe Abschnitt 8)

**Verhaltensregel für `epistemic_status = AXIOMATIC`:**
Die Markierung bedeutet nicht, dass das Element wahr oder unveränderlich ist. Sie bedeutet, dass das Modell dieses Element an dieser Stelle nicht weiter intern herleitet. Änderungen an `AXIOMATIC`-Elementen sind prüfpflichtig — alle abhängigen Elemente müssen neu bewertet werden.

### CausalLeaf (abstrakt)
Atomares Element ohne eigene Kinder. Antwortet auf `get_namespace()` mit `∅` und auf `is_complete()` mit `false` — ein einzelnes Blatt ist für sich kein vollständiges Modell.

**Funktion:** CausalLeafs sind die inhaltlichen Grundbausteine. Sie tragen die eigentliche semantische Last des Wirkgefüges.

### Slot
Ein benannter Platzhalter für einen beobachtbaren oder messbaren Wert.

Inspiriert durch das Variablenkonzept im Compilerbau: ein Bezeichner, der mit einem Wert (Zustand) gekoppelt ist, mit Typ, Scope und Namespace.

**Zusätzliche Attribute** (über CausalComponent hinaus):
- `identifier: str` — eindeutiger Bezeichner im Namespace
- `slot_type: SlotType` — Typ (physikalische Größe, soziale Größe, etc.)
- `source: Source | None`

### Zustand
Ein konkreter Wert eines Slots. Eigenständiges Objekt, aber **kein CausalComponent** — er existiert immer relativ zu einem Slot und ist kein eigenständiger Modellbaustein, der im Composite-Baum platziert wird.

Da ein Zustand jedoch selbst epistemisch bewertet und als axiomatisch markiert werden kann (z.B. "dieser Wert gilt als gesetzt"), trägt er dieselben Statusattribute wie ein CausalComponent — allerdings nicht durch Vererbung, sondern als explizite Wiederholung.

**Attribute:**
- `value: str | float | int` — qualitativer oder quantitativer Wert
- `slot: Slot` — Referenz auf den zugehörigen Slot
- `epistemic_status: EpistemicStatus`

- `source: Source | None`

### Entity
Subtyp von `Slot`. Repräsentiert einen Akteur (Organisation, Gruppe, Institution). Kernmerkmal: Agency — die Fähigkeit zu handeln, zu entscheiden, zu beeinflussen.

Zustände einer Entity beschreiben Kapazität oder Status ("handlungsfähig", "aufgelöst"), keine Messwerte.

### Relation (abstrakt)
Eine gerichtete Beziehung zwischen zwei (Slot + Zustand)-Paaren.

**Zusätzliche Attribute** (über CausalComponent hinaus):
- `source_condition: (Slot, Zustand)` — Quellbedingung
- `target_effect: (Slot, Zustand)` — Zieleffekt
- `source: Source | None`

### CausalRelation
Spezialisiert `Relation`. Beschreibt einen gerichteten Wirkzusammenhang.

**Zusätzliche Attribute:**
- `mechanism: str` — Wirkmechanismus
- `polarity: Polarity` — positiv / negativ
- `strength: float | None`
- `uncertainty: float | None`
- `preconditions: list[Precondition]`

### ConflictRelation
Spezialisiert `Relation`. Markiert expliziten Widerspruch zwischen zwei Elementen — z.B. zwei Slots mit gleichem Bezeichner aber verschiedenen Zuständen im selben Geltungsbereich.

### DefinitoryRelation
Spezialisiert `Relation`. Beschreibt, wie ein Slot aus anderen Slots definiert oder berechnet wird. Grundlage für referentielle Integrität: alle Begriffe in einer Definition müssen selbst als Slots existieren.

### Precondition
Eine Bedingung, die erfüllt sein muss, damit eine Relation oder ein Prozess gültig angewendet werden kann. Normative Claims ("sollte", "muss") werden als Preconditions modelliert.

**Attribute:**
- `condition: (Slot, Zustand)`

### CausalMixin
Ein kohärentes, möglicherweise unvollständiges Fragment eines Wirkmodells. Kann aus anderen CausalMixins und CausalLeafs zusammengesetzt werden. Wiederverwendbar in mehreren CausalModels.

`is_complete()` gibt immer `false` zurück.

**Enthält:** `CausalLeaf`, `CausalMixin`  
**Eigener Namespace:** ja

### CausalModel
Eine vollständige, versionierte, prüfbare Instanz eines Wirkmodells. Enthält CausalLeafs direkt und bindet CausalMixins über eine separate `applies`-Beziehung ein (nicht `contains`).

`is_complete()` gibt `true` zurück, wenn alle Prüfungen bestanden.

**Enthält (contains):** `CausalLeaf`  
**Bindet ein (applies):** `CausalMixin`  
**Eigenschaft:** `causal_scope: CausalScope`  
**Eigener Namespace:** ja

### CausalModelFederation
Eine strukturierte Hierarchie mehrerer CausalModels und/oder CausalModelFederations. Kann auch CausalMixins direkt enthalten.

`is_complete()` gibt `true` zurück, wenn alle enthaltenen Modelle vollständig sind.

**Enthält:** `CausalModel`, `CausalModelFederation`, `CausalMixin`  
**Eigener Namespace:** ja

---

## 5. Composite Pattern — Enthaltensein und Beziehungen

| Klasse | `contains` | `applies` |
|---|---|---|
| CausalMixin | CausalLeaf, CausalMixin | — |
| CausalModel | CausalLeaf | CausalMixin |
| CausalModelFederation | CausalModel, CausalModelFederation, CausalMixin | — |

`get_slots()` und `get_relations()` auf CausalModel aggregieren aus `contains` **und** `applies`.

---

## 6. Namespace

Hierarchisch, typisiert. Jeder Container (CausalMixin, CausalModel, CausalModelFederation) hat einen eigenen Namespace. CausalLeafs haben keinen eigenen Namespace — sie erben vom Container.

**Grundregel:** Ein Bezeichner existiert genau einmal pro Namespace. Gleicher Bezeichner + verschiedene Zustände = selbes Objekt zu verschiedenen Zeitpunkten (→ Zeitscheiben) oder expliziter Konflikt (→ ConflictRelation).

**Qualifizierte Namen** für containerübergreifende Referenzen: `CausalModel::CO2-Konzentration`

---

## 7. Scope

Attribut auf jedem Element (CausalLeaf, CausalMixin, CausalModel, CausalModelFederation). Drei strukturierte, automatisch prüfbare Dimensionen:

```
Scope:
  temporal:     DateRange(start, end)
  spatial:      reference to region hierarchy
  disciplinary: reference to discipline taxonomy
```

Zwei Elemente sind nur dann in echtem Konflikt, wenn ihre Scopes sich in **allen** Dimensionen überschneiden.

---

## 8. EpistemicStatus

`EpistemicStatus` ist ein Enum mit drei mutual exclusive Werten. Er beschreibt den **Transparenzstatus** eines Elements: wie ausformuliert ist es im Modell, und welche Rolle spielt es in der Ableitungsstruktur?

Die Plattform ist keine Wahrheitsmaschine — `EpistemicStatus` urteilt nicht über externe Wahrheit, sondern über die interne Struktur des Modells.

```python
class EpistemicStatus(Enum):
    INCOMPLETE = "incomplete"   # default — not yet formalized
    DERIVED    = "derived"      # follows from other elements
    AXIOMATIC  = "axiomatic"    # set as premise, not derived here
```

| EpistemicStatus | Wann vollständig? |
|---|---|
| `INCOMPLETE` | Nie — blockiert `is_complete()` |
| `DERIVED` | Wenn alle Vorgänger in der Ableitungskette vollständig sind |
| `AXIOMATIC` | Immer — ist der Anker, an dem Ableitungsketten enden |

**Axiomsraum:** abgeleitete Menge aller Elemente mit `epistemic_status = AXIOMATIC` in einem CausalModel.

**`is_complete()` auf CausalModel** gibt `true` zurück, wenn kein enthaltenes Element den Status `INCOMPLETE` hat und alle `DERIVED`-Ketten bis zu `AXIOMATIC`-Elementen aufgelöst sind.

---

## 9. Source

Externes Objekt — kein Teil des Wirkgefüges. Jeder Slot und jede Relation kann optional auf eine Source verweisen. Die Referenz zeigt auf die kleinstmögliche semantische Einheit im Quelldokument (paragraph, measurement series, table).

---

## 10. Offene Todos

| # | Thema |
|---|---|
| T-09 | Veränderungen (steigend/sinkend) und Zeitscheiben |
| T-10 | Prüfung: Slots mit gleichem Bezeichner + referentielle Integrität von Definitionen |
| T-11 | Import von Quellen: granulare Verknüpfung auf Absatz-/Messreihenebene |
| T-12 | Scope: sachliche und methodische Dimension (derzeit ausgeklammert) |
| T-13 | Scope: attribute or standalone object? |

---

## 11. Noch nicht abgestimmt mit restlicher Dokumentation

Dieses Dokument beschreibt den erarbeiteten Kernstand. Folgende Kapitel der bestehenden Dokumentation müssen noch auf Konsistenz geprüft werden:

- Kap. 7.3 (Bestandteile eines Wirkmodells) — Begriffe wie "Entität", "Prozess", "Variable" müssen auf die neuen Klassennamen gemappt werden
- Kap. 7.4 (Objekt- und Lebenszyklusmodell) — Claims, Axiome, Gegenclaims neu bewerten
- Kap. 7.5 (Prüfverfahren) — Anforderungen gegen das neue Modell validieren
- Kap. 21 (Wirkmodell-Autor-Workflow) — Workflows gegen neue Klassen prüfen
