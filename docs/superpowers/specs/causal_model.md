# Causal Model — Konsolidierte Spezifikation

**Datum:** 2026-06-03
**Status:** Konsolidiert aus mehreren Specs
**Quellen:** causal-core-object-model-design.md, scope.md, timeslice.md,
zustand-und-trend.md, precondition-postcondition.md,
t22-definitory-vs-causal.md, wirkgefuege-design-principles.md,
current-causal-model.md

---

## 1. Terminologie

| Begriff | Bedeutung |
|---|---|
| **Wirkgefüge** | Sprachlicher Oberbegriff für alle kausalen Konzepte. Keine Klasse. |
| **CausalModel** | Konkrete Top-Level-Klasse — eine versionierte, prüfbare Instanz. |

---

## 2. Designprinzipien

### Keine Wahrheitsmaschine
Die Plattform prüft ausschließlich interne Konsistenz, Vollständigkeit
und Transparenz. `EpistemicStatus` beschreibt den Transparenzstatus,
nicht externe Wahrheit. Kontrafaktische und spekulative Modelle sind
zulässig, sofern ihre Annahmen explizit sind.

### Semantische Operationen top-down
CausalComponents sind kontextfrei — sie kennen ihren Container nicht.
Alle semantischen Operationen (Namespace-Auflösung, Scope-Prüfung,
Vollständigkeitsprüfung) starten am Container und traversieren nach
unten. Kein `_container`-Attribut auf CausalComponent.

### Code immer auf Englisch
Alle Bezeichner (Klassen, Methoden, Variablen) sind Englisch.
Kommunikation mit dem User auf Deutsch.

### Explizitheit über Implizitheit
Mehrdeutigkeiten müssen als Varianten, Konflikte, Lücken oder offene
Fragen explizit ausgewiesen werden.

### Keine Claim-Klasse im Wirkgefüge
Claims existieren nicht als eigenständige Klasse. Jeder Claimtyp wird
auf bestehende Strukturen zurückgeführt. "Claim" bleibt dem Narrativ
vorbehalten.

| Claimtyp | Übersetzung ins Modell |
|---|---|
| Empirisch | Slot + Zustand + EpistemicStatus |
| Kausal | CausalRelation |
| Definitorisch | DefinitoryRelation |
| Normativ | Precondition auf einer Relation |
| Kontrafaktisch | Slot + Zustand mit AXIOMATIC |
| Methodisch | Slot + Zustand mit AXIOMATIC, optional Source |
| Unsicherheit | Attribut auf einem Element |

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

Außerhalb der Hierarchie (keine Modellbausteine):
  Zustand           — Wert eines Slots
  Condition (abstrakt)
    ├── Precondition
    └── Postcondition
  TimeSlice         — Zeitobjekt, lebt in Scope.temporal
  SpatialRegion     — Knoten in räumlicher Taxonomie
  Discipline        — Knoten in Disziplin-Taxonomie
  Scope             — Geltungsbereich (temporal + spatial + disciplinary)
  Source            — externe Referenz
  ModelIssue (abstrakt)
    ├── NamespaceConflict
    ├── ScopeConflict
    └── ConditionConflict
```

---

## 4. Gemeinsame Attribute aller CausalComponents

```python
# Auf jedem CausalComponent:
scope: Scope
epistemic_status: EpistemicStatus = EpistemicStatus.INCOMPLETE
```

---

## 5. Klassen im Detail

### CausalComponent (abstrakt)

Protokoll (abstrakte Methoden):

```python
def get_own_slots(self) -> list[Slot]: ...
def get_own_relations(self) -> list[Relation]: ...
def get_own_conditions(self) -> list[Condition]: ...
def get_slots(self) -> list[Slot]: ...        # rekursiv
def get_relations(self) -> list[Relation]: ... # rekursiv
def get_conditions(self) -> list[Condition]: ...# rekursiv
def get_namespace(self) -> Namespace | None: ...
def is_complete(self) -> bool: ...
```

### Slot

Benannter Platzhalter für einen beobachtbaren oder messbaren Wert.

```python
@dataclass
class Slot(CausalLeaf):
    identifier: str
    slot_type: SlotType
    reference: Source | None = None
    derivation_source: Relation | None = None
```

**Zustandsraum:** Der valide Wertebereich eines Slots wird durch `slot_type`
bestimmt. Trend-Werte wie `"steigend"` sind nur auf einem expliziten
Trend-Slot valide. Ein Messwert-Slot mit Trend-Wert ist ein
Modellierungsfehler.

### Entity

Subtyp von Slot. Repräsentiert Akteure mit Agency (Organisationen,
Institutionen, Gruppen). Zustände beschreiben Kapazität oder Status
("handlungsfähig", "aufgelöst"), keine Messwerte.

```python
@dataclass
class Entity(Slot):
    pass  # Gleiche Struktur wie Slot, andere semantische Bedeutung
```

### Zustand

Konkreter Wert eines Slots. Kein CausalComponent — existiert immer
relativ zu einem Slot.

```python
@dataclass
class Zustand:
    value: str | float | int
    slot: Slot
    epistemic_status: EpistemicStatus = EpistemicStatus.INCOMPLETE
    reference: Source | None = None
    derivation_source: Relation | None = None
```

**Zwei Slot-Typen:**

```
Messwert-Slot:  Slot(co2_concentration) → Zustand.value = 421.0    ✓
                Slot(co2_concentration) → Zustand.value = "steigend" ✗

Trend-Slot:     Slot(co2_trend)         → Zustand.value = "steigend" ✓
                Slot(co2_trend)         → Zustand.value = 421.0      ✗
```

**Hinweis zu EpistemicStatus.DERIVED:** DERIVED ist eine berechnete
Eigenschaft, kein explizit speicherbarer Wert. Ein Zustand gilt als
derived wenn `derivation_source is not None`. Das Enum kennt nur
INCOMPLETE und AXIOMATIC als explizite Werte.

### Relation (abstrakt)

```python
@dataclass
class Relation(CausalLeaf):
    identifier: str
    source: Slot
    target: Slot
    scope: Scope
    epistemic_status: EpistemicStatus = EpistemicStatus.INCOMPLETE
    reference: Source | None = None
    derivation_source: Relation | None = None
```

### CausalRelation

Gerichteter Wirkzusammenhang.

```python
@dataclass
class CausalRelation(Relation):
    mechanism: str | None = None
    polarity: Polarity | None = None       # positiv / negativ / ambivalent
    strength: float | None = None          # 0.0–1.0
    uncertainty: float | None = None       # 0.0–1.0
    source_condition: tuple[Slot, Zustand] | None = None
    target_effect: tuple[Slot, Zustand] | None = None
    preconditions: list[Precondition] = field(default_factory=list)
```

### DefinitoryRelation

Begriffliche Gleichsetzung. Atemporal, kein Mechanismus.

```python
@dataclass
class DefinitoryRelation(Relation):
    definition: str
```

**Abgrenzung von CausalRelation:**
- CausalRelation beantwortet: *Was bewirkt was?*
- DefinitoryRelation beantwortet: *Was bedeutet dieser Begriff?*
- Der Unterschied ist strukturell, nicht epistemisch (beide können AXIOMATIC sein).
- Abgrenzungsregel: Wenn ein Mechanismus benennbar ist → CausalRelation.
  Wenn es eine begriffliche Gleichsetzung ist → DefinitoryRelation.

**Risiko versteckter Axiome:** Eine Kausalaussage als DefinitoryRelation
zu tarnen ist ein Missbrauchspfad. Gegenmaßnahmen:
1. System warnt wenn eine DefinitoryRelation Slots berührt die in
   CausalRelationen als source_condition oder target_effect vorkommen.
2. Alle DefinitoryRelationen erscheinen explizit im Transparenzbericht.

### CausalMixin

Wiederverwendbares Fragment. Kann in mehreren Containern gleichzeitig leben.
Kennt seinen Container nicht.

```python
@dataclass
class CausalMixin(CausalComponent):
    identifier: str
    namespace: Namespace
    components: list[CausalComponent] = field(default_factory=list)
```

### CausalModel

Top-Level-Container. Enthält Slots, Entities und Relationen.

```python
@dataclass
class CausalModel(CausalComposite):
    identifier: str
    title: str
    scope: Scope
    status: CausalModelStatus = CausalModelStatus.PRIVATE
    namespace: Namespace = field(default_factory=Namespace)
    components: list[CausalComponent] = field(default_factory=list)
    preconditions: list[Precondition] = field(default_factory=list)
    postconditions: list[Postcondition] = field(default_factory=list)

    def add(self, component: CausalComponent) -> None:
        """Prüft Scope-Kompatibilität und Namespace-Konflikte vor dem Einfügen."""
        ...

    def axiomatic_space(self) -> list[CausalComponent]:
        """Alle Elemente mit epistemic_status = AXIOMATIC."""
        ...

    def is_complete(self) -> bool:
        """True wenn kein Element INCOMPLETE und alle DERIVED-Ketten aufgelöst."""
        ...

    def get_active_postconditions(
        self, from_federation: CausalModelFederation
    ) -> list[Postcondition]:
        """Alle Postconditions die aus früheren Scheiben propagieren."""
        ...
```

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

### CausalModelFederation

Verbindet mehrere CausalModels. Verantwortlich für Übergangsprüfungen
zwischen Zeitscheiben.

```python
class CausalModelFederation(CausalComposite):
    def get_successors(self, model: CausalModel) -> list[CausalModel]: ...
    def validate_transition(
        self, predecessor: CausalModel, successor: CausalModel
    ) -> list[ConditionConflict]: ...
    def get_active_postconditions(
        self, at_model: CausalModel
    ) -> list[Postcondition]: ...
```

Noch nicht vollständig spezifiziert.

---

## 6. Scope

Drei explizite Objekte mit eigener Hierarchie und Prüflogik.

```python
@dataclass
class TimeSlice:
    start: date
    end: date
    identifier: str = field(default="")

    def __post_init__(self):
        if not self.identifier:
            self.identifier = f"{self.start.year}-{self.end.year}"

    def includes(self, other: "TimeSlice") -> bool:
        return self.start <= other.start and other.end <= self.end

    def intersects(self, other: "TimeSlice") -> bool:
        return self.start <= other.end and other.start <= self.end


@dataclass
class SpatialRegion:
    identifier: str
    parent: "SpatialRegion | None" = None

    def includes(self, other: "SpatialRegion") -> bool:
        current = other
        while current is not None:
            if current.identifier == self.identifier:
                return True
            current = current.parent
        return False


@dataclass
class Discipline:
    identifier: str
    parent: "Discipline | None" = None

    def includes(self, other: "Discipline") -> bool:
        current = other
        while current is not None:
            if current.identifier == self.identifier:
                return True
            current = current.parent
        return False


@dataclass
class Scope:
    temporal:     TimeSlice     | None = None
    spatial:      SpatialRegion | None = None
    disciplinary: Discipline    | None = None

    def includes(self, other: "Scope") -> bool:
        """True if other lies entirely within this scope (für add()-Prüfung)."""
        if self.temporal is not None and other.temporal is not None:
            if not self.temporal.includes(other.temporal):
                return False
        if self.spatial is not None and other.spatial is not None:
            if not self.spatial.includes(other.spatial):
                return False
        if self.disciplinary is not None and other.disciplinary is not None:
            if not self.disciplinary.includes(other.disciplinary):
                return False
        return True

    def is_compatible(self, other: "Scope") -> bool:
        """True if scopes overlap in all defined dimensions (für Konfliktprüfung)."""
        if self.temporal is not None and other.temporal is not None:
            if not self.temporal.intersects(other.temporal):
                return False
        return True

    def is_complete(self) -> bool:
        return (
            self.temporal is not None and
            self.spatial is not None and
            self.disciplinary is not None
        )
```

**Verhalten beim add():**
1. Beide Scopes gesetzt → `composite.scope.includes(component.scope)`.
   Fehlschlag → `ScopeConflict`.
2. Einer oder beide Scopes fehlen → add() erlaubt, aber INCOMPLETE.

**Nicht definiert ≠ universal:** `None` bedeutet INCOMPLETE, nicht "gilt überall".
Universal wäre ein explizit gesetzter maximaler Scope.

---

## 7. Zeitscheiben und Zeitscheiben-Verkettung

Ein CausalModel mit gesetztem `scope.temporal` ist eine Zeitscheibe.
Zeitscheiben sind diskret und überlappen sich nicht im selben Pfad.
Auf eine Zeitscheibe können mehrere alternative Folge-Scheiben folgen (Szenarios).

Pre- und Postconditions liegen am CausalModel — nicht an der TimeSlice.
Die TimeSlice ist ein reines Zeitobjekt ohne Modellkenntnis.

### Übergangsregeln

- **Konsumiert:** Postcondition N + Precondition N+1, gleicher Slot,
  kompatibler Zustand → Übergang valid, Postcondition endet.
- **Konflikt:** gleicher Slot, inkompatibler Zustand → ConditionConflict.
- **Propagiert:** keine Precondition für diesen Slot → UI-Hinweis,
  Postcondition läuft weiter.

### Propagationsregel
Unbegrenzte Vorwärtspropagation bis zur expliziten Konsumtion durch Precondition.

---

## 8. Precondition und Postcondition

```python
@dataclass
class Condition:
    slot: Slot
    state: Zustand
    scope: Scope

@dataclass
class Precondition(Condition):
    """Konsumiert eine matchende Postcondition und stoppt deren Propagation."""
    pass

@dataclass
class Postcondition(Condition):
    """Propagiert vorwärts bis zur Konsumtion durch Precondition."""
    pass
```

**Abgrenzung zu source_condition:**
`CausalRelation.source_condition` = direkte Ursache (löst Relation aus).
`Precondition` = Kontextbedingung (muss gelten, ist nicht Ursache).

---

## 9. EpistemicStatus

```python
class EpistemicStatus(Enum):
    INCOMPLETE = "incomplete"  # default — noch nicht formalisiert
    AXIOMATIC  = "axiomatic"   # als Prämisse gesetzt, nicht hergeleitet
```

DERIVED ist eine berechnete Eigenschaft, kein speicherbarer Wert:
- `is_derived: bool` = `derivation_source is not None`
- `is_incomplete: bool` = `not is_axiomatic and not is_derived`

Der **Axiomsraum** ist die abgeleitete Menge aller Elemente mit AXIOMATIC.

---

## 10. Namespace

Hierarchisch, typisiert. Jeder Container hat einen eigenen Namespace.
CausalLeafs erben vom Container.

Grundregel: Ein Bezeichner existiert genau einmal pro Namespace.
Qualifizierte Namen für containerübergreifende Referenzen: `CausalModel::identifier`

Namespace als eigenständige Klasse noch nicht spezifiziert (offen).

---

## 11. ModelIssue

```python
class ModelIssue:
    status: IssueStatus  # open → acknowledged → resolved
    affected_components: list[CausalComponent]
    detected_at: datetime
    resolved_at: datetime | None

class NamespaceConflict(ModelIssue): ...
class ScopeConflict(ModelIssue): ...
class ConditionConflict(ModelIssue):
    postcondition: Postcondition
    precondition: Precondition
```

Offene Issues setzen `CausalModel.is_complete() = False`.

---

## 12. Source

Externes Objekt, kein Teil des Wirkgefüges. Jeder Slot und jede
Relation kann optional auf eine Source verweisen. Referenz zeigt auf
kleinstmögliche semantische Einheit (Paragraph, Messreihe, Tabelle).

---

## 13. Aktueller Implementierungsstand (Phase 1)

Die aktuelle Implementierung ist eine bewusste Vereinfachung.
Zur Zielarchitektur: siehe Abschnitte 3–12 oben.

**Was implementiert ist:**
- `CausalModel` als Container mit Titel und Status
- `Axiom` als eigene Klasse (konzeptionell = Element mit AXIOMATIC)
- `CausalModelStatus` vollständig
- API: GET/POST /causal-models, POST /causal-models/{id}/axioms
- Konsistenzprüfung via Claude API: POST /causal-models/{id}/check-consistency

**Was noch fehlt:**
- CausalComponent-Hierarchie (Slot, Relation, Zustand)
- EpistemicStatus als Enum
- Scope auf Modellelementen
- CausalModelFederation
- CausalMixin
- Versionierung

Datenbankschema: `causal_models` + `model_elements` (Polymorphtabelle,
aktuell nur `typ='axiom'` genutzt).

---

## 14. Offene Todos

| # | Status | Thema |
|---|---|---|
| T-09 | ✅ Geschlossen | Trend = eigenständiger Slot. Zwischenschritte nicht modelliert. |
| T-10 | Offen | Prüfung: Slots gleicher Bezeichner + referentielle Integrität |
| T-11 | Offen | Import: granulare Verknüpfung auf Absatz-/Messreihenebene |
| T-12 | Offen | Scope: sachliche und methodische Dimension |
| T-13 | Weitgehend geschlossen | Scope als eigenständiges Objekt — durch scope.md beantwortet |
| T-14 | Offen | Modell-Rating (System + Community) |
| T-15–T-17 | Offen | UI-Feedback (nach Konzeptionsabschluss) |
| T-18 | ✅ Geschlossen | Scope-Verhalten beim add() — durch scope.md beantwortet |
| T-19 | Offen | Prüfungen: Namespace-Shadowing durch CausalMixin |
| T-20 | Offen | UI: Namespace-Konflikte beim Einbinden von CausalMixin |
| T-21 | Geparkt | Versionierung — nach praktischer Erfahrung |
| T-22 | ✅ Geschlossen | DefinitoryRelation vs CausalRelation AXIOMATIC |
| T-23 | ✅ Geschlossen | TimeSlice — durch timeslice.md + scope.md beantwortet |
| — | Offen | CausalModelFederation vollständig spezifizieren |
| — | Offen | Namespace als Klasse spezifizieren |
| — | Offen | CausalModel.applies(), resolve(identifier) konkret |
