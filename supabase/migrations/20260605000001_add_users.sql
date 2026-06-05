-- Add name column to users table if it doesn't exist.
-- The users table already exists with profile fields.
-- This migration links narratives to users.
ALTER TABLE users ADD COLUMN IF NOT EXISTS name TEXT DEFAULT NULL;

-- Seed the single default user with a fixed, well-known UUID.
-- This UUID is referenced in code as DEFAULT_USER_ID.
INSERT INTO users (id, username, name)
VALUES ('00000000-0000-0000-0000-000000000001', 'thorsten', 'Thorsten')
ON CONFLICT (id) DO NOTHING;

-- Add user ownership to narratives (step 1: nullable for migration safety).
ALTER TABLE narrative ADD COLUMN IF NOT EXISTS user_id UUID REFERENCES users(id);

-- Assign all existing narratives to the default user if they don't have one.
UPDATE narrative SET user_id = '00000000-0000-0000-0000-000000000001' WHERE user_id IS NULL;

-- Enforce that every narrative has an owner.
ALTER TABLE narrative ALTER COLUMN user_id SET NOT NULL;

-- Index for user-scoped narrative lookups.
CREATE INDEX IF NOT EXISTS idx_narrative_user_id ON narrative(user_id);
