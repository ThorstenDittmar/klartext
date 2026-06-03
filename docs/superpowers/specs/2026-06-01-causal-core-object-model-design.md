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
  │           └── DefinitoryRelation
  ├── CausalMixin
  └── CausalComposite (abstrakt)
        ├── CausalModel
        └── CausalModelFederation

Außerhalb der CausalComponent-Hierarchie (keine Modellbausteine):
  Zustand       — Wert eines Slots, immer relativ zu einem Slot
  Condition     — abstrakte Basisklasse für Bedingungen (kein CausalComponent)
    ├── Precondition   — Bedingung die erfüllt sein muss (vor einem Übergang)
    └── Postcondition  — erwarteter Zustand nach einem Übergang
  Source        — externe Referenz, nicht Teil des Wirkgefüges

ModelIssue (eigene Objektstruktur, kein CausalComponent):
  ├── NamespaceConflict   — gleicher Bezeichner, verschiedene Elemente
  ├── ScopeConflict       — unvereinbare Geltungsbereiche
  └── ConditionConflict   — unvereinbare Bedingungen

Hinweis: Precondition und Postcondition sind inhaltlich mit Zeitscheiben
verknüpft und werden dort vollständig spezifiziert (T-09). Die Struktur
von Condition ist jedoch bereits klar.
```

---

## 4. Klassen im Detail

### CausalComponent (abstrakt)
Die gemeinsame Basisklasse aller Modellelemente. Definiert das Protokoll, das alle Subklassen erfüllen müssen — unabhängig davon, ob sie atomar, zusammengesetzt oder ein Fragment sind.

**Funktion:** Jedes Element im Wirkgefüge ist ein CausalComponent. Das ermöglicht einheitliche Traversierung, Prüfung und Abfrage über alle Ebenen der Composite-Hierarchie hinweg.

**Protokoll (abstrakte Methoden):**

Jede Methode existiert in zwei Varianten — direkt (nur das Element selbst) und rekursiv (Element + alle Kinder):

```python
# Direct — own elements only:
def get_own_slots(self) -> list[Slot]: ...
def get_own_relations(self) -> list[Relation]: ...
def get_own_conditions(self) -> list[Condition]: ...

# Recursive — own + all children:
def get_slots(self) -> list[Slot]: ...
def get_relations(self) -> list[Relation]: ...
def get_conditions(self) -> list[Condition]: ...

# Own namespace (None for CausalLeaf, own namespace for CausalMixin/CausalComposite):
def get_namespace(self) -> Namespace | None: ...

def is_complete(self) -> bool: ...
```

Für `CausalLeaf`: `get_*()` = `get_own_*()` — keine Kinder vorhanden.  
Für `CausalComposite` und `CausalMixin`: `get_*()` = `get_own_*()` + rekursiv alle Kinder.

**Kontextualisierungsprinzip:**
Components sind kontextfrei — sie kennen ihren Container nicht. Alle semantischen Operationen (Namespace-Auflösung, Scope-Prüfung, Vollständigkeitsprüfung, Prüfverfahren) laufen immer **top-down**: sie starten am Container und traversieren nach unten. Eine Component kann nicht fragen "in welchem Modell bin ich?" — das Modell fragt "welche Components gehören zu mir?"

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
- `reference: Source | None` — optionaler Verweis auf externes Quelldokument
- `derivation_source: Relation | None` — Relation, aus der dieses Element abgeleitet wird (`None` wenn axiomatic oder incomplete)

### Zustand
Ein konkreter Wert eines Slots. Eigenständiges Objekt, aber **kein CausalComponent** — er existiert immer relativ zu einem Slot und ist kein eigenständiger Modellbaustein, der im Composite-Baum platziert wird.

Da ein Zustand jedoch selbst epistemisch bewertet und als axiomatisch markiert werden kann (z.B. "dieser Wert gilt als gesetzt"), trägt er dieselben Statusattribute wie ein CausalComponent — allerdings nicht durch Vererbung, sondern als explizite Wiederholung.

**Attribute:**
- `value: str | float | int` — qualitativer oder quantitativer Wert
- `slot: Slot` — Referenz auf den zugehörigen Slot
- `epistemic_status: EpistemicStatus`

- `reference: Source | None` — optionaler Verweis auf externes Quelldokument
- `derivation_source: Relation | None` — Relation, aus der dieses Element abgeleitet wird (`None` wenn axiomatic oder incomplete)

### Entity
Subtyp von `Slot`. Repräsentiert einen Akteur (Organisation, Gruppe, Institution). Kernmerkmal: Agency — die Fähigkeit zu handeln, zu entscheiden, zu beeinflussen.

Zustände einer Entity beschreiben Kapazität oder Status ("handlungsfähig", "aufgelöst"), keine Messwerte.

### Relation (abstrakt)
Eine gerichtete Beziehung zwischen Modellelementen. Ist ein `CausalLeaf` — enthält selbst keine weiteren Komponenten. Subklassen definieren ihre eigenen Endpoint-Typen.

**Zusätzliche Attribute** (über CausalComponent hinaus):
- `reference: Source | None` — optionaler Verweis auf externes Quelldokument
- `derivation_source: Relation | None` — Relation, aus der dieses Element abgeleitet wird (`None` wenn axiomatic oder incomplete)

### CausalRelation
Spezialisiert `Relation`. Beschreibt einen gerichteten Wirkzusammenhang zwischen zwei (Slot + Zustand)-Paaren.

**Zusätzliche Attribute:**
- `source_condition: tuple[Slot, Zustand]` — Quellbedingung
- `target_effect: tuple[Slot, Zustand]` — Zieleffekt
- `mechanism: str` — Wirkmechanismus
- `polarity: Polarity` — positiv / negativ
- `strength: float | None`
- `uncertainty: float | None`
- `preconditions: list[Precondition]`

### DefinitoryRelation
Spezialisiert `Relation`. Beschreibt, was ein Slot **bedeutet** — nicht was er verursacht. Atemporal und konzeptbasiert, im Gegensatz zur dynamischen `CausalRelation`.

Grundlage für referentielle Integrität: alle Slots in `components` müssen im Modell existieren.

**Zusätzliche Attribute:**
- `defined_slot: Slot` — der Slot, der definiert wird
- `components: list[Slot]` — die Slots, aus denen er definiert wird
- `definition_type: DefinitionType` — COMPOSITIONAL / OPERATIONAL / EQUIVALENCE

> **Offener Punkt (T-22):** Abgrenzung zu `CausalRelation` mit `AXIOMATIC` noch zu validieren. Möglicherweise kann `DefinitoryRelation` als Sonderfall ausgedrückt werden.

### Condition (abstrakt)
Abstrakte Basisklasse für alle Bedingungen. Kein CausalComponent — Bedingungen sind keine eigenständigen Modellbausteine, sondern Eigenschaften von Relationen und Composites.

```python
class Condition(ABC):
    @abstractmethod
    def is_compatible_with(self, other: Condition) -> bool:
        """Returns True if this condition can coexist with the other condition
        without contradiction. Used by add() to validate new components."""
        ...
```

### Precondition
Spezialisiert `Condition`. Eine Bedingung, die erfüllt sein muss, damit eine Relation oder ein Prozess gültig angewendet werden kann. Normative Claims ("sollte", "muss") werden als Preconditions modelliert.

Inhaltliche Spezifikation (insbesondere Verbindung zu Zeitscheiben) folgt in T-09.

### Postcondition
Spezialisiert `Condition`. Beschreibt einen erwarteten Zustand nach einem Übergang oder der Anwendung einer Relation.

Inhaltliche Spezifikation folgt in T-09.

### CausalMixin
Ein kohärentes, möglicherweise unvollständiges Fragment eines Wirkmodells. Wiederverwendbar — dasselbe Mixin kann in mehreren CausalModels eingebunden werden. Kann aus anderen CausalMixins und CausalLeafs zusammengesetzt werden, aber nie aus CausalComposites.

`is_complete()` gibt immer `False` zurück — ein Fragment ist per Definition kein vollständiges Modell.

**Enthält:** `CausalLeaf`, `CausalMixin`  
**Eigener Namespace:** ja  
**`_used_in: list[CausalModel | CausalModelFederation]`** — informativ, kein semantischer Einfluss. Zeigt dem Autor wo dieses Mixin genutzt wird. Wird beim `applies` gepflegt.

**Namespace-Auflösung beim `applies`:**

Wenn ein `CausalModel` ein `CausalMixin` einbindet, werden die Bezeichner des Mixins im Namespace des Containers sichtbar. Es gelten folgende Regeln:

| Situation | Ergebnis |
|---|---|
| Bezeichner nur im Mixin | ✓ Mixin-Eintrag gilt direkt im Container |
| Bezeichner im Container (eigener Eintrag) UND im Mixin | Container gewinnt — Mixin wird überschattet. Mixin bleibt unverändert. UI informiert den Autor. |
| Bezeichner in zwei Mixins, nicht im Container selbst | `NamespaceCollisionError` — Autor muss explizite Definition im Container anlegen, die dann dem Container gehört. |

**Qualifizierter Zugriff** ist immer möglich: `ClimateMixin::co2_concentration` — insbesondere für externe Referenzen aus anderen Modellen.

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

### add-Operation

`add` ist die zentrale Mutationsmethode auf allen CausalComposites. Sie erzwingt zwei Invarianten vor dem Einhängen:

```python
def add(self, component: CausalComponent) -> None:
    """Add a component to this composite.

    Raises:
        TypeError: if the component type is not allowed in this container.
        NamespaceCollisionError: if the identifier already exists in this namespace.
        ScopeConflictError: if the component scope conflicts with an axiomatic container scope.
    """
    # 1. Type check — enforced by each subclass
    self._assert_type_allowed(component)

    # 2. Namespace collision
    if component.identifier in self._namespace:
        raise NamespaceCollisionError(
            identifier=component.identifier,
            existing=self._namespace[component.identifier],
            incoming=component,
        )

    # 3. Scope negotiation
    # TODO (T-18): scope negotiation logic is not yet fully specified.
    # Open questions: undefined vs universal scope, union vs intersection,
    # list vs lowest-common-ancestor for spatial/disciplinary dimensions.
    if self.scope is not None and not self.scope.is_compatible(component.scope):
        raise ScopeConflictError(
            container_scope=self.scope,
            component_scope=component.scope,
        )

    # 4. Condition compatibility check
    new_conditions = component.get_conditions()
    existing_conditions = self.get_conditions()
    for new_cond in new_conditions:
        for existing_cond in existing_conditions:
            if not new_cond.is_compatible_with(existing_cond):
                raise ConditionConflictError(
                    new_condition=new_cond,
                    existing_condition=existing_cond,
                )

    # 5. Add
    self._components.append(component)
```

**Scope-Verhalten beim add:**

| Container-Scope | Komponenten-Scope | Ergebnis |
|---|---|---|
| gesetzt, kompatibel | beliebig | ✓ OK |
| gesetzt, inkompatibel | beliebig | `ScopeConflictError` |
| nicht gesetzt (`None`) | beliebig | ✓ OK — aber `is_complete() = False` |

> **Offener Punkt (T-18):** Vollständiges Scope-Verhalten beim add noch nicht spezifiziert. Ungeklärte Fragen: "nicht definiert" vs. "unendlich/universal"; wie trägt ein Element seinen Scope zum Container bei (Union, Schnittmenge, Liste, oder nächsthöhere Hierarchieebene)?

**Fehlerbehandlung in der UI:**
- `NamespaceCollisionError` → UI erzeugt ein `NamespaceConflict`-Objekt, informiert den Autor
- `ScopeConflictError` → UI erzeugt ein `ScopeConflict`-Objekt, informiert den Autor
- `ConditionConflictError` → UI erzeugt ein `ConditionConflict`-Objekt, informiert den Autor

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

Ein explizit gesetzter Scope wirkt als Einschränkung beim `add`. Ist kein Scope gesetzt (`None`), blockiert das `is_complete()`, erlaubt aber weiteres Arbeiten am Modell.

> **Offener Punkt (T-18):** Unterscheidung zwischen "nicht definiert" und "unendlich/universal" noch nicht spezifiziert. Wie sich Scopes beim add zusammensetzen (zeitlich, räumlich, disziplinär) ist ebenfalls noch offen.

**Schlüsselmethoden:**

```python
def is_compatible(self, other: Scope) -> bool:
    """True if this scope and other overlap in all defined dimensions."""
    ...
```

---

## 8. EpistemicStatus

`EpistemicStatus` beschreibt den **Transparenzstatus** eines Elements. Die Plattform ist keine Wahrheitsmaschine — es geht nicht um externe Wahrheit, sondern um interne Modellstruktur.

`DERIVED` wird nicht gespeichert, sondern berechnet. Der Autor setzt explizit nur `AXIOMATIC`. Alles andere folgt aus der Struktur.

```python
class EpistemicStatus(Enum):
    INCOMPLETE = "incomplete"  # default — not yet formalized
    AXIOMATIC  = "axiomatic"   # set as premise, not derived here
```

Die berechneten Eigenschaften auf jedem `CausalComponent`:

```python
@property
def is_axiomatic(self) -> bool:
    return self.epistemic_status == EpistemicStatus.AXIOMATIC

@property
def is_derived(self) -> bool:
    """An element is derived if it has an explicit derivation source."""
    return self.derivation_source is not None

@property
def is_incomplete(self) -> bool:
    return not self.is_axiomatic and not self.is_derived

@property
def is_complete(self) -> bool:
    """Complete if axiomatic (chain anchor) or derived from a complete source."""
    if self.is_axiomatic:
        return True
    if self.is_derived:
        return self.derivation_source.is_complete
    return False  # incomplete
```

**Axiomsraum:** abgeleitete Menge — alle Elemente eines CausalModels mit `epistemic_status = AXIOMATIC`.

**`is_complete()` auf CausalModel** gibt `True` zurück, wenn kein enthaltenes Element `is_incomplete` ist und alle `is_derived`-Ketten bis zu einem `AXIOMATIC`-Element aufgelöst sind.

---

## 9. Source

Externes Objekt — kein Teil des Wirkgefüges. Jeder Slot und jede Relation kann optional auf eine Source verweisen. Die Referenz zeigt auf die kleinstmögliche semantische Einheit im Quelldokument (paragraph, measurement series, table).

---

## 10. ModelIssue

`ModelIssue` ist eine eigenständige Objektstruktur — kein `CausalComponent`, nicht Teil des Modell-Inhalts. Ein `ModelIssue` beschreibt einen Zustand, der aufgelöst werden muss, bevor das Modell vollständig sein kann.

**Funktion:** Trennung zwischen Modellinhalt (Slots, Relationen) und Modellproblemen (Konflikte, Inkonsistenzen). Relationen sind gewünschte, dauerhafte Modellelemente. Issues sind transient — sie sollen aufgelöst werden.

**Lebenszyklus:** `open → acknowledged → resolved`

```
ModelIssue (abstrakt)
  ├── NamespaceConflict   — gleicher Bezeichner, verschiedene Elemente im selben Namespace
  ├── ScopeConflict       — unvereinbare Geltungsbereiche
  └── ConditionConflict   — unvereinbare Bedingungen
```

**Gemeinsame Attribute:**
- `status: IssueStatus` — open / acknowledged / resolved
- `affected_components: list[CausalComponent]` — betroffene Elemente
- `detected_at: datetime`
- `resolved_at: datetime | None`

Issues werden vom Modell getrennt verwaltet — sie sind kein Teil des Namespace und beeinflussen `is_complete()`: ein Modell mit offenen Issues gibt `is_complete() = False` zurück.

---

## 11. Offene Todos

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
