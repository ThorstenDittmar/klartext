-- Add narrative_id to claims so claims can be persisted at analysis time
-- without requiring a scene reference. Backfill from existing scene→narrative links.

-- Step 1: Add nullable narrative_id
ALTER TABLE claims ADD COLUMN IF NOT EXISTS narrative_id UUID REFERENCES narrative(id) ON DELETE CASCADE;

-- Step 2: Backfill from scene relationship
-- narrative_einheiten was renamed to narrative_units in 20260529000001_english_naming.sql
UPDATE claims c
SET narrative_id = nu.narrative_id
FROM narrative_units nu
WHERE c.scene_id = nu.id
  AND c.narrative_id IS NULL;

-- Step 3: Make scene_id nullable (analysis-level claims have no scene)
ALTER TABLE claims ALTER COLUMN scene_id DROP NOT NULL;

-- Step 4: Index for narrative-scoped claim lookups
CREATE INDEX IF NOT EXISTS idx_claims_narrative_id ON claims(narrative_id);
