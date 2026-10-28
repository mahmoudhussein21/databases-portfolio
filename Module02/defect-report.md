# Task 2 — Five proven integrity defects

All results were executed against the bundled `legacy.db` using Python’s `sqlite3` and queries are in `audit_queries.sql`.

### D1 Orphan jobs

```sql
SELECT j.job_id, j.machine_name
FROM maint_job AS j LEFT JOIN machine AS m
  ON m.machine_name = j.machine_name
WHERE m.machine_name IS NULL ORDER BY j.job_id;
```

**Observed output:**
```text
job_id | machine_name
-------+-------------
3      | cnc-05      
```

**Production impact:** Orphan job 3 (`cnc-05`) cannot be assigned to a known machine or site, giving incomplete maintenance history.

### D2 Duplicate part keys

```sql
SELECT part_no, COUNT(*) AS copies
FROM part GROUP BY part_no HAVING COUNT(*)>1;
```

**Observed output:**
```text
part_no | copies
--------+-------
P-1003  | 2     
```

**Production impact:** `P-1003` has two catalog rows: duplicate joins/charges and ambiguous lookups result.

### D3 Wrong text price comparison

```sql
SELECT part_no, unit_price FROM part
WHERE unit_price < '15' ORDER BY part_no;
```

**Observed output:**
```text
part_no | unit_price
--------+-----------
P-1001  | 12.50     
```

**Production impact:** A text-order price filter incorrectly excludes `9.90` from 'below 15', corrupting purchasing totals.

**Comparison for defect 3 (`CAST`, not lexicographic ordering):**
```text
part_no | unit_price
--------+-----------
P-1001  | 12.50     
P-1003  | 9.90      
P-1003  | 9.90      
```

### D4 Invalid date pattern

```sql
SELECT machine_name, installed FROM machine
WHERE installed NOT GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]';
```

**Observed output:**
```text
machine_name | installed
-------------+----------
RANDOM-NAME  | unknown  
```

**Production impact:** `RANDOM-NAME` has `installed='unknown'`; date calculations and preventive-maintenance scheduling fail.

### D5 Broken join of job to part

```sql
SELECT j.job_id, p.description FROM maint_job AS j
JOIN part AS p ON p.part_no = j.parts_used
ORDER BY j.job_id, p.description;
```

**Observed output:**
```text
job_id | description      
-------+------------------
2      | Coolant filter   
2      | Coolant filter   
3      | Ball bearing 6203
```

**Production impact:** Job 1 with two parts silently disappears in direct joins, under-reporting replacement history.

**Caution:** The bad join creates three result rows, not two: job 2 joins **twice** because `P-1003` is duplicated; job 3 joins once; job 1 joins zero times. SQLite accepts this query without any warning. The duplicate is separately documented in defect 2.
