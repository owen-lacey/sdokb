-- Step 0: Reset all optimized position data
-- Run this in the Supabase SQL editor to start fresh

-- First, clear all existing position and ordering data
UPDATE public.actors
SET
    x_100 = NULL,
    y_100 = NULL,
    ordinal_100 = NULL
WHERE ordinal_100 IS NOT NULL;

-- Then, reassign ordinal_100 based on Recognizability ranking (top 100 actors)
-- This creates a fresh baseline ordering by recognizability
WITH ranked_actors AS (
    SELECT
        person_id,
        ROW_NUMBER() OVER (ORDER BY "Recognizability" DESC) - 1 AS new_ordinal
    FROM public.actors
    WHERE "Recognizability" IS NOT NULL
    ORDER BY "Recognizability" DESC
    LIMIT 100
)
UPDATE public.actors a
SET ordinal_100 = ra.new_ordinal
FROM ranked_actors ra
WHERE a.person_id = ra.person_id;

-- Verify the reset
SELECT
    'Reset complete' as status,
    COUNT(*) as actors_with_ordinal,
    COUNT(x_100) as actors_with_x,
    COUNT(y_100) as actors_with_y
FROM public.actors
WHERE ordinal_100 IS NOT NULL;
