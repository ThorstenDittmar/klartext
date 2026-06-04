-- Actor + Claim Evolution (Plan B)
--
-- Renames narrative_actors columns to match the domain model:
--   name        → label
--   typ         → actor_type  (column + constraint rename)
--   description → notes
--   +entity_ref  (new nullable column)
--
-- Adds columns to claims:
--   +label          (short human-readable name for the claim)
--   +status         (draft | linked | unresolved)
--   +wirkgefuege_ref (nullable reference to a causal model element)

-- ============================================================
-- narrative_actors: rename name → label
-- ============================================================

ALTER TABLE narrative_actors RENAME COLUMN name TO label;

-- ============================================================
-- narrative_actors: rename description → notes
-- ============================================================

ALTER TABLE narrative_actors RENAME COLUMN description TO notes;

-- ============================================================
-- narrative_actors: rename typ → actor_type
-- ============================================================

-- Drop the existing CHECK constraint (named in the previous migration)
ALTER TABLE narrative_actors DROP CONSTRAINT narrative_actors_typ_check;
-- Rename the column
ALTER TABLE narrative_actors RENAME COLUMN typ TO actor_type;
-- Re-add the constraint with the new column name
ALTER TABLE narrative_actors ADD CONSTRAINT narrative_actors_actor_type_check
    CHECK (actor_type IN ('individual', 'organisation', 'group', 'institution', 'abstract_entity'));

-- ============================================================
-- narrative_actors: add entity_ref
-- ============================================================

ALTER TABLE narrative_actors ADD COLUMN entity_ref TEXT DEFAULT NULL;

-- ============================================================
-- claims: add label, status, wirkgefuege_ref
-- ============================================================

ALTER TABLE claims ADD COLUMN label TEXT NOT NULL DEFAULT '';
ALTER TABLE claims ADD COLUMN status TEXT NOT NULL DEFAULT 'draft'
    CHECK (status IN ('draft', 'linked', 'unresolved'));
ALTER TABLE claims ADD COLUMN wirkgefuege_ref TEXT DEFAULT NULL;

-- Backfill label from text for existing rows (first 80 chars)
UPDATE claims SET label = left(text, 80) WHERE label = '';

-- Remove the default so future inserts must provide a label explicitly
ALTER TABLE claims ALTER COLUMN label DROP DEFAULT;
