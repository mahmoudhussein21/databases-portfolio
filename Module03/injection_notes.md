# Task 3 — SQL injection test

A string-built SQL query lets input text become part of the SQL command. With the value `' OR '1'='1`, the unsafe equality condition becomes a condition that is always true, so it returns all **2,000** customers instead of no matching customer. A name with an apostrophe such as `O'Brien` can also break the unsafe query's SQL syntax.

The parameterized version uses `WHERE name = ?` and passes the name separately as a value. With the injection string, it returns **zero** customers. A normal customer name returns the expected record. See the tested output in [`injection_results.txt`](injection_results.txt).

**Why not filter or escape quotes by hand?** Handwritten escaping rules are easy to get wrong across quoting contexts, encodings and database implementations. Bound parameters leave the SQL statement structure fixed and let the database driver safely handle the supplied value. This is the safer general approach to SQL values. Identifiers (like table names) cannot be bound as values and require separate allowlisting.
