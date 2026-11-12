# Module 4 — Integrity Notes

## References

- Module 4 course workbook: the sensor readings story, integrity layers, `STRICT` tables, generated columns, triggers and `UPSERT`.
- [SQLite foreign keys](https://www.sqlite.org/foreignkeys.html): foreign-key checking must be enabled per connection.
- [SQLite STRICT tables](https://www.sqlite.org/stricttables.html): declared data types are enforced more strictly.
- [SQLite generated columns](https://www.sqlite.org/gencol.html): values derived from an SQL expression.
- [SQLite triggers](https://www.sqlite.org/lang_createtrigger.html): SQL actions that run automatically when data changes.
- [SQLite UPSERT](https://www.sqlite.org/lang_upsert.html): handle insert conflicts without making duplicate records.
- [SQLite query_only](https://www.sqlite.org/pragma.html#pragma_query_only): prevent a connection from modifying the database.

## Task A — Three layers of data integrity

| Layer | Meaning | Our example |
|---|---|---|
| Entity | Every row can be identified and required fields are present | `PRIMARY KEY`, `NOT NULL`, `UNIQUE(machine_id, metric)` |
| Referential | A relationship points to a row that exists | `reading.sensor_id` references `sensor.sensor_id` |
| Domain | Values follow business rules | `CHECK(value BETWEEN -273.15 AND 5000)` and valid metric names |

In the first test, an unconstrained table accepted a temperature of `9000`, the word `'hot'` in a numeric field, and an invalid metric `'bogus'`. The actual output is in [acceptance_results.txt](acceptance_results.txt).

The stricter table rejected those cases and also rejected `NULL` when combined with `NOT NULL`. A separate `CHECK(value > 0)` accepted `NULL`, because a `CHECK` fails only when its expression is false (zero); unknown/NULL is not false in this situation. To require a value, use `NOT NULL` too.

Another issue is that the database can reject impossible measurements but cannot prove that a plausible reading is true. A broken sensor reporting `48.0` could still pass its numeric constraints. This needs monitoring or validation outside a single-row `CHECK`.

## Follow-up concepts

**STRICT types:** a text value such as `'hot'` cannot be stored in a `REAL` column. SQLite may still convert numeric text such as `'41.5'` into a real number, so `STRICT` is not the same thing as accepting only Python floats.

**Generated columns:** the lab's `energy_j` equals `value * interval_s`. For the sample `41.5 * 1`, the stored result is `41.5`. In actual engineering, multiplying a temperature or vibration reading by seconds does not calculate joules. The formula illustrates SQLite's generated-column mechanism, but a production system would need a metric-specific unit model.

**Trigger vs CHECK:** a `CHECK` can reject a bad reading in its own row. An `AFTER INSERT` trigger can create a separate alarm row when vibration exceeds the threshold, which a simple row-level `CHECK` cannot do. The alarm trigger only handles inserts; an update to an older reading would need a separate update-trigger rule if it should also raise an alarm.

**UPSERT:** `UNIQUE(sensor_id, ts)` identifies the same measurement. `ON CONFLICT DO UPDATE` replaces a corrected value rather than adding a duplicate. The `WHERE` clause avoids making an unchanged replay count as an update, so the audit table stays meaningful.

**Access control:** PostgreSQL has roles and privileges such as `GRANT SELECT`, enforced for individual database users. SQLite does not provide its own multi-user authentication and roles. A local application can open the file read-only, use operating-system permissions, and use views to make reports simpler. The view alone does not restrict access to the underlying table. This approach fits a trusted edge device but not a multi-tenant web application where different users need separate permissions.

## Task B — Topics prepared for discussion

These are study observations and questions, not a record of a live meeting.

1. A loose SQLite table accepted the string `'hot'` in a column labelled `REAL`. Should an edge gateway trust the field's declared type without `STRICT`?
2. `CHECK` by itself did not reject `NULL`. When do we need both `CHECK` and `NOT NULL`?
3. `UNIQUE(machine_id, metric)` prevents two sensor definitions for the same machine and metric; `UNIQUE(sensor_id, ts)` prevents repeat readings. These two keys protect different rules.
4. `FOREIGN KEY` enforcement needs `PRAGMA foreign_keys = ON` on every database connection.
5. How should a system respond if a vibration reading is corrected from below the alarm limit to above it? The example trigger fires on inserts, not value updates.
6. A trigger writes extra records automatically but can slow down frequent inserts. The benchmark measures that cost.

Useful questions to bring to `#sql-questions`: how should sensors report missing data without allowing NULL in measurements, and whether a corrected high vibration should generate another alarm.

## Lab observations

- [Task 1](task1_results.txt): six invalid statements were rejected; the generated column produced `41.5`.
- [Task 2](task2_results.txt): repeated CSV ingestion kept the number of readings at four.
- [Task 3](task3_results.txt): an alarm and an audit record were generated by the correct SQL events.
- [Benchmark](trigger_benchmark_results.txt): three timed 10,000-row tests with and without the alarm trigger.
- [Task 4](task4_results.txt): `mode=ro` and `PRAGMA query_only` both refused a `DELETE`.
- [Optional Task 5](task5_results.txt): the row is not yet present during a `BEFORE INSERT` trigger, but it is present when `AFTER INSERT` runs; both versions rolled back a failed insert.

## AI verification

AI assistance was used to draft and review SQL and Python examples. The claims were checked against a real SQLite database: invalid rows were inserted deliberately, duplicate CSV imports were counted, trigger side effects were queried, read-only writes were attempted, and the trigger benchmark was repeated three times per case. The actual outputs are saved in the result files rather than relying only on a written explanation.
