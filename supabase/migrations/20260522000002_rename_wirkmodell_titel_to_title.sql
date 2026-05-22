-- Rename titel column to title in wirkmodelle table.
-- Aligns the database schema with the English naming convention used in all Python code.
ALTER TABLE wirkmodelle RENAME COLUMN titel TO title;
