"""Extend the Module 5 report table into ten quarters of SQLite history.

Run from the portfolio root with:
    uv run --with duckdb python Module06a/prepare.py
"""
from pathlib import Path
import csv
import sqlite3

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / "Module05" / "normalize.db"
TARGET = HERE / "history.db"
CSV_PATH = HERE / "report_jobpart.csv"
EXPECTED_BASE = 200_000
QUARTERS = 10


def main():
    if not SOURCE.is_file():
        raise SystemExit(
            "Missing Module05/normalize.db. Run: python3 Module05/run_all.py "
            "and then run Module06a again."
        )
    with sqlite3.connect(SOURCE) as source:
        base_count = source.execute("SELECT COUNT(*) FROM report_jobpart").fetchone()[0]
        if base_count != EXPECTED_BASE:
            raise SystemExit(f"Expected {EXPECTED_BASE} Module 5 rows, got {base_count}.")
        if TARGET.exists():
            TARGET.unlink()
        with sqlite3.connect(TARGET) as con:
            con.execute("ATTACH DATABASE ? AS m5", (str(SOURCE),))
            con.execute("""CREATE TABLE report_history (
                job_id INTEGER, machine_id TEXT, site TEXT, technician TEXT,
                part_no TEXT, part_price REAL, done_on TEXT)""")
            # Different job_id ranges prevent collisions between quarters.
            con.execute("""
                WITH RECURSIVE q(k) AS (
                    SELECT 0 UNION ALL SELECT k + 1 FROM q WHERE k < ?
                )
                INSERT INTO report_history
                SELECT r.job_id + q.k * 1000000, r.machine_id, r.site,
                       r.technician, r.part_no, r.part_price,
                       date(r.done_on, '+' || (q.k * 91) || ' days')
                FROM m5.report_jobpart r CROSS JOIN q
            """, (QUARTERS - 1,))
            con.commit()
            actual = con.execute("SELECT COUNT(*) FROM report_history").fetchone()[0]
            if actual != EXPECTED_BASE * QUARTERS:
                raise AssertionError(f"Bad history row count: {actual}")
            total = con.execute("SELECT ROUND(SUM(part_price), 2) FROM report_history").fetchone()[0]
        # Export *only* the 200k-row base table for the independent DuckDB build.
        with CSV_PATH.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(("job_id", "machine_id", "site", "technician",
                             "part_no", "part_price", "done_on"))
            rows = source.execute("""SELECT job_id, machine_id, site, technician,
                                part_no, part_price, done_on FROM report_jobpart""")
            writer.writerows(rows)
        print(f"Source Module 5 rows: {base_count:,}")
        print(f"History SQLite rows: {actual:,}")
        print(f"History price sum (rounded): {total}")
        print(f"History SQLite size: {TARGET.stat().st_size / (1024*1024):.2f} MiB")
        print(f"Base CSV size: {CSV_PATH.stat().st_size / (1024*1024):.2f} MiB")


if __name__ == "__main__":
    main()
