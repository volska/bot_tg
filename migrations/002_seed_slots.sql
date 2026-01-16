CREATE EXTENSION IF NOT EXISTS pgcrypto;

WITH days AS (
  SELECT (date_trunc('day', now())::date + offs) AS d
  FROM generate_series(0, 62) AS offs
),
workdays AS (
  SELECT d FROM days WHERE EXTRACT(ISODOW FROM d) BETWEEN 1 AND 5
),
times AS (
  SELECT time '12:00' AS t
  UNION ALL SELECT time '16:00'
  UNION ALL SELECT time '18:00'
),
to_insert AS (
  SELECT
    (gen_random_uuid()) AS slot_id,
    ((w.d::timestamp + t.t) AT TIME ZONE 'Europe/Moscow') AS start_at,
    60::smallint AS duration_min
  FROM workdays w
  CROSS JOIN times t
)
INSERT INTO slots (slot_id, start_at, duration_min, status, created_at, updated_at)
SELECT slot_id, start_at, duration_min, 'FREE', now(), now()
FROM to_insert
ON CONFLICT (start_at) DO NOTHING;