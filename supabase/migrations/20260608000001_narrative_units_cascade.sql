-- Add ON DELETE CASCADE to narrative_units.parent_id so deleting a parent
-- automatically removes all descendants.
--
-- The FK constraint was created by the initial schema as
-- narrative_einheiten_parent_id_fkey and may have been renamed.
-- We drop both possible names defensively.

ALTER TABLE narrative_units
    DROP CONSTRAINT IF EXISTS narrative_einheiten_parent_id_fkey;

ALTER TABLE narrative_units
    DROP CONSTRAINT IF EXISTS narrative_units_parent_id_fkey;

ALTER TABLE narrative_units
    ADD CONSTRAINT narrative_units_parent_id_fkey
        FOREIGN KEY (parent_id)
        REFERENCES narrative_units(id)
        ON DELETE CASCADE;
