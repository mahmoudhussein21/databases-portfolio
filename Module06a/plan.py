"""Record SQLite EXPLAIN QUERY PLAN and DuckDB EXPLAIN ANALYZE on the same filter."""
from pathlib import Path
import sqlite3
import duckdb

HERE = Path(__file__).resolve().parent
DB = HERE / "history.db"
PQ = HERE / "report_history.parquet"


def main():
    sql = """SELECT machine_id, site, technician, SUM(part_price) AS cost
FROM report_history WHERE done_on >= '2026-01-01'
GROUP BY machine_id, site, technician"""
    with sqlite3.connect(DB) as con:
        sqlite_lines = con.execute("EXPLAIN QUERY PLAN " + sql).fetchall()
    print("SQLite EXPLAIN QUERY PLAN (estimated access path, no execution timings)")
    for _, _, _, line in sqlite_lines:
        print("  " + line)
    sql_d = sql.replace("FROM report_history", "FROM read_parquet('" + str(PQ).replace("'", "''") + "')")
    with duckdb.connect() as con:
        explain = con.execute("EXPLAIN ANALYZE " + sql_d).fetchone()[1]
    print("\nDuckDB EXPLAIN ANALYZE (actual operator counts and timings)")
    print(explain.replace(str(Path.home()), "~"))
    print("\nInterpretation: DuckDB reads the selected Parquet columns; "
          "SQLite scans rows, then groups them. Read the operator counts above.")


if __name__ == "__main__":
    main()
