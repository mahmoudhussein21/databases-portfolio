"""Compare the *same* aggregates, warmed and interleaved, using five-run medians."""
import json
from pathlib import Path
import sqlite3
import statistics
import time
import duckdb

HERE = Path(__file__).resolve().parent
SQLITE = HERE / "history.db"
PARQUET = HERE / "report_history.parquet"
RUNS = 5

DASHBOARD = """SELECT machine_id, site, technician, SUM(part_price) AS cost
FROM {source} WHERE done_on >= '2026-01-01'
GROUP BY machine_id, site, technician ORDER BY machine_id, site, technician"""
MONTHLY_SQLITE = """SELECT strftime('%Y-%m', done_on) AS month, machine_id,
COUNT(*) AS lines, SUM(part_price) AS cost
FROM report_history GROUP BY month, machine_id ORDER BY month, machine_id"""
MONTHLY_DUCKDB = """SELECT strftime(done_on, '%Y-%m') AS month, machine_id,
COUNT(*) AS lines, SUM(part_price) AS cost
FROM read_parquet('{pq}') GROUP BY month, machine_id ORDER BY month, machine_id"""


def same_rows(a, b):
    if len(a) != len(b):
        return False
    for x, y in zip(a, b):
        if x[:-1] != y[:-1] or abs(float(x[-1]) - float(y[-1])) > 0.02:
            return False
    return True


def timed(fn):
    start = time.perf_counter()
    fn()
    return (time.perf_counter() - start) * 1000


def main():
    if not SQLITE.is_file() or not PARQUET.is_file():
        raise SystemExit("Run prepare.py and to_parquet.py first.")
    sq, du = sqlite3.connect(SQLITE), duckdb.connect()
    pq = str(PARQUET).replace("'", "''")
    tasks = (
        ("dashboard", DASHBOARD.format(source="report_history"),
         DASHBOARD.format(source=f"read_parquet('{pq}')")),
        ("monthly", MONTHLY_SQLITE, MONTHLY_DUCKDB.format(pq=pq)),
    )
    metrics = {}
    try:
        for name, sq_sql, du_sql in tasks:
            first, second = sq.execute(sq_sql).fetchall(), du.execute(du_sql).fetchall()
            if not same_rows(first, second):
                raise AssertionError(f"{name} report results differ across engines")
            # Warm-up happened in the comparison above; time results only now.
            sq_time, du_time = [], []
            for _ in range(RUNS):
                sq_time.append(timed(lambda: sq.execute(sq_sql).fetchall()))
                du_time.append(timed(lambda: du.execute(du_sql).fetchall()))
            sm, dm = statistics.median(sq_time), statistics.median(du_time)
            metrics[name] = {"groups": len(first), "sqlite_median_ms": round(sm, 3),
                             "duckdb_median_ms": round(dm, 3),
                             "sqlite_min_ms": round(min(sq_time), 3),
                             "sqlite_max_ms": round(max(sq_time), 3),
                             "duckdb_min_ms": round(min(du_time), 3),
                             "duckdb_max_ms": round(max(du_time), 3),
                             "speed_ratio": round(sm / dm, 2) if dm else None}
            print(f"{name}: matching groups={len(first)} | "
                  f"SQLite median {sm:.2f} ms [{min(sq_time):.2f}-{max(sq_time):.2f}] | "
                  f"DuckDB median {dm:.2f} ms [{min(du_time):.2f}-{max(du_time):.2f}] | "
                  f"ratio={sm/dm:.2f}x")
    finally:
        sq.close()
        du.close()
    (HERE / "race_metrics.json").write_text(json.dumps(metrics, indent=2) + "\n")
    print("Both engines returned matching grouped values for both reports.")


if __name__ == "__main__":
    main()
