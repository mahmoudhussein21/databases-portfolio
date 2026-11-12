# Reflection 04 — Data Integrity, Constraints and Edge Triggers

## Take-away

I learned that the database should protect its own data instead of trusting every application that writes to it. SQLite can reject invalid values using constraints, update repeated readings using `UPSERT`, and automatically create alarm and audit records using triggers.

## What was good?

The most helpful part was seeing incorrect data rejected. The test with a temperature of `9000` failed because of a `CHECK`, and entering `'hot'` as a number failed because the table uses `STRICT`. The UPSERT test also showed why a repeated CSV upload should not create duplicate readings. Running the same file twice kept four unique readings.

## What was difficult?

I had to understand that different constraints solve different problems. `NOT NULL` prevents missing values, `FOREIGN KEY` prevents references to missing sensors, and `CHECK` controls allowed values. A detail that surprised me was that `CHECK` by itself does not reject `NULL`. Triggers were also more complex than normal inserts because they run automatically when a row changes.

## Exploration and show stoppers

The examples use a local SQLite database with sensor and reading tables. The test scripts checked invalid inserts, corrected readings, alarms, and read-only access. A vibration reading of `2.7` created an alarm, and changing it to `1.4` created an audit record. I also compared the cost of 10,000 inserts with and without the alarm trigger. The timing results are saved with the module and depend on the computer used to run them.

## Interaction with peers and instructors

I did not attend the live pod discussion for this module. I prepared an independent set of questions about why `CHECK` accepts `NULL`, when a trigger is better than a constraint, and how repeated readings can be handled safely. These are recorded in `Module04/integrity-notes.md` for later discussion.

## How did you verify AI suggestions?

I used AI assistance to prepare the SQL and Python examples, then checked them by executing the scripts on SQLite. I did not treat a suggested constraint or trigger as correct just because the code looked reasonable. I tested invalid rows one by one, checked exact error messages, ran the CSV ingestion twice, looked at the resulting alarm and audit records, and tested that read-only database connections refused writes. The recorded results are in the Module 4 folder.
