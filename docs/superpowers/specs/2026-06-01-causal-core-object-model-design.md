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
| Kontrafaktisch | Axiomatisch gesetzter Slot + Zustand |
| Methodisch | Axiomatisch gesetzter Slot + Zustand über Quelle |
| Unsicherheit | Attribut auf einem Element |

Der Begriff "Claim" bleibt dem Narrativ vorbehalten.

### Axiomatisch als Flag
Es gibt keine `Axiom`-Klasse. Jedes Modellelement kann mit dem Flag `axiomatisch` markiert werden. Der **Axiomsraum** ist eine abgeleitete Menge — alle Elemente eines CausalModels, bei denen `axiomatisch = true`.

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
```

---

## 4. Klassen im Detail

### Slot
Ein benannter Platzhalter für einen beobachtbaren oder messbaren Wert.

Inspiriert durch das Variablenkonzept im Compilerbau: ein Bezeichner, der mit einem Wert (Zustand) gekoppelt ist, mit Typ, Scope und Namespace.

**Attribute:**
- `identifier: str` — eindeutiger Bezeichner im Namespace
- `slot_type: SlotType` — Typ (physikalische Größe, soziale Größe, etc.)
- `scope: Geltungsbereich`
- `epistemic_status: EpistemicStatus`
- `axiomatisch: bool`
- `source: Quelle | None`

### Zustand
Ein konkreter Wert eines Slots zu einem bestimmten Zeitpunkt oder in einem bestimmten Kontext. Eigenständiges Objekt — kein CausalComponent, da er immer relativ zu einem Slot existiert.

**Attribute:**
- `value: str | float | int` — qualitativer oder quantitativer Wert
- `slot: Slot` — Referenz auf den zugehörigen Slot
- `epistemic_status: EpistemicStatus`
- `axiomatisch: bool`
- `source: Quelle | None`

### Entity
Subtyp von `Slot`. Repräsentiert einen Akteur (Organisation, Gruppe, Institution). Kernmerkmal: Agency — die Fähigkeit zu handeln, zu entscheiden, zu beeinflussen.

Zustände einer Entity beschreiben Kapazität oder Status ("handlungsfähig", "aufgelöst"), keine Messwerte.

### Relation (abstrakt)
Eine gerichtete Beziehung zwischen zwei (Slot + Zustand)-Paaren.

**Attribute:**
- `source_condition: (Slot, Zustand)` — Quellbedingung
- `target_effect: (Slot, Zustand)` — Zieleffekt
- `scope: Geltungsbereich`
- `epistemic_status: EpistemicStatus`
- `axiomatisch: bool`
- `source: Quelle | None`

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
**Eigenschaft:** `wirkraum: Wirkraum`  
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

## 7. Geltungsbereich

Attribut auf jedem Element (CausalLeaf, CausalMixin, CausalModel, CausalModelFederation). Drei strukturierte, automatisch prüfbare Dimensionen:

```
Geltungsbereich:
  temporal:     DateRange(start, end)
  spatial:      Referenz auf Regionshierarchie
  disciplinary: Referenz auf Disziplintaxonomie
```

Zwei Elemente sind nur dann in echtem Konflikt, wenn ihre Geltungsbereiche sich in **allen** Dimensionen überschneiden.

---

## 8. Quelle

Externes Objekt — kein Teil des Wirkgefüges. Jeder Slot und jede Relation kann optional auf eine Quelle verweisen. Die Referenz zeigt auf die kleinstmögliche semantische Einheit im Quelldokument (Absatz, Messreihe, Tabelle).

---

## 9. Offene Todos

| # | Thema |
|---|---|
| T-09 | Veränderungen (steigend/sinkend) und Zeitscheiben |
| T-10 | Prüfung: Slots mit gleichem Bezeichner + referentielle Integrität von Definitionen |
| T-11 | Import von Quellen: granulare Verknüpfung auf Absatz-/Messreihenebene |
| T-12 | Geltungsbereich: sachliche und methodische Dimension (derzeit ausgeklammert) |
| T-13 | Geltungsbereich: Attribut oder eigenständiges Objekt? |

---

## 10. Noch nicht abgestimmt mit restlicher Dokumentation

Dieses Dokument beschreibt den erarbeiteten Kernstand. Folgende Kapitel der bestehenden Dokumentation müssen noch auf Konsistenz geprüft werden:

- Kap. 7.3 (Bestandteile eines Wirkmodells) — Begriffe wie "Entität", "Prozess", "Variable" müssen auf die neuen Klassennamen gemappt werden
- Kap. 7.4 (Objekt- und Lebenszyklusmodell) — Claims, Axiome, Gegenclaims neu bewerten
- Kap. 7.5 (Prüfverfahren) — Anforderungen gegen das neue Modell validieren
- Kap. 21 (Wirkmodell-Autor-Workflow) — Workflows gegen neue Klassen prüfen
