-- Rename all German table names, column names and CHECK-constraint values to English.
--
-- The initial schema was a direct translation of the German concept document.
-- All code must be in English (CLAUDE.md); this migration brings the database
-- schema in line with that rule.
--
-- Tables renamed:
--   narrative_einheiten  → narrative_units
--   narrative_akteure    → narrative_actors
--   wirkmodelle          → causal_models
--   wirkmodell_versions  → causal_model_versions
--   narrativ_versions    → narrative_versions
--   modellelemente       → model_elements
--
-- Columns renamed (selection of what Python code touches):
--   narrative.titel               → title
--   narrative.wirkmodell_id       → causal_model_id
--   narrative_units.narrativ_id   → narrative_id
--   narrative_units.titel         → title
--   narrative_units.inhalt        → content
--   narrative_actors.narrativ_id  → narrative_id
--   narrative_actors.beschreibung → description
--   causal_models.nachfolger_id   → successor_id
--   causal_models.rechtsraum      → legal_context
--   causal_models.klappentext     → blurb
--   causal_model_versions.wirkmodell_id → causal_model_id
--   narrative_versions.narrativ_id      → narrative_id
--   model_elements.*  (see below)
--   users.*           (see below)

-- ============================================================
-- RENAME TABLES
-- ============================================================

ALTER TABLE narrative_einheiten  RENAME TO narrative_units;
ALTER TABLE narrative_akteure    RENAME TO narrative_actors;
ALTER TABLE wirkmodelle          RENAME TO causal_models;
ALTER TABLE wirkmodell_versions  RENAME TO causal_model_versions;
ALTER TABLE narrativ_versions    RENAME TO narrative_versions;
ALTER TABLE modellelemente       RENAME TO model_elements;

-- ============================================================
-- RENAME COLUMNS — narrative
-- ============================================================

ALTER TABLE narrative RENAME COLUMN titel        TO title;
ALTER TABLE narrative RENAME COLUMN wirkmodell_id TO causal_model_id;

-- ============================================================
-- RENAME COLUMNS — narrative_units
-- ============================================================

ALTER TABLE narrative_units RENAME COLUMN narrativ_id TO narrative_id;
ALTER TABLE narrative_units RENAME COLUMN titel       TO title;
ALTER TABLE narrative_units RENAME COLUMN inhalt      TO content;

-- ============================================================
-- RENAME COLUMNS — narrative_actors
-- ============================================================

ALTER TABLE narrative_actors RENAME COLUMN narrativ_id  TO narrative_id;
ALTER TABLE narrative_actors RENAME COLUMN beschreibung TO description;

-- ============================================================
-- RENAME COLUMNS — causal_models (was wirkmodelle)
-- ============================================================

ALTER TABLE causal_models RENAME COLUMN nachfolger_id TO successor_id;
ALTER TABLE causal_models RENAME COLUMN rechtsraum    TO legal_context;
ALTER TABLE causal_models RENAME COLUMN klappentext   TO blurb;

-- ============================================================
-- RENAME COLUMNS — causal_model_versions
-- ============================================================

ALTER TABLE causal_model_versions RENAME COLUMN wirkmodell_id TO causal_model_id;

-- ============================================================
-- RENAME COLUMNS — narrative_versions
-- ============================================================

ALTER TABLE narrative_versions RENAME COLUMN narrativ_id TO narrative_id;

-- ============================================================
-- RENAME COLUMNS — model_elements (was modellelemente)
-- ============================================================

ALTER TABLE model_elements RENAME COLUMN wirkmodell_id         TO causal_model_id;
ALTER TABLE model_elements RENAME COLUMN wirkmodell_version_id TO causal_model_version_id;
ALTER TABLE model_elements RENAME COLUMN beschreibung          TO description;
ALTER TABLE model_elements RENAME COLUMN ist_axiomatisch       TO is_axiomatic;
ALTER TABLE model_elements RENAME COLUMN lebenszyklus_status   TO lifecycle_status;
ALTER TABLE model_elements RENAME COLUMN geltungsbereich_id    TO scope_id;

-- ============================================================
-- RENAME COLUMNS — users
-- ============================================================

ALTER TABLE users RENAME COLUMN rechtsraum          TO legal_context;
ALTER TABLE users RENAME COLUMN lesehistorie_public TO reading_history_public;
ALTER TABLE users RENAME COLUMN muster_public       TO patterns_public;

-- ============================================================
-- UPDATE CHECK VALUES AND CONSTRAINTS — narrative_units.typ
-- Constraint was auto-named narrative_einheiten_typ_check.
-- ============================================================

UPDATE narrative_units SET typ = 'work'    WHERE typ = 'werk';
UPDATE narrative_units SET typ = 'part'    WHERE typ = 'teil';
UPDATE narrative_units SET typ = 'chapter' WHERE typ = 'kapitel';
UPDATE narrative_units SET typ = 'scene'   WHERE typ = 'szene';
-- 'fragment' is unchanged

ALTER TABLE narrative_units DROP CONSTRAINT narrative_einheiten_typ_check;
ALTER TABLE narrative_units ADD  CONSTRAINT narrative_units_typ_check
    CHECK (typ IN ('work', 'part', 'chapter', 'scene', 'fragment'));

-- ============================================================
-- UPDATE CHECK VALUES AND CONSTRAINTS — narrative_actors.typ
-- ============================================================

UPDATE narrative_actors SET typ = 'individual'    WHERE typ = 'figur';
UPDATE narrative_actors SET typ = 'group'         WHERE typ = 'gruppe';
UPDATE narrative_actors SET typ = 'abstract_entity' WHERE typ = 'abstrakte_entitaet';
-- 'organisation' and 'institution' are unchanged

ALTER TABLE narrative_actors DROP CONSTRAINT narrative_akteure_typ_check;
ALTER TABLE narrative_actors ADD  CONSTRAINT narrative_actors_typ_check
    CHECK (typ IN ('individual', 'organisation', 'group', 'institution', 'abstract_entity'));

-- ============================================================
-- UPDATE CHECK VALUES AND CONSTRAINTS — narrative.status
-- ============================================================

UPDATE narrative SET status = 'private'  WHERE status = 'privat';
UPDATE narrative SET status = 'shared'   WHERE status = 'geteilt';
UPDATE narrative SET status = 'internal' WHERE status = 'intern';
UPDATE narrative SET status = 'public'   WHERE status = 'oeffentlich';

ALTER TABLE narrative DROP CONSTRAINT narrative_status_check;
ALTER TABLE narrative ADD  CONSTRAINT narrative_status_check
    CHECK (status IN ('private', 'shared', 'internal', 'public'));
ALTER TABLE narrative ALTER COLUMN status SET DEFAULT 'private';

-- ============================================================
-- UPDATE CHECK VALUES AND CONSTRAINTS — causal_models.status
-- ============================================================

UPDATE causal_models SET status = 'private'    WHERE status = 'privat';
UPDATE causal_models SET status = 'shared'     WHERE status = 'geteilt';
UPDATE causal_models SET status = 'reviewable' WHERE status = 'reviewfaehig';
UPDATE causal_models SET status = 'internal'   WHERE status = 'intern';
UPDATE causal_models SET status = 'catalogue'  WHERE status = 'katalog';
UPDATE causal_models SET status = 'archived'   WHERE status = 'archiviert';
UPDATE causal_models SET status = 'superseded' WHERE status = 'ersetzt';
UPDATE causal_models SET status = 'withdrawn'  WHERE status = 'zurueckgezogen';

ALTER TABLE causal_models DROP CONSTRAINT wirkmodelle_status_check;
ALTER TABLE causal_models ADD  CONSTRAINT causal_models_status_check
    CHECK (status IN (
        'private', 'shared', 'reviewable', 'internal',
        'catalogue', 'archived', 'superseded', 'withdrawn'
    ));
ALTER TABLE causal_models ALTER COLUMN status SET DEFAULT 'private';

-- ============================================================
-- UPDATE CHECK VALUES AND CONSTRAINTS — model_elements.lifecycle_status
-- ============================================================

UPDATE model_elements SET lifecycle_status = 'draft'          WHERE lifecycle_status = 'entwurf';
UPDATE model_elements SET lifecycle_status = 'specified'      WHERE lifecycle_status = 'spezifiziert';
UPDATE model_elements SET lifecycle_status = 'linked'         WHERE lifecycle_status = 'verknuepft';
UPDATE model_elements SET lifecycle_status = 'pending_review' WHERE lifecycle_status = 'pruefpflichtig';
UPDATE model_elements SET lifecycle_status = 'reviewed'       WHERE lifecycle_status = 'geprueft';
UPDATE model_elements SET lifecycle_status = 'stable'         WHERE lifecycle_status = 'stabilisiert';
UPDATE model_elements SET lifecycle_status = 'revised'        WHERE lifecycle_status = 'ueberarbeitet';
UPDATE model_elements SET lifecycle_status = 'discarded'      WHERE lifecycle_status = 'verworfen';
UPDATE model_elements SET lifecycle_status = 'archived'       WHERE lifecycle_status = 'archiviert';

ALTER TABLE model_elements DROP CONSTRAINT modellelemente_lebenszyklus_status_check;
ALTER TABLE model_elements ADD  CONSTRAINT model_elements_lifecycle_status_check
    CHECK (lifecycle_status IN (
        'draft', 'specified', 'linked', 'pending_review', 'reviewed',
        'stable', 'revised', 'discarded', 'archived'
    ));
ALTER TABLE model_elements ALTER COLUMN lifecycle_status SET DEFAULT 'draft';

-- ============================================================
-- UPDATE CHECK VALUES AND CONSTRAINTS — model_elements.typ
-- ============================================================

UPDATE model_elements SET typ = 'causal_space'           WHERE typ = 'wirkraum';
UPDATE model_elements SET typ = 'scope'                  WHERE typ = 'geltungsbereich';
UPDATE model_elements SET typ = 'time_slice'             WHERE typ = 'zeitscheibe';
UPDATE model_elements SET typ = 'scenario'               WHERE typ = 'szenario';
UPDATE model_elements SET typ = 'scenario_path'          WHERE typ = 'szenariopfad';
UPDATE model_elements SET typ = 'model_variant'          WHERE typ = 'modellvariante';
UPDATE model_elements SET typ = 'entity'                 WHERE typ = 'entitaet';
UPDATE model_elements SET typ = 'state'                  WHERE typ = 'zustand';
UPDATE model_elements SET typ = 'process'                WHERE typ = 'prozess';
UPDATE model_elements SET typ = 'interface'              WHERE typ = 'schnittstelle';
UPDATE model_elements SET typ = 'counter_claim'          WHERE typ = 'gegenclaim';
UPDATE model_elements SET typ = 'assumption'             WHERE typ = 'annahme';
UPDATE model_elements SET typ = 'inference_rule'         WHERE typ = 'schlussregel';
UPDATE model_elements SET typ = 'priority_rule'          WHERE typ = 'prioritaetsregel';
UPDATE model_elements SET typ = 'evidence_object'        WHERE typ = 'evidenzobjekt';
UPDATE model_elements SET typ = 'evidence_standard'      WHERE typ = 'evidenzstandard';
UPDATE model_elements SET typ = 'competency_question'    WHERE typ = 'kompetenzfrage';
UPDATE model_elements SET typ = 'causal_relation'        WHERE typ = 'kausalrelation';
UPDATE model_elements SET typ = 'conflict_relation'      WHERE typ = 'konfliktrelation';
UPDATE model_elements SET typ = 'dependency_relation'    WHERE typ = 'abhaengigkeitsrelation';
UPDATE model_elements SET typ = 'evidence_relation'      WHERE typ = 'evidenzrelation';
UPDATE model_elements SET typ = 'reference_relation'     WHERE typ = 'referenzrelation';
UPDATE model_elements SET typ = 'variant_relation'       WHERE typ = 'variantenrelation';
UPDATE model_elements SET typ = 'transformation_relation' WHERE typ = 'transformationsrelation';
UPDATE model_elements SET typ = 'contract'               WHERE typ = 'vertrag';
UPDATE model_elements SET typ = 'invariant'              WHERE typ = 'invariante';
UPDATE model_elements SET typ = 'activation_condition'   WHERE typ = 'aktivierungsbedingung';
UPDATE model_elements SET typ = 'transition_condition'   WHERE typ = 'uebergangsbedingung';
UPDATE model_elements SET typ = 'status_annotation'      WHERE typ = 'statusangabe';
UPDATE model_elements SET typ = 'uncertainty_annotation' WHERE typ = 'unsicherheitsangabe';
UPDATE model_elements SET typ = 'gap'                    WHERE typ = 'luecke';
UPDATE model_elements SET typ = 'open_question'          WHERE typ = 'offene_frage';
UPDATE model_elements SET typ = 'ambiguity'              WHERE typ = 'mehrdeutigkeit';
UPDATE model_elements SET typ = 'review_obligation'      WHERE typ = 'pruefpflicht';
-- 'variable', 'claim', 'axiom', 'relation', 'precondition', 'postcondition' unchanged

ALTER TABLE model_elements DROP CONSTRAINT modellelemente_typ_check;
ALTER TABLE model_elements ADD  CONSTRAINT model_elements_typ_check
    CHECK (typ IN (
        'causal_space', 'scope', 'time_slice', 'scenario', 'scenario_path', 'model_variant',
        'entity', 'state', 'process', 'variable', 'interface',
        'claim', 'counter_claim', 'assumption', 'axiom', 'inference_rule', 'priority_rule',
        'evidence_object', 'evidence_standard', 'competency_question',
        'relation', 'causal_relation', 'conflict_relation', 'dependency_relation',
        'evidence_relation', 'reference_relation', 'variant_relation', 'transformation_relation',
        'contract', 'precondition', 'postcondition', 'invariant',
        'activation_condition', 'transition_condition',
        'status_annotation', 'uncertainty_annotation',
        'gap', 'open_question', 'ambiguity', 'review_obligation'
    ));

-- ============================================================
-- UPDATE CHECK VALUES AND CONSTRAINTS — users.system_role
-- ============================================================

UPDATE users SET system_role = 'reviewer' WHERE system_role = 'gutachter';

ALTER TABLE users DROP CONSTRAINT users_system_role_check;
ALTER TABLE users ADD  CONSTRAINT users_system_role_check
    CHECK (system_role IN ('admin', 'reviewer', 'moderator'));

-- ============================================================
-- REBUILD INDEXES WITH ENGLISH NAMES
-- ============================================================

DROP INDEX IF EXISTS idx_wirkmodelle_status;
DROP INDEX IF EXISTS idx_wirkmodelle_created_by;
DROP INDEX IF EXISTS idx_modellelemente_typ;
DROP INDEX IF EXISTS idx_modellelemente_axiom;
DROP INDEX IF EXISTS idx_einheiten_parent;
DROP INDEX IF EXISTS idx_einheiten_narrativ;
DROP INDEX IF EXISTS idx_akteure_narrativ;

CREATE INDEX idx_causal_models_status     ON causal_models(status);
CREATE INDEX idx_causal_models_created_by ON causal_models(created_by);
CREATE INDEX idx_model_elements_typ       ON model_elements(causal_model_id, typ);
CREATE INDEX idx_model_elements_axiomatic ON model_elements(causal_model_id, is_axiomatic)
                                           WHERE is_axiomatic = TRUE;
CREATE INDEX idx_narrative_units_parent   ON narrative_units(parent_id);
CREATE INDEX idx_narrative_units_narrative ON narrative_units(narrative_id, position);
CREATE INDEX idx_narrative_actors_narrative ON narrative_actors(narrative_id);
