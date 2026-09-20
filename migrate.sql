-- Migration script for V6 - run this in Supabase SQL Editor
-- This fixes duplicate categories from previous buggy versions

-- Step 1: Delete duplicate categories, keeping the one with the lowest ID
DELETE FROM categories
WHERE id NOT IN (
  SELECT MIN(id) FROM categories GROUP BY name
);

-- Step 2: Reset the BIGSERIAL sequence to the next available ID
SELECT setval('categories_id_seq', (SELECT COALESCE(MAX(id), 0) FROM categories));

-- Step 3: Verify no duplicates remain
SELECT name, COUNT(*) as cnt FROM categories GROUP BY name HAVING COUNT(*) > 1;
-- Should return 0 rows
