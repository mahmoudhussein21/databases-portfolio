# Module 6b — Engine decision for Kortmann

| Workload | Engine | Why and what I measured | Cost | If the data is stale or missing |
| --- | --- | --- | --- | --- |
| Monthly report | Parquet + DuckDB | My 2-million-row test took 10.50 ms in DuckDB and 1,446.12 ms in SQLite. Both returned the same report totals. | The Parquet copy needs a nightly refresh. | Show the last successful refresh so people know how current the report is. |
| Sensor readings every 30 seconds | SQLite | In Module 4, the reading count stayed at 4 after I imported the CSV twice. A foreign key also rejected an unknown sensor. I would commit each batch before marking it as received and use UPSERT to handle retries. | Each reading needs a stable sensor ID and timestamp. Writes take turns. | Missing readings leave gaps. Retry the batch from the original data. |
| Vendor metadata | SQLite with a JSON column | The JSON can hold different fields for different vendors. My plan showed SEARCH using the index for `json_extract(meta, '$.vendor')`. The `->>` spelling used SCAN because it is a different expression from the one in the index. | Important fields need their own validation. The index covers the vendor expression. | A missing calibration date leaves its status unknown. |
| Dashboard sessions | SQLite | For 20,000 sessions, SQLite took 0.023 s to write and 0.104 s to read. Shelve took 1.591 s to write and 0.077 s to read. I chose SQLite for the faster batch writes and the option to count sessions by city with SQL. | Store the selected city in a column if the dashboard needs to group by it. | The user loses their saved filter and goes back to the default. |

## If I could use only one engine

I would keep SQLite. It can handle the sensor readings, metadata, and
sessions in one database. The monthly report would slow down first.
On my test data its median would go from about 11 ms to about 1.4 seconds.

## Defence notes

In my two-window test, the second SQLite writer got `database is locked`.
It could write after the first window committed, and the counter ended at 2.
The Parquet report has a different trade-off. It can read a copy of the
data quickly, and a nightly export has to keep that copy up to date.