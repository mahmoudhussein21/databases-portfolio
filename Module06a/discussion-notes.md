# Module 6a — Review questions and answers

These notes organize the discussion prompts from the module. They are a study resource, not a record of a meeting.

**Why do ten quarters produce 2 million rows?** The Module 5 report has 200,000 rows. A cross join with ten quarter values creates ten copies of each row, so 200,000 × 10 = 2,000,000.

**How can we check that a Parquet export is correct?** Compare row counts and totals, then check that important grouped reports return the same values. Matching file sizes would not prove that the records match.

**Why might DuckDB be faster on monthly reporting?** It reads compressed columns from Parquet and can perform large aggregates efficiently. SQLite is reading rows in its operational file, including data that the query may not need.

**Why do we measure several times?** The first run may load file pages into memory. A median of interleaved runs is less sensitive to a single slow run.

**When is DuckDB a poor choice?** Many individual inserts and point lookups are better handled by an operational database such as SQLite. The `boundary.py` script measures this rather than assuming it.

**What if the analytical copy is one day old?** It may miss recent jobs and give outdated totals. The report should display its refresh age and should not claim to be current.

**Is a matching row count and total price enough?** No. Two incorrect rows could cancel each other out. Stronger row-level and key-based checks are needed for production.

**What is the lesson from Module 5?** Denormalization can simplify reads but duplicates facts and makes updates more expensive. Module 6a moves heavy reports to a different engine rather than adding more copied columns to the operational database.
