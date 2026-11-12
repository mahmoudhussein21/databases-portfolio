"""Refresh Parquet from SQLite history, or verify an existing Parquet copy.

    uv run --with duckdb python Module06a/refresh.py
    uv run --with duckdb python Module06a/refresh.py --check
"""
import argparse
import csv
import hashlib
import os
from pathlib import Path
import sqlite3
import time

import duckdb

HERE = Path(__file__).resolve().parent
SQLITE = HERE / "history.db"
PARQUET = HERE / "report_history.parquet"
STAGING_CSV = HERE / "history_export.csv"
STAGING_PARQUET = HERE / "report_history.next.parquet"
FIELDS = ("job_id", "machine_id", "site", "technician",
          "part_no", "part_price", "done_on")


def quoted(path):
    return "'" + str(path).replace("'", "''") + "'"


def db_metrics():
    with sqlite3.connect(SQLITE) as db:
        return db.execute(
            "SELECT COUNT(*), ROUND(SUM(part_price),2) FROM report_history"
        ).fetchone()


def parquet_metrics(path):
    with duckdb.connect() as db:
        return db.execute(f"""SELECT COUNT(*), ROUND(SUM(part_price),2)
                      FROM read_parquet({quoted(path)})""").fetchone()


def verify(path):
    expected = db_metrics()
    actual = parquet_metrics(path)
    print(f"SQLite: rows={expected[0]}, rounded price sum={expected[1]}")
    print(f"Parquet: rows={actual[0]}, rounded price sum={actual[1]}")
    if expected[0] != actual[0] or abs(expected[1] - actual[1]) > 0.01:
        raise SystemExit("CHECK FAILED: Parquet does not match SQLite counts/sums.")
    print("CHECK PASSED: row count and rounded price sum match.")
    return expected


def checksum(path):
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def build():
    start = time.perf_counter()
    with sqlite3.connect(SQLITE) as db, STAGING_CSV.open("w", newline="", encoding="utf8") as f:
        writer = csv.writer(f)
        writer.writerow(FIELDS)
        cursor = db.execute("SELECT " + ", ".join(FIELDS) + " FROM report_history")
        while batch := cursor.fetchmany(25_000):
            writer.writerows(batch)
    try:
        with duckdb.connect() as db:
            db.execute(f"""
                COPY (SELECT CAST(job_id AS BIGINT) AS job_id, machine_id, site,
                             technician, part_no, CAST(part_price AS DOUBLE) AS part_price,
                             CAST(done_on AS DATE) AS done_on
                      FROM read_csv_auto({quoted(STAGING_CSV)}, header=true))
                TO {quoted(STAGING_PARQUET)} (FORMAT PARQUET, COMPRESSION SNAPPY)
            """)
        verify(STAGING_PARQUET)
        os.replace(STAGING_PARQUET, PARQUET)
        print(f"Refreshed rows={db_metrics()[0]}, checksum SHA256={checksum(PARQUET)}")
        print(f"Parquet size MiB={PARQUET.stat().st_size / (1024**2):.3f}")
        print(f"Refresh elapsed ms={(time.perf_counter()-start)*1000:.1f}")
    finally:
        STAGING_CSV.unlink(missing_ok=True)
        STAGING_PARQUET.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Verify without rebuilding")
    args = parser.parse_args()
    if not SQLITE.exists():
        raise SystemExit("Missing Module06a/history.db; run prepare.py first.")
    if args.check:
        if not PARQUET.exists():
            raise SystemExit("Missing report_history.parquet; run refresh.py first.")
        verify(PARQUET)
        print("SHA256:", checksum(PARQUET))
    else:
        build()


if __name__ == "__main__":
    main()
