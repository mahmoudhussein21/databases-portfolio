# Module 5 — Normalization notes

## Round 1: functional dependencies (FDs)

An FD `X → Y` means that two rows with the same `X` must have the same `Y`.

| FD | Classification | Reason |
|---|---|---|
| `job_id → machine_id` | Domain assumption | Each maintenance job belongs to one machine. |
| `job_id → technician` | Domain assumption | This lab assumes one technician recorded per job. |
| `job_id → done_on` | Domain assumption | This lab assumes one completion date per job. |
| `machine_id → site` | Domain assumption | One current site is recorded for each machine. |
| `part_no → part_price` | Domain assumption | This lab uses one current price per part. Historical prices need a different model. |
| `machine_id → technician` | Merely observed in the tiny sample, not guaranteed | A machine can have jobs handled by different technicians. |
| `part_no → site` | Not a valid domain rule | The same part can be used at different sites. |

**Candidate key in the flat job-part records:** `(job_id, part_no)`, *assuming a part appears at most once in a job*. If quantity or repeated use matters, the model would need an additional key/quantity field.

### LLM cross-check

**Prompt:** "Given the Module 5 five-row flat table with job_id, machine_id, site, technician, part_no and part_price, list candidate keys and functional dependencies. Distinguish domain rules from patterns that only appear in five rows."

**Generated suggestion:** `(job_id, part_no)` as a candidate key; `job_id → machine_id, technician`; `machine_id → site`; `part_no → part_price`.

**Verification:** Those statements fit the stated assumptions. A five-row sample alone cannot *prove* the rules. In particular, `machine_id → technician` could look true in the sample but fails when technicians change between jobs. A database schema needs explicit assumptions or constraints, not only examples.

## 1NF → 2NF → 3NF

1. **1NF**: Each field stores one value. The flat job-part table has atomic fields; the earlier `parts_used='P-1001,P-1002'` design from Module 2 did not.
2. **2NF**: Remove partial dependencies from a composite key. Here `part_no → part_price` means part price should move to `part`.
3. **3NF**: Remove non-key-to-non-key dependencies. Here `machine_id → site` means site should move to `machine` rather than be copied on job rows.

The resulting tables are `machine`, `part`, `job`, and `job_part`. The generated test has 50 machines, 10 distinct parts, 20,000 jobs, and 200,000 job-part links.

**Why only 10 parts, not 40?** `k` takes the values 1–10. Thus `(k % 40)+1` produces only 2–11, even though the expression uses 40. `SELECT DISTINCT` leaves 10 part numbers.

## Round 2: three anomalies

- **Update:** One copy of `cnc-01` was changed to Bielefeld while other rows stayed in Gütersloh. The flat table now gives inconsistent sites for the same machine.
- **Insert:** A new part not yet used by a job can be inserted only with missing job columns, creating an incomplete job-part record (unless modeled separately).
- **Delete:** Removing the only job-part row for `P-0002` also loses the price information for that part.

The exact SQL and executed outputs are in `anomalies.sql` and `anomaly_results.txt`.

## Round 3: checks

- `PRAGMA foreign_keys=ON` is enabled in the setup and the Python benchmark connection.
- The generated row counts in the four 3NF tables reconstruct all 200,000 flat records.
- `part_price` is converted from `TEXT` in the flat table to `REAL` in `part`; real money applications should consider integer cents to avoid floating point rounding.

## Self-check questions from the seven gate prompts

These are independent study questions and answers, **not a record of peer discussions**.

1. **Which arrows disappear from the job-part table?** Machine site and part price move to their parent tables.
2. **How can you break the flat schema?** Change a site in just one job-part row, or delete the last use of a part.
3. **Why only 10 parts?** The recursive part counter has just 10 values.
4. **Why can plans differ?** Indexes, SQLite versions and statistics change the optimizer's choices.
5. **What costs more on an update?** Changing one machine row or thousands of copied site values in the report.
6. **What if the machine changes site after report generation?** The report becomes stale and must be refreshed or maintained by triggers.
7. **Which curiosities stood out?** The `CROSS JOIN`, prices stored as text, and an index that can slow a full scan.
