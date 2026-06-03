# Narrative Model — Konsolidierte Spezifikation

**Datum:** 2026-06-03
**Status:** Konsolidiert
**Quellen:** current-narrative-domain.md, current-claim.md,
current-import.md, 2026-06-03-actor.md, 2026-06-03-claim.md,
kap-06-systemarchitektur.md (updated)

---

## 1. Überblick

Das narrative Modell besteht aus drei Schichten:

1. **DocumentNode-Baum** — Textstruktur (Composite Pattern)
2. **DocumentAsset** — Objekte außerhalb des Baums (Actor, Claim, Ressourcen)
3. **DocumentLink** — Graphlayer für Querverbindungen

---

## 2. Dokumentmodell

### DocumentNode — der Composite-Baum

```python
@dataclass
class DocumentNode:
    id: UUID
    narrativ_id: UUID
    version_id: UUID
    parent_id: UUID | None          # None = Root-Knoten
    node_type: NodeType
    structural_role: StructuralRole | None = None
    presentation_role: PresentationRole | None = None
    audience: Audience = Audience.PUBLIC
    content: str | None = None
    position: int = 0

class NodeType(str, Enum):
    WORK      = "work"
    PART      = "part"
    CHAPTER   = "chapter"
    SECTION   = "section"
    PARAGRAPH = "paragraph"
    SENTENCE  = "sentence"
    STRING    = "string"
    CHARACTER = "character"   # Leaf

class StructuralRole(str, Enum):
    MAIN_TEXT    = "main_text"
    TITLE        = "title"
    SUBTITLE     = "subtitle"
    PREFACE      = "preface"
    MOTTO        = "motto"
    DEDICATION   = "dedication"
    APPENDIX     = "appendix"
    FOOTNOTE     = "footnote"
    BIBLIOGRAPHY = "bibliography"
    GLOSSARY     = "glossary"

class PresentationRole(str, Enum):
    HEADING     = "heading"
    EMPHASIS    = "emphasis"
    BLOCK_QUOTE = "block_quote"
    CAPTION     = "caption"
    NORMAL      = "normal"

class Audience(str, Enum):
    PUBLIC      = "public"
    AUTHOR_ONLY = "author_only"
    CO_AUTHORS  = "co_authors"
    EDITORIAL   = "editorial"
```

### DocumentAsset — außerhalb des Baums

Lebt außerhalb des Baums. Kann von beliebig vielen DocumentNodes
referenziert werden ohne kopiert zu werden.

```python
@dataclass
class DocumentAsset:
    id: UUID
    narrativ_id: UUID
    asset_type: str     # 'actor', 'claim', 'map', 'image', 'file',
                        # 'note', 'todo', 'comment', 'research_ref', ...
    content: str | None = None
    url: str | None = None
    audience: Audience = Audience.PUBLIC
    created_by: UUID = None
```

### DocumentLink — der Graphlayer

Beziehungen die keine Containment-Beziehungen sind. Von beiden Seiten
aus sichtbar und abfragbar.

```python
@dataclass
class DocumentLink:
    id: UUID
    source_id: UUID
    source_type: str    # 'document_node', 'document_asset'
    target_id: UUID
    target_type: str    # 'document_node', 'document_asset'
    link_type: LinkType
    created_by: UUID

class LinkType(str, Enum):
    REFERS_TO  = "refers_to"
    ANNOTATION = "annotation"
    CROSS_REF  = "cross_ref"
    ASSET_REF  = "asset_ref"
```

---

## 3. Narrativ und Szene (aktueller Stand)

**Hinweis:** Die aktuelle Implementierung nutzt noch nicht das
DocumentNode-Modell. Sie verwendet `Narrative` + `Scene` als direkte
Domain-Objekte. Migration zur DocumentNode-Architektur steht aus.

```python
@dataclass
class Narrative:
    id: str | None
    title: str
    causal_model_id: str | None = None
    scenes: list[Scene] = field(default_factory=list)
    actors: list[Actor] = field(default_factory=list)

@dataclass
class Scene:
    id: str | None
    title: str
    text: str
    position: int
```

Datenbankschema: `narrative` + `narrative_units` (Polymorphtabelle,
aktuell nur `typ='scene'` genutzt).

**Architekturentscheidung: Fragment wird gestrichen.**
Explizit entschieden: `Fragment` hat keine eigene Funktion im Composite Pattern —
es hat keinen eigenen Lebenszyklus, keine eigenen Operationen und kein Verhalten
das sich von `Scene` unterscheidet. Die Hierarchie lautet deshalb:

```
Werk → Teil → Kapitel → Szene (Leaf)
```

Claims, Akteure und Zeitachsen hängen an der **Szene** als atomare Einheit.
`Fragment` wird aus dem `typ`-Enum der `narrative_units`-Tabelle entfernt
sobald die Migration zu `document_nodes` (Phase 2) stattfindet.

---

## 4. Actor

### Zielarchitektur

```python
@dataclass
class Actor:
    """DocumentAsset mit asset_type = 'actor'."""
    id: UUID
    label: str                          # Anzeigename der Figur
    actor_type: ActorType               # Typ der Figur
    entity_ref: "Entity | None"         # optionaler Link ins Wirkgefüge
    notes: str | None                   # immer AuthorOnly
    audience: Audience = Audience.PUBLIC

    def occurrences(self, links: list[DocumentLink]) -> list[DocumentNode]:
        """Alle DocumentNodes die auf diesen Actor verweisen. Abgeleitet."""
        return [
            link.source for link in links
            if link.target_id == self.id and link.target_type == "actor"
        ]

class ActorType(str, Enum):
    INDIVIDUAL   = "individual"
    ORGANISATION = "organisation"
    GROUP        = "group"
    INSTITUTION  = "institution"
    ABSTRACT     = "abstract_entity"
```

**Drei Verantwortlichkeiten:**
1. Wirkgefüge-Brücke — optionaler Link zu Entity
2. Navigationshilfe — occurrences() zeigt alle Vorkommen im Text
3. Autorennotiz — immer AuthorOnly, unabhängig von audience

**Verhältnis zu Entity:**
- Rein narrative Figur (Maria Schneider): `entity_ref = None`
- Figur repräsentiert modellierten Akteur (Zentralbank): `entity_ref → Entity`

### Aktueller Stand

Aktuell: Actor per Narrativ (`narrative_actors`-Tabelle, gehört zu einem
Narrativ). Zielarchitektur: Actor als plattformweites DocumentAsset das
via DocumentLink referenziert wird.

**Migrationslücke:** Fundamentale Architekturänderung — Actor wechselt
von narrativ-gebunden zu plattformweit. Bestehende `narrative_actors`-
Einträge müssen zu DocumentAssets migriert werden.

---

## 5. Claim

### ClaimStatus

```python
class ClaimStatus(Enum):
    DRAFT      = "draft"       # Default — kein Wirkgefüge-Link
    LINKED     = "linked"      # Entsprechung im Wirkgefüge vorhanden
    UNRESOLVED = "unresolved"  # Bewusst offene Lücke
```

### Zielarchitektur

```python
@dataclass
class Claim:
    """DocumentAsset mit asset_type = 'claim'."""
    id: UUID
    label: str
    text: str | None                    # ursprünglicher Wortlaut
    status: ClaimStatus = ClaimStatus.DRAFT
    wirkgefuege_ref: "CausalComponent | None" = None
    confidence: float | None = None     # LLM-Extraktions-Konfidenz, 0.0–1.0
    notes: str | None = None            # immer AuthorOnly
    audience: Audience = Audience.PUBLIC

    def occurrences(self, links: list[DocumentLink]) -> list[DocumentNode]:
        """Alle DocumentNodes die auf diesen Claim verweisen. Abgeleitet."""
        return [
            link.source for link in links
            if link.target_id == self.id and link.target_type == "claim"
        ]
```

**Vier Verantwortlichkeiten:**
1. Wirkgefüge-Brücke — Link zur formalen Entsprechung
2. Navigationshilfe — occurrences()
3. Autorennotiz — immer AuthorOnly
4. Status — zeigt Formalisierungsstand an

**Wirkgefüge-Entsprechungen:**

| Claim-Typ | Wirkgefüge-Entsprechung |
|---|---|
| Zustandsaussage | Slot + Zustand |
| Kausalaussage | CausalRelation |
| Definitionsaussage | DefinitoryRelation |
| Grundannahme | EpistemicStatus = AXIOMATIC |

**Veröffentlichungsregel:**
- LINKED → erscheint als bestätigter Claim im Transparenzbericht
- UNRESOLVED → erscheint als offener Befund (nicht-kritisch)
- DRAFT → blockiert Veröffentlichung als kritischer Befund

### Aktueller Stand

Aktuell: Claim als reines LLM-Analyseprodukt mit `text`, `typ`, `confidence`.
Kein ClaimStatus, kein Wirkgefüge-Link, keine DocumentLink-Navigation.

Claim-Typen (aktuelle Implementierung, reine String-Werte):
`empirischer_claim`, `kausaler_claim`, `definitorischer_claim`,
`normativer_claim`, `prognostischer_claim`, `kontrafaktischer_claim`,
`methodischer_claim`, `unsicherheitsclaim`

---

## 6. Import

### Aktueller Stand

```
NarrativeImportService
  ├── NarrativeParser (Port)
  │     └── MarkdownNarrativeParser    — Szenen via ### Szene N
  └── NarrativeFileParser (Port)
        └── DocxNarrativeParser        — Szenen via ^Szene\s+\d+$ Absätze
```

API: `POST /narratives/import {path: str}` — Server-Dateisystempfad.

**Was fehlt:**
- Browser-Dateiupload
- Scrivener-Format
- Automatische Erstanalyse nach Import
- JATS XML, BibTeX, OWL/RDF (→ Wirkgefüge-Import, separates Thema)

---

## 7. Offene Todos

| Thema | Status |
|---|---|
| Migration narrative_units → document_nodes | Offen |
| Migration narrative_actors → document_assets | Offen |
| ActorType in Zielarchitektur bestätigen | ✅ Aufgenommen |
| confidence auf Claim in Zielarchitektur | ✅ Aufgenommen |
| Browser-Dateiupload | Offen |
| Erstanalyse nach Import | Offen |
| DocumentLink-Navigation für Actor + Claim | Offen |
| Szenenbearbeitung (PATCH/PUT) | Offen |
| Szene-Actor-Verknüpfung | Offen |
