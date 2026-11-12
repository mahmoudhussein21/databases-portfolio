# Module 3 — SQL Notes

## References and concepts

- [SQLite — EXPLAIN QUERY PLAN](https://www.sqlite.org/eqp.html): distinguishing a table `SCAN` from an indexed `SEARCH`.
- [SQLite — Query Planner](https://www.sqlite.org/queryplanner.html): understanding when an index may help.
- [OWASP — SQL Injection Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html): using parameters instead of combining input into SQL text.
- Module 3 course workbook: relational algebra mapping, SQL logical order, and index experiments.

## Workstream 1 — Relational algebra and SQL

- `σ` = filter rows (`WHERE`); `π` = choose columns (`SELECT`); `⋈` = join (`JOIN ... ON`); `γ` = aggregation (`GROUP BY`).
- One verified conversion is in [task4_algebra.md](task4_algebra.md).

## Workstream 2 — Clause order

Written order: `SELECT → FROM → WHERE → GROUP BY → HAVING → ORDER BY`.
Logical order: `FROM → WHERE → GROUP BY → HAVING → SELECT → ORDER BY`.

The output alias `revenue` is defined in the `SELECT` list, so relying on it in `WHERE` is not portable SQL. The filter should use a column or expression available at the `WHERE` stage. Note: SQLite supports some alias references as a nonstandard extension, so a purported failure should be tested on its actual database engine.

## Workstream 3 — Plan vocabulary

- `SCAN` generally means a full walk through a table or index.
- `SEARCH USING INDEX` means the index is used to narrow the candidate records.
- `SEARCH USING COVERING INDEX` means the index contains everything that query needs, avoiding extra table lookups.

The `plan_safari.txt` experiment showed that adding `ix_job_tech` changed the equality query on `maint_job.technician` from `SCAN` to `SEARCH`. The leading-wildcard `LIKE '%ei%'` query remained a `SCAN`.

## Workstream 4 — Tuning and security

- Indexes can help a selective lookup but hurt an aggregation. The benchmark demonstrated both outcomes.
- `WHERE date(ordered_on) = '2026-02-14'` did not use the ordinary date-column index.
- Bound parameters stop user-supplied text from changing SQL syntax. The injection demonstration tested this.

## Task A — Plan safari

The three queries, baseline plan predictions, and actual SQLite plans are recorded in [plan_safari.txt](plan_safari.txt). The equality search on `technician` benefited from a new index; querying `machine` did not because no index was added there; a leading-wildcard `LIKE` did not benefit.

## Task B — Algebra check

For `SELECT job_id, machine_name FROM maint_job WHERE technician = 'Beier'`, the equivalent algebra is projection of a selection: `π_{job_id,machine_name}(σ_{technician='Beier'}(maint_job))`. Both versions keep the same records and columns. See [task4_algebra.md](task4_algebra.md).

## Task C — Catch-up discussion points

I was not present for the live neighbouring-pod comparison. I reviewed these issues independently as preparation for a follow-up conversation:

1. Did anyone see a different query plan on another SQLite version?
2. Why was the new index not helpful for the city revenue report?
3. Why did `LIKE '%ei%'` remain a scan after adding an index?
4. How do bound parameters prevent SQL injection?

These are study questions, not recorded agreements from a meeting.

## Curiosities (with source)

- `EXPLAIN QUERY PLAN` shows `USE TEMP B-TREE FOR count(DISTINCT)` — grouping distinct customers has a real planning cost. (Module 3 Task 1; `task1_results.txt`)
- The new `order_line.order_id` index **slowed** the revenue report. (Module 3 Task 2; `benchmark_results.txt`)
- An index on `product_id` helped a lookup but not the city report. (Module 3 Task 2; `benchmark_results.txt`)
- Input containing an apostrophe broke the vulnerable SQL, while a bound parameter handled it safely. (Module 3 Task 3; `injection_results.txt`)

## LLM verification

The LLM-assisted revenue query was checked by executing it, inspecting the query plan, checking the year filter, using `COUNT(DISTINCT)` instead of counting repeated line rows, and independently calculating the totals. See [task1_analysis.md](task1_analysis.md). The benchmark also showed why the suggestion to add indexes requires measurement rather than acceptance by default.
