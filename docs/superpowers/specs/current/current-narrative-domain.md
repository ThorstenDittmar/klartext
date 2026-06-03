# Spec: Narrative Domain — aktueller Implementierungsstand

**Datum:** 2026-05-29
**Status:** Implementiert
**Scope:** Narrative, Scene, Actor — die narrative Seite des Systems.
Beschreibt was heute im Code existiert, nicht die Zielarchitektur.

---

## Überblick

Das Narrativ ist der zentrale Container der narrativen Seite. Es hält
eine geordnete Liste von Szenen und eine Liste von Akteuren. Optional
ist es mit einem CausalModel verknüpft.

Die drei Objekte sind bewusst einfach gehalten. Sie bilden keine
DocumentAsset/DocumentNode-Hierarchie (→ Zielarchitektur) und haben
keinen eigenen Lebenszyklus mit Status-Tracking.

---

## Narrative

### Attribute

| Attribut | Typ | Beschreibung |
|---|---|---|
| `id` | `str \| None` | UUID, nach Persistierung gesetzt |
| `title` | `str` | Nicht-leer, Pflichtfeld |
| `causal_model_id` | `str \| None` | FK auf CausalModel; `None` wenn nicht verknüpft |
| `scenes` | `list[Scene]` | Geordnete Szenen-Liste |
| `actors` | `list[Actor]` | Akteure des Narrativs |

### Factory Methods

```python
Narrative.create(title: str) -> Narrative
    # Pflicht: title nicht leer (NarrativeValidationError)

Narrative.from_record(record: dict) -> Narrative
    # Felder: id, title, causal_model_id (optional)
```

### Mutationen

```python
narrative.add_scene(scene: Scene) -> None
narrative.add_actor(actor: Actor) -> None
narrative.remove_actor(actor_id: str) -> None
narrative.link_to_causal_model(causal_model_id: str) -> None
    # Pflicht: causal_model_id nicht leer (NarrativeValidationError)
```

### Datenbank

Tabelle: `narrative`

| Spalte | Typ | Anmerkung |
|---|---|---|
| `id` | UUID PK | |
| `title` | TEXT NOT NULL | |
| `causal_model_id` | UUID | FK → `causal_models.id`, nullable |
| `status` | TEXT | Default `'private'`; wird aktuell nicht genutzt |
| `created_at` | TIMESTAMPTZ | |

---

## Scene

### Attribute

| Attribut | Typ | Beschreibung |
|---|---|---|
| `id` | `str \| None` | UUID, nach Persistierung gesetzt |
| `title` | `str` | Nicht-leer, Pflichtfeld |
| `text` | `str` | Nicht-leer, Pflichtfeld |
| `position` | `int` | Reihenfolge innerhalb des Narrativs, beginnt bei 1 |

### Factory Methods

```python
Scene.create(title: str, text: str, position: int) -> Scene
    # Pflicht: title und text nicht leer (SceneValidationError)

Scene.from_record(record: dict) -> Scene
    # Felder: id, title, text, position
```

### Datenbank

Tabelle: `narrative_units`

| Spalte | Typ | Anmerkung |
|---|---|---|
| `id` | UUID PK | |
| `narrative_id` | UUID NOT NULL | FK → `narrative.id` ON DELETE CASCADE |
| `typ` | TEXT | CHECK: `'work','part','chapter','scene','fragment'`; wir verwenden nur `'scene'` |
| `title` | TEXT | |
| `content` | TEXT | |
| `position` | INTEGER NOT NULL | |
| `parent_id` | UUID | FK → `narrative_units.id`; aktuell immer NULL |
| `created_at` | TIMESTAMPTZ | |

**Hinweis:** `narrative_units` ist die selbstreferentielle Baumtabelle der
Zielarchitektur (Werk → Teil → Kapitel → Szene → Fragment). Aktuell
nutzen wir sie ausschließlich mit `typ='scene'` und `parent_id=NULL` —
eine flache Liste ohne Hierarchie.

---

## Actor

### ActorType

```python
class ActorType(str, Enum):
    INDIVIDUAL   = "individual"
    ORGANISATION = "organisation"
    GROUP        = "group"
    INSTITUTION  = "institution"
    ABSTRACT     = "abstract_entity"
```

### Attribute

| Attribut | Typ | Beschreibung |
|---|---|---|
| `id` | `str \| None` | UUID, nach Persistierung gesetzt |
| `name` | `str` | Nicht-leer, Pflichtfeld |
| `typ` | `ActorType` | Pflichtfeld |
| `description` | `str \| None` | Optionale Beschreibung |

### Factory Methods

```python
Actor.create(name: str, typ: ActorType, description: str | None) -> Actor
    # Pflicht: name nicht leer (ActorValidationError)

Actor.from_record(record: dict) -> Actor
    # Felder: id, name, typ, description
    # Fehler: ActorValidationError für unbekannten typ-Wert
```

### Mutation

```python
actor.update(name: str, typ: ActorType, description: str | None) -> None
    # Pflicht: name nicht leer (ActorValidationError)
```

### Datenbank

Tabelle: `narrative_actors`

| Spalte | Typ | Anmerkung |
|---|---|---|
| `id` | UUID PK | |
| `narrative_id` | UUID NOT NULL | FK → `narrative.id` ON DELETE CASCADE |
| `name` | TEXT NOT NULL | |
| `typ` | TEXT NOT NULL | CHECK: `'individual','organisation','group','institution','abstract_entity'` |
| `description` | TEXT | nullable |
| `created_at` | TIMESTAMPTZ | |

**Hinweis:** Akteure hängen am Narrativ, nicht an einzelnen Szenen.
Die Zielarchitektur sieht Akteure als `DocumentAsset` mit `DocumentLink`-
Referenzen auf Textstellen vor. Wir haben noch keine Szene-Akteur-Verknüpfung.

---

## API-Endpunkte

```
GET    /narratives                            Liste aller Narrative (id + title)
POST   /narratives                            Narrativ anlegen {title}
GET    /narratives/{id}                       Narrativ mit Szenen und Akteuren
POST   /narratives/{id}/scenes               Szene hinzufügen {title, text}
POST   /narratives/{id}/actors               Akteur anlegen {name, typ, description?}
PUT    /narratives/{id}/actors/{actor_id}    Akteur aktualisieren {name, typ, description?}
DELETE /narratives/{id}/actors/{actor_id}    Akteur löschen
PUT    /narratives/{id}/causal-model         Wirkmodell verknüpfen {causal_model_id}
POST   /narratives/import                    Datei importieren {path}
```

---

## Was fehlt (bewusste Vereinfachungen)

- Keine Hierarchie in `narrative_units` (kein Kapitel, kein Teil)
- Keine Szene-Akteur-Verknüpfung (wer tritt in welcher Szene auf?)
- Keine Szenenbearbeitung nach dem Anlegen (kein PATCH/PUT für Szenen)
- Akteure sind nicht mit Wirkgefüge-Entitäten verknüpft
