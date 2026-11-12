# Module 5 — Normalization vs. Denormalization

This module compares a flat maintenance job-part table, a third-normal-form (3NF) design, and a deliberately denormalized reporting table. The exercise measures correctness, read speed, write cost, and storage.

## Evidence by round

| Round | Evidence |
|---|---|
| 1 — See it | [Functional dependencies and explanations](normalization-notes.md), [two ER sketches](er-sketches.md) |
| 2 — Break it | [Three anomaly SQL statements](anomalies.sql), [actual anomaly results](anomaly_results.txt) |
| 3 — Build it | [Reproducible setup](setup.sql), [table counts and integrity checks](benchmark_results.txt) |
| 4 — Race it | [Both SQL report queries](report_queries.sql), [actual query plans](query_plans.txt), [measured benchmark](benchmark.md) |
| 5 — Price it | [Write cost and storage](round5-storage.md), [raw benchmark numbers](benchmark_results.txt) |
| 6 — Decide | [Recommendation to the operations lead](recommendation-memo.md) |
| 7 — Harvest | [Curiosities and questions](harvest.md), [self-check gate questions](normalization-notes.md) |

[Reflection 05](../Reflections/ref05.md)

## Run the module on a Mac

From the portfolio root:

```bash
python3 Module05/run_all.py
```

This script builds `Module05/normalize.db` and reruns the three anomalies, 3NF decomposition, both reporting queries, and the benchmark. The database is a local generated file and is excluded from Git by `Module05/.gitignore`.

Alternatively, to replay the SQL setup directly with the SQLite command line:

```bash
sqlite3 Module05/normalize.db < Module05/setup.sql
```

To run the optional DuckDB comparison **if DuckDB is installed**, use:

```bash
python3 Module05/duckdb_optional.py
```

The optional DuckDB experiment is separate from the recorded SQLite benchmark.

## How to read the measured results

- Times are medians of **five warm runs**. The saved measurements can be reproduced with `python3 Module05/benchmark.py`; exact timings depend on the computer and cache.
- `EXPLAIN QUERY PLAN` is saved so the query work can be explained without relying only on a stopwatch.
- Both designs must return the same groups and total costs before comparing performance.
- A faster report is not automatically a better database: its duplicated columns need extra storage and can become stale after updates.

## Short explanation

**Normalization** keeps each fact in one place. A machine's site belongs in `machine`, and a part's price belongs in `part`. This helps prevent update, insert, and delete anomalies. **Denormalization** deliberately copies these values into a report table to simplify repeated reads, but a site change then affects many report rows. The correct choice depends on real measured performance and the cost of keeping copies synchronized.
