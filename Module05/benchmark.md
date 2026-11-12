# Rounds 4–5 — Benchmark and storage results

The results below are measured in the environment used to build this portfolio package (SQLite 3.51.0, Darwin). Rerunning `python3 Module05/benchmark.py` on a Mac regenerates this report with Mac measurements. Hardware and caching affect the numbers.

## Verified data counts

| Table | Rows |
|---|---:|
| Flat job-part | 200,000 |
| Machine | 50 |
| Part | 10 |
| Job | 20,000 |
| Job-part link | 200,000 |
| Denormalized report | 200,000 |

Both queries returned **350 matching groups** and the total part cost was **722,610.00**. Foreign-key and SQLite integrity checks passed. The query uses the module's fixed `done_on >= '2026-03-01'` cutoff, not a moving 90-day window.

## Before/after read and write comparison

| Design | Report median (ms; 5 warm runs) | Rows affected by site change | Table data storage (KiB, excludes indexes) | Repeated data? |
|---|---:|---:|---:|---|
| 3NF (`machine`, `part`, `job`, `job_part`) | 47.425 | 1 | 3976.0 | No repeated site and price |
| Denormalized `report_jobpart` (with index) | 44.307 | 4,000 | 10832.0 | Site, technician and price repeated |

The row-change comparison is the more stable result: updating one site changes **one 3NF machine row** versus **4,000 report rows**. The measured update statements were rolled back so the example data remains unchanged.

## Index experiment

- Report WITH `ix_report_machine`: median **44.307 ms**.
- Report WITHOUT `ix_report_machine`: median **34.121 ms**.
- In this run, having that index made the report query **slower** than without it (index-free report median 34.121 ms vs indexed 44.307 ms). This result is workload-dependent.
- See `query_plans.txt` for actual `EXPLAIN QUERY PLAN` output. An index scan can repeatedly fetch table rows, whereas a full table scan can be more sequential.
- The read benchmark favored the **report table** at this scale. Do not assume one design always wins.

The raw five-run timings are preserved in [`benchmark_results.txt`](benchmark_results.txt).
