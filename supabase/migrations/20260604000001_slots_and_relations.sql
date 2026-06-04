-- Migration 20260604000001 — Slots and CausalRelations tables
--
-- Slots are the named placeholders in a Wirkgefüge (e.g. "Geldmenge", "Inflation").
-- CausalRelations are directed causal links between two Slots.
-- Both belong to exactly one CausalModel via causal_model_id.

ALTER TABLE causal_models ADD COLUMN IF NOT EXISTS identifier TEXT DEFAULT NULL;

CREATE TABLE slots (
    id               UUID    PRIMARY KEY DEFAULT gen_random_uuid(),
    causal_model_id  UUID    NOT NULL REFERENCES causal_models(id) ON DELETE CASCADE,
    identifier       TEXT    NOT NULL,
    slot_type        TEXT    NOT NULL
                             CHECK (slot_type IN (
                                 'physical_quantity', 'social_quantity',
                                 'entity_state', 'trend', 'process'
                             )),
    epistemic_status TEXT    NOT NULL DEFAULT 'incomplete'
                             CHECK (epistemic_status IN ('incomplete', 'axiomatic')),
    is_entity        BOOLEAN NOT NULL DEFAULT FALSE,
    created_at       TIMESTAMPTZ DEFAULT now(),
    UNIQUE (causal_model_id, identifier)
);

CREATE TABLE causal_relations (
    id               UUID    PRIMARY KEY DEFAULT gen_random_uuid(),
    causal_model_id  UUID    NOT NULL REFERENCES causal_models(id) ON DELETE CASCADE,
    identifier       TEXT    NOT NULL,
    source_slot_id   UUID    NOT NULL REFERENCES slots(id),
    target_slot_id   UUID    NOT NULL REFERENCES slots(id),
    mechanism        TEXT    DEFAULT NULL,
    polarity         TEXT    DEFAULT NULL
                             CHECK (polarity IN ('positive', 'negative', 'ambivalent')),
    epistemic_status TEXT    NOT NULL DEFAULT 'incomplete'
                             CHECK (epistemic_status IN ('incomplete', 'axiomatic')),
    created_at       TIMESTAMPTZ DEFAULT now(),
    UNIQUE (causal_model_id, identifier)
);

CREATE INDEX slots_causal_model_id_idx ON slots (causal_model_id);
CREATE INDEX causal_relations_causal_model_id_idx ON causal_relations (causal_model_id);
