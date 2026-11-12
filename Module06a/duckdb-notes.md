# DuckDB study notes — Module 6a

## What the two engines are used for

- **SQLite** is a row-oriented database useful for operational data: lots of small inserts, updates, and lookups.
- **DuckDB** is an analytical engine designed for scanning and grouping large datasets. It can query a Parquet file directly, without importing it into a database server.
- **Parquet** stores values by column, with compression and per-group statistics. A query that asks for four columns can avoid reading the other three columns.
- This module's comparison is about **workload**, not one engine always being faster.

## Round 1 — Build the history

Module 5 produces 200,000 job-part rows. Ten copies give 2,000,000. The new `job_id` adds `k * 1000000` to separate each quarter's job identifiers. Each quarter shifts dates by `k * 91` days; 90 days would make the periods overlap. Calendar months cannot be replaced reliably by a fixed number of days because months have different lengths.

## Round 2 — Check the conversion

A matching **row count alone is not proof of data equality**. The lab checks both count and rounded `SUM(part_price)`. The race script checks grouped results as well. For real financial records, an additional comparison by keys and stronger data reconciliation would be needed.

The original SQLite file is row-oriented. The Parquet copy is columnar, so the aggregate can read a few relevant columns rather than full rows. Compression also makes repeated values cheaper to store.

## Round 3 — Compare fairly

- Measure exactly the same report in both engines.
- Warm up both engines first, then alternate SQLite and DuckDB five times.
- Report the **median** (middle reading), not the fastest run, and show the spread.
- Validate the grouped results before interpreting performance.
- A large speedup for monthly reports does not imply faster point lookups.

## Round 4 — Read the plan

`EXPLAIN QUERY PLAN` in SQLite reports the access approach, such as `SCAN` or use of an index. `EXPLAIN ANALYZE` in DuckDB executes the query and reports operators, rows, and time. Look for the Parquet scan, the columns listed as projections, and the grouped result. The exact operator names and counts depend on the DuckDB version and the query filter.

## Round 5 — Find the boundary

A single indexed row lookup and many tiny inserts are operational workloads (OLTP). A historical sum over millions of rows is analytical (OLAP). DuckDB can handle both kinds of SQL, but its strengths are large scans and aggregates; the measured comparison should decide which to use here. Batching inserts reduces per-statement overhead, but does not change the type of workload.

## Round 6 — Keep the analytical copy fresh

The proposed process is an end-of-shift or nightly refresh from SQLite into a new Parquet file. `refresh.py` writes a temporary CSV and Parquet file, checks the row count and rounded total price, then replaces the existing Parquet file. `--check` verifies the current copy without rebuilding it. If a refresh fails, reports should clearly show the date of the last successful update; a stale report must not be presented as current.

The count and total-price check can miss two changes that cancel each other out. A production system should also verify keys, critical aggregates, and a refresh timestamp.

## Optional observations to investigate

- Joining a small JSON device file with Parquet is possible inside DuckDB.
- Sorting Parquet rows by date may make row-group min/max statistics more useful for skipping data.
- zstd compression may reduce file size relative to snappy, but the size and speed trade-off should be measured.

## Sources

- Module 6a assignment, rounds 1–7.
- DuckDB docs: https://duckdb.org/docs/
- Parquet: https://parquet.apache.org/docs/overview/
- SQLite plans: https://sqlite.org/eqp.html
