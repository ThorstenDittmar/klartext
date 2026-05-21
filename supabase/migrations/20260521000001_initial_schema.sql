-- klartext.jetzt – Initial Schema
-- Kap. 24: Technisches Datenmodell (Whitepaper V0.24)
-- First migration: core tables + RLS for acceptance

-- ============================================================
-- EXTENSIONS
-- ============================================================
CREATE EXTENSION IF NOT EXISTS "pgcrypto";


-- ============================================================
-- 24.2 NUTZER UND IDENTITÄT
-- ============================================================

CREATE TABLE users (
    id                          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username                    TEXT NOT NULL UNIQUE,
    bio                         TEXT CHECK (length(bio) <= 280),
    system_role                 TEXT DEFAULT NULL
                                    CHECK (system_role IN ('admin', 'gutachter', 'moderator')),
    rechtsraum                  TEXT[] DEFAULT '{}',
    allow_recycling_default     BOOLEAN DEFAULT TRUE,
    acceptance_pattern_public   BOOLEAN DEFAULT FALSE,
    show_violations             BOOLEAN DEFAULT FALSE,
    lesehistorie_public         BOOLEAN DEFAULT FALSE,
    muster_public               BOOLEAN DEFAULT FALSE,
    created_at                  TIMESTAMPTZ DEFAULT now(),
    last_active_at              TIMESTAMPTZ
);

-- Nur für Admins und System zugänglich (Privacy by Design)
CREATE TABLE user_private_data (
    user_id                 UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    real_name               TEXT,
    contact_email           TEXT,
    contact_info            JSONB DEFAULT '{}',
    identity_verified_at    TIMESTAMPTZ DEFAULT NULL
);


-- ============================================================
-- 24.3 WIRKMODELL
-- ============================================================

CREATE TABLE wirkmodelle (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    -- current_version_id wird nach Anlage der ersten Version gesetzt
    current_version_id  UUID DEFAULT NULL,
    created_by          UUID REFERENCES users(id),
    status              TEXT NOT NULL DEFAULT 'privat'
                            CHECK (status IN (
                                'privat', 'geteilt', 'reviewfaehig', 'intern',
                                'katalog', 'archiviert', 'ersetzt', 'zurueckgezogen'
                            )),
    nachfolger_id       UUID REFERENCES wirkmodelle(id) DEFAULT NULL,
    rechtsraum          TEXT[] DEFAULT '{}',
    registered_only     BOOLEAN DEFAULT FALSE,
    cover_url           TEXT DEFAULT NULL,
    klappentext         TEXT CHECK (length(klappentext) <= 1000),
    tags                TEXT[] DEFAULT '{}',
    recycling_allowed   BOOLEAN DEFAULT TRUE,
    created_at          TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE wirkmodell_versions (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    wirkmodell_id   UUID NOT NULL REFERENCES wirkmodelle(id) ON DELETE CASCADE,
    version_number  INTEGER NOT NULL,
    snapshot        JSONB NOT NULL DEFAULT '{}',
    created_by      UUID REFERENCES users(id),
    created_at      TIMESTAMPTZ DEFAULT now(),
    change_summary  TEXT DEFAULT NULL,
    UNIQUE (wirkmodell_id, version_number)
);

-- Polymorphe Tabelle für alle Objektklassen A–H (Kap. 7.4.3)
CREATE TABLE modellelemente (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    wirkmodell_id           UUID NOT NULL REFERENCES wirkmodelle(id) ON DELETE CASCADE,
    wirkmodell_version_id   UUID REFERENCES wirkmodell_versions(id),
    typ                     TEXT NOT NULL
                                CHECK (typ IN (
                                    'wirkraum', 'geltungsbereich', 'zeitscheibe',
                                    'szenario', 'szenariopfad', 'modellvariante',
                                    'entitaet', 'zustand', 'prozess', 'variable',
                                    'schnittstelle', 'claim', 'gegenclaim', 'annahme',
                                    'axiom', 'schlussregel', 'prioritaetsregel',
                                    'evidenzobjekt', 'evidenzstandard', 'kompetenzfrage',
                                    'relation', 'kausalrelation', 'konfliktrelation',
                                    'abhaengigkeitsrelation', 'evidenzrelation',
                                    'referenzrelation', 'variantenrelation',
                                    'transformationsrelation', 'vertrag',
                                    'precondition', 'postcondition', 'invariante',
                                    'aktivierungsbedingung', 'uebergangsbedingung',
                                    'statusangabe', 'unsicherheitsangabe',
                                    'luecke', 'offene_frage', 'mehrdeutigkeit',
                                    'pruefpflicht'
                                )),
    label                   TEXT NOT NULL,
    beschreibung            TEXT DEFAULT NULL,
    ist_axiomatisch         BOOLEAN DEFAULT FALSE,
    lebenszyklus_status     TEXT NOT NULL DEFAULT 'entwurf'
                                CHECK (lebenszyklus_status IN (
                                    'entwurf', 'spezifiziert', 'verknuepft',
                                    'pruefpflichtig', 'geprueft', 'stabilisiert',
                                    'ueberarbeitet', 'verworfen', 'archiviert'
                                )),
    attribute               JSONB DEFAULT '{}',
    geltungsbereich_id      UUID REFERENCES modellelemente(id) DEFAULT NULL,
    created_by              UUID REFERENCES users(id),
    created_at              TIMESTAMPTZ DEFAULT now()
);


-- ============================================================
-- 24.4 NARRATIV
-- ============================================================

CREATE TABLE narrative (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    current_version_id      UUID DEFAULT NULL,
    created_by              UUID REFERENCES users(id),
    wirkmodell_id           UUID REFERENCES wirkmodelle(id) DEFAULT NULL,
    wirkmodell_version_id   UUID REFERENCES wirkmodell_versions(id) DEFAULT NULL,
    status                  TEXT NOT NULL DEFAULT 'privat'
                                CHECK (status IN ('privat', 'geteilt', 'intern', 'oeffentlich')),
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

CREATE TABLE narrativ_versions (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    narrativ_id     UUID NOT NULL REFERENCES narrative(id) ON DELETE CASCADE,
    version_number  INTEGER NOT NULL,
    created_by      UUID REFERENCES users(id),
    created_at      TIMESTAMPTZ DEFAULT now(),
    change_summary  TEXT DEFAULT NULL,
    UNIQUE (narrativ_id, version_number)
);

-- Selbstreferentielle Baumstruktur: Werk → Teil → Kapitel → Szene → Fragment
CREATE TABLE narrative_einheiten (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    narrativ_id UUID NOT NULL REFERENCES narrative(id) ON DELETE CASCADE,
    version_id  UUID REFERENCES narrativ_versions(id),
    parent_id   UUID REFERENCES narrative_einheiten(id) DEFAULT NULL,
    typ         TEXT NOT NULL
                    CHECK (typ IN ('werk', 'teil', 'kapitel', 'szene', 'fragment')),
    titel       TEXT DEFAULT NULL,
    inhalt      TEXT DEFAULT NULL,
    position    INTEGER NOT NULL,
    created_at  TIMESTAMPTZ DEFAULT now()
);


-- ============================================================
-- 24.6 TRUST NETWORK – acceptance (Privacy by Design)
-- ============================================================

CREATE TABLE acceptance (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    from_user_id    UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    to_user_id      UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at      TIMESTAMPTZ DEFAULT now(),
    UNIQUE (from_user_id, to_user_id),
    CHECK (from_user_id != to_user_id)
);


-- ============================================================
-- INDIZES (Kap. 24.10)
-- ============================================================

CREATE INDEX idx_wirkmodelle_status       ON wirkmodelle(status);
CREATE INDEX idx_wirkmodelle_created_by   ON wirkmodelle(created_by);
CREATE INDEX idx_modellelemente_typ       ON modellelemente(wirkmodell_id, typ);
CREATE INDEX idx_modellelemente_axiom     ON modellelemente(wirkmodell_id, ist_axiomatisch)
                                           WHERE ist_axiomatisch = TRUE;
CREATE INDEX idx_narrative_status         ON narrative(status);
CREATE INDEX idx_einheiten_parent         ON narrative_einheiten(parent_id);
CREATE INDEX idx_einheiten_narrativ       ON narrative_einheiten(narrativ_id, position);
CREATE INDEX idx_acceptance_from          ON acceptance(from_user_id);
-- KEIN Index auf to_user_id (Privacy by Design: Abfragen "wer hat mich akzeptiert" verboten)


-- ============================================================
-- ROW LEVEL SECURITY
-- ============================================================

ALTER TABLE acceptance ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_private_data ENABLE ROW LEVEL SECURITY;

-- acceptance: Jeder Nutzer sieht nur eigene abgegebene Akzeptanzen
CREATE POLICY acceptance_own_rows ON acceptance
    FOR ALL
    USING (from_user_id = auth.uid());

-- acceptance: Niemand kann abfragen wer ihn akzeptiert hat
-- (keine SELECT-Policy für to_user_id)

-- user_private_data: Nur eigene Daten lesbar (Admins über Service Role)
CREATE POLICY user_private_data_own ON user_private_data
    FOR SELECT
    USING (user_id = auth.uid());

CREATE POLICY user_private_data_insert_own ON user_private_data
    FOR INSERT
    WITH CHECK (user_id = auth.uid());

CREATE POLICY user_private_data_update_own ON user_private_data
    FOR UPDATE
    USING (user_id = auth.uid());
