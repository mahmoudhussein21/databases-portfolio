"""Write the operations memo from measured results, without hard-coded timings."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def data(name):
    path = HERE / name
    if not path.is_file():
        raise SystemExit(f"Missing {path}; run run_all.py first.")
    return json.loads(path.read_text())


def main():
    c = data("conversion_metrics.json")
    r = data("race_metrics.json")
    b = data("boundary_metrics.json")
    s = r["dashboard"]
    m = r["monthly"]
    memo = f"""# Recommendation to Lea Winter and Yasmin Kaya

The daily machine readings and individual write operations should stay in SQLite, while the larger historical reports should use a Parquet copy queried with DuckDB. On this machine, the dashboard report took a median of {s['sqlite_median_ms']:.2f} ms in SQLite and {s['duckdb_median_ms']:.2f} ms in DuckDB, and the monthly report took {m['sqlite_median_ms']:.2f} ms and {m['duckdb_median_ms']:.2f} ms respectively. The two engines returned matching report groups, with {c['sqlite_rows']:,} rows in each dataset. The SQLite history database occupies {c['sqlite_mib']:.2f} MiB, compared with {c['parquet_mib']:.2f} MiB for the first Parquet copy. For the point-lookup workload, SQLite took {b['sqlite']['lookups_median_ms']:.2f} ms for 1,000 lookups versus {b['duckdb']['lookups_median_ms']:.2f} ms in DuckDB, so individual application lookups should not move to the analytical engine. I recommend an automated refresh after the last shift each night, using `refresh.py`, followed by `refresh.py --check` to compare the row count and total price. If that check fails or the refresh is not completed, the reporting page should display the age of the copy and withhold reports that require current data. A matching row count and total price do not prove every row is identical, so additional reconciliation would be needed for a production system.
"""
    (HERE / "decision-memo.md").write_text(memo, encoding="utf-8")
    print("Decision memo generated using measured data: Module06a/decision-memo.md")


if __name__ == "__main__":
    main()
