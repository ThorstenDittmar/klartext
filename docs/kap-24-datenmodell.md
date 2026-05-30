# 24. Technisches Datenmodell

Dieses Kapitel übersetzt das konzeptionelle Objekt- und Lebenszyklusmodell aus [Kap. 7.4](kap-07-wirkmodelle.md) in ein implementierbares Datenbankschema.

→ Querverweis: [Objekt- und Lebenszyklusmodell – Kap. 7.4](kap-07-wirkmodelle.md)

## 24.1 Designentscheidungen und Grundprinzipien

### Relational statt Graph

Das Wirkmodell ist konzeptionell ein Graph – Knoten sind Modellelemente, Kanten sind Relationen. Trotzdem empfiehlt sich **PostgreSQL als primäre Datenbank**, nicht eine dedizierte Graphdatenbank.

> **Begründung:** Der Großteil der Daten (Nutzer, Narrative, Community, Trust Network) ist relational. PostgreSQL unterstützt rekursive CTEs für Graphabfragen und JSONB für flexible Attribute.

### Polymorphe Modellelemente

Kap. 7.4.3 beschreibt acht Kategorien von Objektklassen (A–H) mit insgesamt über vierzig Typen. Diese werden in einer **einzigen Tabelle `modellelemente`** mit einem Typ-Diskriminator und einem JSONB-Feld für typspezifische Attribute abgebildet.

### Snapshot-basierte Versionierung

Wirkmodelle und Narrative werden **snapshot-basiert versioniert**: Jede neue Version ist ein vollständiger Snapshot, keine Diff-Liste.

### Privacy by Design

- `acceptance`: RLS sperrt Abfragen „wer hat mich akzeptiert" auf Datenbankebene
- `user_private_data`: separate Tabelle mit eingeschränktem Zugriff

---

## 24.2 Nutzer und Identität

### Tabelle: `users`

```sql
CREATE TABLE users (
    id                          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username                    TEXT NOT NULL UNIQUE,
    bio                         TEXT CHECK (length(bio) <= 280),
    system_role                 TEXT DEFAULT NULL,
    -- Enum: admin, gutachter, moderator, NULL
    rechtsraum                  TEXT[] DEFAULT '{}',
    allow_recycling_default     BOOLEAN DEFAULT TRUE,
    acceptance_pattern_public   BOOLEAN DEFAULT FALSE,
    show_violations             BOOLEAN DEFAULT FALSE,
    lesehistorie_public         BOOLEAN DEFAULT FALSE,
    muster_public               BOOLEAN DEFAULT FALSE,
    created_at                  TIMESTAMPTZ DEFAULT now(),
    last_active_at              TIMESTAMPTZ
);
```

### Tabelle: `user_private_data`

Nur für Admins und das System zugänglich.

```sql
CREATE TABLE user_private_data (
    user_id                 UUID PRIMARY KEY REFERENCES users(id),
    real_name               TEXT,
    contact_email           TEXT,
    contact_info            JSONB DEFAULT '{}',
    identity_verified_at    TIMESTAMPTZ DEFAULT NULL
);
```

---

## 24.3 Wirkmodell

### Tabelle: `wirkmodelle`

```sql
CREATE TABLE wirkmodelle (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    current_version_id  UUID,  -- FK zu wirkmodell_versions (nach Erstellung gesetzt)
    created_by          UUID REFERENCES users(id),
    status              TEXT NOT NULL DEFAULT 'privat',
    -- Enum: privat, geteilt, reviewfaehig, intern, katalog, archiviert, ersetzt, zurueckgezogen
    nachfolger_id       UUID REFERENCES wirkmodelle(id) DEFAULT NULL,
    rechtsraum          TEXT[] DEFAULT '{}',
    registered_only     BOOLEAN DEFAULT FALSE,
    cover_url           TEXT DEFAULT NULL,
    klappentext         TEXT CHECK (length(klappentext) <= 1000),
    tags                TEXT[] DEFAULT '{}',
    recycling_allowed   BOOLEAN DEFAULT TRUE,
    created_at          TIMESTAMPTZ DEFAULT now()
);
```

### Tabelle: `wirkmodell_versions`

```sql
CREATE TABLE wirkmodell_versions (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    wirkmodell_id   UUID REFERENCES wirkmodelle(id),
    version_number  INTEGER NOT NULL,
    snapshot        JSONB NOT NULL,
    -- Vollständiger Snapshot aller Modellelemente und Relationen dieser Version
    created_by      UUID REFERENCES users(id),
    created_at      TIMESTAMPTZ DEFAULT now(),
    change_summary  TEXT DEFAULT NULL,
    UNIQUE (wirkmodell_id, version_number)
);
```

### Tabelle: `modellelemente`

Polymorphe Tabelle für alle Objektklassen aus Kap. 7.4.3 (A bis H).

```sql
CREATE TABLE modellelemente (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    wirkmodell_id           UUID REFERENCES wirkmodelle(id),
    wirkmodell_version_id   UUID REFERENCES wirkmodell_versions(id),
    typ                     TEXT NOT NULL,
    -- Enum: wirkraum, geltungsbereich, zeitscheibe, szenario, entitaet, zustand,
    -- prozess, variable, schnittstelle, claim, gegenclaim, annahme, axiom,
    -- schlussregel, evidenzobjekt, kompetenzfrage, relation, kausalrelation,
    -- konfliktrelation, abhaengigkeitsrelation, vertrag, precondition,
    -- postcondition, invariante, statusangabe, luecke, mehrdeutigkeit, pruefpflicht
    label                   TEXT NOT NULL,
    beschreibung            TEXT DEFAULT NULL,
    ist_axiomatisch         BOOLEAN DEFAULT FALSE,
    lebenszyklus_status     TEXT DEFAULT 'entwurf',
    -- Enum: entwurf, spezifiziert, verknuepft, pruefpflichtig, geprueft,
    -- stabilisiert, ueberarbeitet, verworfen, archiviert
    attribute               JSONB DEFAULT '{}',
    geltungsbereich_id      UUID REFERENCES modellelemente(id) DEFAULT NULL,
    created_by              UUID REFERENCES users(id),
    created_at              TIMESTAMPTZ DEFAULT now()
);
```

---

## 24.4 Narrativ

### Tabelle: `narrative`

```sql
CREATE TABLE narrative (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    current_version_id      UUID,  -- FK zu narrativ_versions
    created_by              UUID REFERENCES users(id),
    wirkmodell_id           UUID REFERENCES wirkmodelle(id) DEFAULT NULL,
    wirkmodell_version_id   UUID REFERENCES wirkmodell_versions(id) DEFAULT NULL,
    status                  TEXT NOT NULL DEFAULT 'privat',
    -- Enum: privat, geteilt, intern, oeffentlich
    titel                   TEXT NOT NULL,
    klappentext             TEXT CHECK (length(klappentext) <= 1000),
    cover_url               TEXT DEFAULT NULL,
    tags                    TEXT[] DEFAULT '{}',
    rechtsraum              TEXT[] DEFAULT '{}',
    registered_only         BOOLEAN DEFAULT FALSE,
    recycling_allowed       BOOLEAN DEFAULT TRUE,
    recycling_forced        BOOLEAN DEFAULT FALSE,
    created_at              TIMESTAMPTZ DEFAULT now()
);
```

### Tabellen: `document_nodes`, `document_assets`, `document_links`

Drei Tabellen bilden das Dokumentmodell ab: `document_nodes` für den Composite-Baum, `document_assets` für Ressourcen außerhalb des Baums, `document_links` für den Graphlayer. Vgl. Kap. 6.2.1.

```sql
-- DocumentNode: Composite-Baum. Jeder Knoten hat genau einen Parent,
-- außer dem Root-Knoten (parent_id IS NULL).

CREATE TABLE document_nodes (
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    narrativ_id       UUID REFERENCES narrative(id),
    version_id        UUID,
    parent_id         UUID REFERENCES document_nodes(id) DEFAULT NULL,
    node_type         TEXT NOT NULL,
    -- Enum: work, part, chapter, section, paragraph, sentence, string, character
    structural_role   TEXT DEFAULT NULL,
    -- Enum: main_text, title, subtitle, preface, motto, dedication,
    --       appendix, footnote, bibliography, glossary
    presentation_role TEXT DEFAULT NULL,
    -- Enum: heading, emphasis, block_quote, caption, normal
    audience          TEXT NOT NULL DEFAULT 'public',
    -- Enum: public, author_only, co_authors, editorial
    inhalt            TEXT DEFAULT NULL,
    position          INTEGER NOT NULL,
    created_at        TIMESTAMPTZ DEFAULT now()
);

-- DocumentAsset: Ressourcen außerhalb des Baums.
-- Kann von beliebig vielen document_nodes referenziert werden.

CREATE TABLE document_assets (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    narrativ_id UUID REFERENCES narrative(id),
    asset_type  TEXT NOT NULL,
    -- Enum: map, image, file, note, todo, comment, research_ref
    inhalt      TEXT DEFAULT NULL,
    url         TEXT DEFAULT NULL,
    audience    TEXT NOT NULL DEFAULT 'author_only',
    -- Enum: public, author_only, co_authors, editorial
    created_by  UUID REFERENCES users(id),
    created_at  TIMESTAMPTZ DEFAULT now()
);

-- DocumentLink: Graphlayer. Verbindet Knoten mit Knoten oder Assets.
-- Von beiden Seiten abfragbar (source → target und target → source).

CREATE TABLE document_links (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_id   UUID NOT NULL,
    source_type TEXT NOT NULL,
    -- Enum: document_node, document_asset
    target_id   UUID NOT NULL,
    target_type TEXT NOT NULL,
    -- Enum: document_node, document_asset
    link_type   TEXT NOT NULL,
    -- Enum: refers_to, annotation, cross_ref, asset_ref
    created_by  UUID REFERENCES users(id),
    created_at  TIMESTAMPTZ DEFAULT now()
);
```

---

## 24.5 Trust Network

### Tabelle: `acceptance`

!!! warning "Privacy by Design"
    Row-Level Security: `user_id` darf nur eigene Zeilen lesen.
    `to_user_id` hat **keinen** Lesezugriff auf Zeilen die ihn betreffen.

```sql
CREATE TABLE acceptance (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    from_user_id    UUID REFERENCES users(id),
    to_user_id      UUID REFERENCES users(id),
    created_at      TIMESTAMPTZ DEFAULT now(),
    UNIQUE (from_user_id, to_user_id),
    CHECK (from_user_id != to_user_id)
);
```

---

## 24.10 Indizes und Performance

```sql
-- Wirkmodell-Status-Filter (Katalog, öffentlich)
CREATE INDEX idx_wirkmodelle_status ON wirkmodelle(status);

-- Modellelemente nach Typ und Wirkmodell
CREATE INDEX idx_modellelemente_typ ON modellelemente(wirkmodell_id, typ);

-- Dokument-Baumstruktur
CREATE INDEX idx_document_nodes_parent ON document_nodes(parent_id);
CREATE INDEX idx_document_links_source ON document_links(source_id, source_type);
CREATE INDEX idx_document_links_target ON document_links(target_id, target_type);

-- Acceptance (nur from_user abfragbar)
CREATE INDEX idx_acceptance_from ON acceptance(from_user_id);
-- KEIN Index auf to_user_id (Privacy by Design)
```
