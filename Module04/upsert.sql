-- Task 2: replay-safe ingestion; the unique index is created in setup.sql.
INSERT INTO reading(sensor_id, ts, value, interval_s)
VALUES (1, '2026-03-01 08:00:00', 41.7, 1)
ON CONFLICT(sensor_id, ts) DO UPDATE
    SET value = excluded.value, interval_s = excluded.interval_s
    WHERE reading.value IS NOT excluded.value
       OR reading.interval_s IS NOT excluded.interval_s;

-- Check for duplicate timestamps: should return no rows.
SELECT sensor_id, ts, COUNT(*) AS copies
FROM reading
GROUP BY sensor_id, ts
HAVING COUNT(*) > 1;
