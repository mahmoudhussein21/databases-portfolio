# Reflection 06a — The Analytical Engine (DuckDB)

## Take-away

This module showed me why one database does not have to handle every type of work. SQLite is good for the normal application data, while DuckDB can read Parquet files for large reports. The important question is not just which one is faster, but which one fits the kind of query.

## What was good

The exercise keeps the same data from Module 5. It makes the comparison fair because the records do not change when the database engine changes. The scripts compare row counts and totals and then measure both engines on the same reports. I also like that the results are saved in text files, because they can be checked again.

## What was difficult

The difference between a row-based database and a column-based file is not immediately obvious. It also takes some care to measure fairly. A first run can be slower just because the computer is loading data into memory, so the script uses warm-ups and several repeated measurements.

## Exploration and show stoppers

One interesting question is how to know that an exported file still has the right data. Counting rows is useful but not enough, so the exercise also compares totals and report results. Another important limitation is that an analytical copy can become outdated. Refreshing and checking the copy needs to be part of the process.

## Interaction with peers and instructors

The module's review questions cover how to compare the engines fairly, when DuckDB is not a good choice, and what happens if a reporting file is out of date. I worked through these questions independently and recorded my answers in `Module06a/discussion-notes.md`.

## How did you verify AI suggestions?

Instead of trusting performance claims, the scripts check the data and collect timings from real runs. The benchmark compares matching query results and uses five alternating runs. The plan exercise shows what the engines actually do. The refresh check also makes it possible to detect some mistakes in the copied data, although matching totals alone cannot prove that every row is correct.
