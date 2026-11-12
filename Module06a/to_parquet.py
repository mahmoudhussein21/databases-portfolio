"""Create a 2,000,000-row Parquet copy independently from the base CSV."""
import json
from pathlib import Path
import sqlite3
import duckdb

HERE = Path(__file__).resolve().parent
CSV = HERE / "report_jobpart.csv"
PARQUET = HERE / "report_history.parquet"
SQLITE = HERE / "history.db"


def quoted(path):
    return "'" + str(path).replace("'", "''") + "'"


def main():
    if not CSV.exists() or not SQLITE.exists():
        raise SystemExit("Run Module06a/prepare.py first.")
    con = duckdb.connect()
    con.execute(f"""
        COPY (
          SELECT CAST(r.job_id AS BIGINT) + k * 1000000 AS job_id,
                 r.machine_id, r.site, r.technician, r.part_no,
                 CAST(r.part_price AS DOUBLE) AS part_price,
                 CAST(r.done_on AS DATE) + CAST(k * 91 AS INTEGER) AS done_on
          FROM read_csv_auto({quoted(CSV)}, header=true) r
          CROSS JOIN range(0, 10) t(k)
        ) TO {quoted(PARQUET)} (FORMAT PARQUET, COMPRESSION SNAPPY)
    """)
    pq_rows, pq_sum = con.execute(f"""SELECT COUNT(*), ROUND(SUM(part_price), 2)
                          FROM read_parquet({quoted(PARQUET)})""").fetchone()
    with sqlite3.connect(SQLITE) as db:
        sq_rows, sq_sum = db.execute(
            "SELECT COUNT(*), ROUND(SUM(part_price), 2) FROM report_history"
        ).fetchone()
    if sq_rows != pq_rows or abs(sq_sum - pq_sum) > 0.01:
        raise AssertionError(f"Data mismatch: SQLite {(sq_rows,sq_sum)} / Parquet {(pq_rows,pq_sum)}")
    metrics = {"sqlite_rows": sq_rows, "parquet_rows": pq_rows,
               "sqlite_sum": sq_sum, "parquet_sum": pq_sum,
               "sqlite_mib": round(SQLITE.stat().st_size / (1024**2), 3),
               "parquet_mib": round(PARQUET.stat().st_size / (1024**2), 3)}
    (HERE / "conversion_metrics.json").write_text(json.dumps(metrics, indent=2) + "\n")
    for key, val in metrics.items():
        print(f"{key}: {val}")
    print("Checks passed: same row count and rounded total price.")


if __name__ == "__main__":
    main()
