# Reflection 03 — LLM-Assisted SQL and Query Profiling

## Take-away

I learned that a SQL query can return an answer but still need checking. The query plan helps me understand how the database gets the answer, and timing helps me see whether changes really improve performance.

## What was good?

The most interesting result was comparing indexes. The lookup for a single day became much faster after adding an index, but the larger city-revenue report actually became slower after a different index was added. It helped me understand that adding an index is not automatically an improvement.

## What was difficult?

At first, `SCAN`, `SEARCH`, and the temporary B-tree messages were confusing. Looking at the plans before and after adding indexes made their meaning clearer. Relational algebra was also unfamiliar, but translating a simple SQL query into selection and projection helped.

## Exploration and show stoppers

I worked with a warehouse database containing 60,000 orders and 240,000 order lines. I checked the city-revenue report using a separate calculation. I also tested a SQL injection example: joining text into a SQL string returned the wrong records, while bound parameters treated the same text as data.

## Interaction with peers and instructors

I was absent for the live pod discussion in this session. I studied the same topics independently and prepared questions about different query plans, index performance, and SQL injection that I can discuss with classmates.

## How did you verify AI suggestions?

I ran the generated SQL, reviewed `EXPLAIN QUERY PLAN`, independently compared the report totals, and repeated the performance measurements. The experiments showed that an index suggestion must be tested because some indexes made the report slower. I also ran the parameterized-query demonstration to check that unsafe input could not change the SQL structure.
