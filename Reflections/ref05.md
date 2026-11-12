# Reflection 05 — Normalization and Denormalization

## Take-away

This module shows why a good database structure is not only about speed. In a normalized database, a machine's site and a part's price are stored once. In a denormalized report table, those values are copied into many rows. The report may be quicker to read, but changes need more work.

## What was good

The two ER sketches make the difference easier to see. The benchmark also gives a real comparison instead of assuming one design must be faster. Both queries produced the same 350 result groups, which is important before comparing their timing.

## What was difficult

One challenging point is the difference between 2NF and 3NF. In 2NF, part price should not depend on only part of the `(job_id, part_no)` key. In 3NF, the machine site should not be copied into job rows because it depends on `machine_id`, not directly on the job key. It is also easy to assume that an index will always speed up a query, but the query plan and timing can show the opposite.

## Exploration and show stoppers

The example generates 200,000 job-part rows with a `CROSS JOIN`. The flat table was separated into `machine`, `part`, `job`, and `job_part`. The benchmark verifies matching results for the normalized and reporting queries. The most important write comparison is changing one machine row in 3NF versus 4,000 rows in the report. No SQL or Python test failures remained after the final run. Measurements can change on another computer, so the benchmark script is included for repeat testing.

## Interaction with peers and instructors

The module uses short gate questions at the end of each round. Questions and possible answers are recorded in `Module05/normalization-notes.md` for independent review. No peer comparison or group discussion for this module is recorded here.

## How were AI suggestions checked?

A generated list of functional dependencies was compared with the domain assumptions rather than accepted only because the five example rows supported it. The SQL setup was executed, actual row counts and foreign-key checks were examined, and the two reporting queries were checked for matching answers. Query plans and repeated measured timings were saved. This helped separate a reasonable suggestion from a result that had actually been tested.
