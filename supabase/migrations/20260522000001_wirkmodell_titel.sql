-- Add titel to wirkmodelle.
-- The initial schema omitted this field; it is required to identify a Wirkmodell
-- without loading its version history or child elements.

ALTER TABLE wirkmodelle ADD COLUMN titel TEXT NOT NULL DEFAULT '';

-- Remove the default after backfill so future inserts must supply a title.
ALTER TABLE wirkmodelle ALTER COLUMN titel DROP DEFAULT;
