-- D1 Orphan jobs
SELECT j.job_id, j.machine_name
FROM maint_job AS j LEFT JOIN machine AS m
  ON m.machine_name = j.machine_name
WHERE m.machine_name IS NULL ORDER BY j.job_id;

-- D2 Duplicate part keys
SELECT part_no, COUNT(*) AS copies
FROM part GROUP BY part_no HAVING COUNT(*)>1;

-- D3 Wrong text price comparison
SELECT part_no, unit_price FROM part
WHERE unit_price < '15' ORDER BY part_no;

-- D3 Correct numeric comparison (for contrast)
SELECT part_no, unit_price FROM part
WHERE CAST(unit_price AS NUMERIC) < 15 ORDER BY part_no;

-- D4 Invalid date pattern
SELECT machine_name, installed FROM machine
WHERE installed NOT GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]';

-- D5 Broken join of job to part
SELECT j.job_id, p.description FROM maint_job AS j
JOIN part AS p ON p.part_no = j.parts_used
ORDER BY j.job_id, p.description;

-- T1 Parts per job
SELECT job_id, parts_used,
 CASE WHEN parts_used IS NULL THEN 0
 ELSE LENGTH(parts_used)-LENGTH(REPLACE(parts_used,',',''))+1 END AS n_parts
FROM maint_job ORDER BY job_id;

-- T1 Jobs per machine (including zero)
SELECT m.machine_name, COUNT(j.job_id) AS n_jobs
FROM machine AS m LEFT JOIN maint_job AS j
  ON j.machine_name=m.machine_name
GROUP BY m.machine_name ORDER BY m.machine_name;

-- T1 Jobs per technician (name is not a declared key)
SELECT technician, COUNT(*) AS n_jobs
FROM maint_job GROUP BY technician ORDER BY technician;

-- T1 Part usage counts, split CSV; count distinct job IDs
WITH RECURSIVE tokens(job_id, remaining, token) AS (
 SELECT job_id, COALESCE(parts_used,'')||',', '' FROM maint_job
 UNION ALL
 SELECT job_id, SUBSTR(remaining,INSTR(remaining,',')+1),
        TRIM(SUBSTR(remaining,1,INSTR(remaining,',')-1))
 FROM tokens WHERE remaining<>''
)
SELECT token AS part_no, COUNT(DISTINCT job_id) AS n_jobs
FROM tokens WHERE token<>'' GROUP BY token ORDER BY token;

-- T1 Unique part codes in catalog
SELECT COUNT(DISTINCT part_no) AS distinct_parts FROM part;

-- T1 Multi-part orders
SELECT COUNT(*) AS jobs_with_multiple_parts FROM maint_job
WHERE parts_used IS NOT NULL AND INSTR(parts_used,',')>0;
