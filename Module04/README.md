# Module 4 — Data Integrity, Constraints and Edge Triggers

This module uses SQLite to keep machine sensor readings valid, handle repeated CSV uploads, create alarms and audit records, and demonstrate read-only access.

## Work and evidence

| Part | Files |
|---|---|
| Pod study Task A — acceptance test | [acceptance.py](acceptance.py), [acceptance_results.txt](acceptance_results.txt), [integrity-notes.md](integrity-notes.md) |
| Pod study Task B — discussion notes | [integrity-notes.md](integrity-notes.md) |
| Database setup | [setup.sql](setup.sql) |
| Task 1 — constraints | [run_all.py](run_all.py), [task1_results.txt](task1_results.txt) |
| Task 2 — UPSERT | [upsert.sql](upsert.sql), [ingest.py](ingest.py), [readings.csv](readings.csv), [task2_results.txt](task2_results.txt) |
| Task 3 — alarms and audit | [triggers.sql](triggers.sql), [task3_results.txt](task3_results.txt), [benchmark_triggers.py](benchmark_triggers.py), [benchmark.md](benchmark.md), [trigger_benchmark_results.txt](trigger_benchmark_results.txt) |
| Task 4 — access control | [access_control.sql](access_control.sql), [access_demo.py](access_demo.py), [task4_access_notes.md](task4_access_notes.md), [task4_results.txt](task4_results.txt) |
| Optional Task 5 — BEFORE vs AFTER | [optional_task5.py](optional_task5.py), [optional_task5.md](optional_task5.md), [task5_results.txt](task5_results.txt) |
| Reflection | [Reflection 04](../Reflections/ref04.md) |

## How to run

From the repository root (the folder containing `Module04`):

```bash
python3 Module04/run_all.py
```

This recreates the **lab-only** database `Module04/edge.db`, runs the constraint and ingestion checks, verifies trigger and read-only behaviour, benchmarks 10,000 inserts with and without an alarm trigger, and writes fresh result files. It intentionally replaces an existing `Module04/edge.db`; the source and evidence files are not deleted.

For an individual exercise after the full setup:

```bash
python3 Module04/ingest.py
python3 Module04/benchmark_triggers.py
python3 Module04/optional_task5.py
```

The `edge.db` file is reproducible and should **not** be uploaded to GitHub. The `.txt` outputs in this folder are evidence from a local test environment using SQLite **3.46.1**. Error wording and timings may differ on macOS or another SQLite version. Python must use SQLite 3.37 or newer because these tables use `STRICT`.

## Main findings

- Without constraints, SQLite accepted values such as `9000`, `'hot'`, and an invalid metric name.
- With `STRICT`, `CHECK`, `UNIQUE`, `NOT NULL` and a foreign key, bad records were rejected.
- A generated column correctly computed `value * interval_s` for the sample. This formula is a course example, not a physically correct energy calculation for every sensor metric.
- Four CSV records produced four unique readings, even after the CSV was imported twice. Replays with unchanged values did not create extra audit events.
- Vibration readings above 2.0 generated alarms; changing a reading produced an audit record with its old and new values.
- A read-only SQLite connection rejected `DELETE`. A reporting view is useful but cannot replace real user permissions in a multi-user application.
- The alarm trigger added measurable work to a 10,000-row insert in the test environment; measurements vary by machine.
