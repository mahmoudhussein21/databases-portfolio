"""Compare 1,000 tiny writes and point lookups: OLTP vs. OLAP boundary."""
import json
from pathlib import Path
import sqlite3
import statistics
import time
import duckdb

HERE = Path(__file__).resolve().parent
N = 1000
REPEATS = 3
ROWS = [(i, f"k{i}", i * 1.5) for i in range(N)]


def elapsed(fn):
    start = time.perf_counter()
    fn()
    return (time.perf_counter() - start) * 1000


def test_sqlite():
    con = sqlite3.connect(":memory:")
    con.execute("CREATE TABLE s(id INTEGER PRIMARY KEY, k TEXT, v REAL)")
    def inserts():
        for r in ROWS:
            con.execute("INSERT INTO s VALUES (?, ?, ?)", r)
        con.commit()
    insert = elapsed(inserts)
    lookups = elapsed(lambda: [con.execute("SELECT v FROM s WHERE id=?", (i,)).fetchone()
                               for i in range(N)])
    con.close()
    return insert, lookups


def test_duckdb(batched=False):
    con = duckdb.connect()
    con.execute("CREATE TABLE s(id INTEGER PRIMARY KEY, k VARCHAR, v DOUBLE)")
    def inserts():
        con.execute("BEGIN TRANSACTION")
        if batched:
            con.executemany("INSERT INTO s VALUES (?, ?, ?)", ROWS)
        else:
            for r in ROWS:
                con.execute("INSERT INTO s VALUES (?, ?, ?)", r)
        con.execute("COMMIT")
    insert = elapsed(inserts)
    lookups = elapsed(lambda: [con.execute("SELECT v FROM s WHERE id=?", (i,)).fetchone()
                               for i in range(N)])
    con.close()
    return insert, lookups


def main():
    measurements = {"sqlite": [], "duckdb": [], "duckdb_executemany": []}
    for _ in range(REPEATS):
        measurements["sqlite"].append(test_sqlite())
        measurements["duckdb"].append(test_duckdb())
        measurements["duckdb_executemany"].append(test_duckdb(batched=True))
    summary = {}
    for name, pairs in measurements.items():
        summary[name] = {"inserts_median_ms": round(statistics.median(p[0] for p in pairs), 3),
                         "lookups_median_ms": round(statistics.median(p[1] for p in pairs), 3)}
        print(f"{name}: 1,000 inserts {summary[name]['inserts_median_ms']:.3f} ms; "
              f"1,000 point lookups {summary[name]['lookups_median_ms']:.3f} ms")
    (HERE / "boundary_metrics.json").write_text(json.dumps(summary, indent=2) + "\n")
    print("All writes used a single explicit transaction for comparability.")


if __name__ == "__main__":
    main()
