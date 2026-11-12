# Module 6a — The Analytical Engine (DuckDB)

This module compares an operational SQLite database with an analytical DuckDB workflow that reads Parquet files. The same data is tested in both engines, so the comparison is about the engines rather than different datasets.

## How to run

From the root of this databases portfolio, first make sure `Module05/normalize.db` exists. If it is missing, rebuild it with `python3 Module05/run_all.py`.

Run the whole Module 6a experiment on your Mac:

```sh
uv run --with duckdb python Module06a/run_all.py
```

The command installs DuckDB into a temporary `uv` environment if necessary, then runs every script and saves the actual timings from your machine. Run it before committing, because benchmark values depend on the computer and installed software.

## The six rounds

| Round | Code | Evidence generated locally |
|---|---|---|
| 1. Build | [prepare.py](prepare.py) | `prepare_results.txt`, `history.db`, 200k-row CSV |
| 2. Convert | [to_parquet.py](to_parquet.py) | `conversion_results.txt`, `report_history.parquet` |
| 3. Race | [race.py](race.py) | `race_results.txt` (two aggregates, five interleaved runs each) |
| 4. Plan | [plan.py](plan.py) | `plan_results.txt` (SQLite plan and DuckDB operator timings) |
| 5. Boundary | [boundary.py](boundary.py) | `boundary_results.txt` (1,000 inserts and point lookups) |
| 6. Decide | [generate_memo.py](generate_memo.py) | `decision-memo.md` from local measured numbers |

The core homework is covered by [optional.py](optional.py), which creates a zstd-compressed Parquet copy and also tries the JSON and Parquet row-group experiments. The intense refresh track is covered by [refresh.py](refresh.py), including two rebuilds and two successful `--check` runs. The script uses an atomic file replacement after a passing verification.

## Notes and reflection

- [DuckDB notes](duckdb-notes.md) — concepts, queries, performance reasoning, and links.
- [Questions and answers](discussion-notes.md) — preparation for peer discussion; not a record of conversations.
- [Reflection 06a](../Reflections/ref06a.md).

## Source data and integrity

The source is the 200,000-row `report_jobpart` table built in Module 5. Ten date-shifted copies create 2,000,000 rows in SQLite and Parquet. The conversion script verifies that **both have the same row count and rounded sum of part prices**. The benchmarking script also checks that grouped results match before measuring the time. The refresh verification checks counts and sums; it does **not** guarantee every individual row is identical.

## Files excluded from Git

Database (`.db`), CSV, Parquet, JSON and temporary generated files are excluded in `.gitignore` because they are large or reproducible. The scripts, notes, reflection, and text evidence **are** included.

## References

- [DuckDB documentation](https://duckdb.org/docs/)
- [SQLite query planner](https://sqlite.org/eqp.html)
- [Apache Parquet](https://parquet.apache.org/docs/overview/)
