-- klartext.jetzt – Spike: Claims table
-- Stores extracted Claims tied to a narrative scene (narrative_einheiten).
-- Used by the ClaimRepository during the TDD spike; can be migrated into
-- modellelemente once the full data model is ready.

CREATE TABLE claims (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    scene_id    UUID NOT NULL REFERENCES narrative_einheiten(id) ON DELETE CASCADE,
    text        TEXT NOT NULL,
    typ         TEXT NOT NULL,
    confidence  DOUBLE PRECISION NOT NULL
                    CHECK (confidence >= 0.0 AND confidence <= 1.0),
    created_at  TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_claims_scene_id ON claims(scene_id);
