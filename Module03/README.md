# Module 3 — LLM-Assisted SQL and Query Profiling

This module covers writing SQL reports, understanding query plans, benchmarking indexes, representing queries in relational algebra, and preventing SQL injection.

## Files and evidence

| Assignment | Files |
|---|---|
| Data setup | [setup.sql](setup.sql) |
| Task A — Index plan safari | [plan_safari.txt](plan_safari.txt), [sql-notes.md](sql-notes.md) |
| Task B & Task 4 — Relational algebra | [task4_algebra.md](task4_algebra.md) |
| Task C — Catch-up notes | [sql-notes.md](sql-notes.md) |
| Task 1 — SQL report and plan | [task1_dashboard.sql](task1_dashboard.sql), [task1_analysis.md](task1_analysis.md), [task1_results.txt](task1_results.txt) |
| Task 2 — Benchmark | [bench.py](bench.py), [benchmark.md](benchmark.md), [benchmark_results.txt](benchmark_results.txt) |
| Task 3 — SQL injection | [injection_demo.py](injection_demo.py), [injection_notes.md](injection_notes.md), [injection_results.txt](injection_results.txt) |
| Task 5 — Optional rewrite | [task5_window_and_subquery.sql](task5_window_and_subquery.sql), [task5_results.txt](task5_results.txt) |
| Reflection | [Reflection 03](../Reflections/ref03.md) |

## Run it on macOS from the repository root

```bash
mkdir -p Module03
sqlite3 Module03/warehouse.db < Module03/setup.sql
sqlite3 Module03/warehouse.db "SELECT COUNT(*) FROM orders; SELECT COUNT(*) FROM order_line;"
sqlite3 Module03/warehouse.db < Module03/task1_dashboard.sql
python3 Module03/bench.py
python3 Module03/injection_demo.py
```

Expected row counts are **60,000** and **240,000**. The database file `warehouse.db` is intentionally excluded from version control, and is reproducible using `setup.sql`. Benchmark results depend on SQLite version, machine and workload. Results currently included were captured on a test environment with SQLite 3.46.1; running locally provides your own measurements.

The catch-up section documents independent study rather than implying attendance at a group discussion.
