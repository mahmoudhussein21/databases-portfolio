"""Task 2: parameterized, replay-safe CSV ingestion using executemany."""
import csv
import sqlite3
from pathlib import Path

HERE = Path(__file__).resolve().parent
UPSERT = """INSERT INTO reading(sensor_id, ts, value, interval_s)
VALUES (?, ?, ?, ?)
ON CONFLICT(sensor_id, ts) DO UPDATE
 SET value = excluded.value, interval_s = excluded.interval_s
 WHERE reading.value IS NOT excluded.value
    OR reading.interval_s IS NOT excluded.interval_s"""


def load_rows(csv_path=HERE / "readings.csv"):
    with Path(csv_path).open(newline="", encoding="utf-8") as handle:
        return [(int(r["sensor_id"]), r["ts"], float(r["value"]), int(r["interval_s"]))
                for r in csv.DictReader(handle)]


def ingest(conn, rows):
    # Each connection must enable foreign keys explicitly.
    conn.execute("PRAGMA foreign_keys = ON")
    with conn:
        conn.executemany(UPSERT, rows)
    return conn.execute("SELECT COUNT(*) FROM reading").fetchone()[0]


if __name__ == "__main__":
    db_file = HERE / "edge.db"
    if not db_file.exists():
        raise SystemExit("edge.db does not exist. Run python3 Module04/run_all.py first.")
    rows = load_rows()
    with sqlite3.connect(db_file) as conn:
        first = ingest(conn, rows)
        second = ingest(conn, rows)
        assert first == second, "Replay duplicated readings"
        print(f"First CSV pass: {first} total readings")
        print(f"Second CSV pass: {second} total readings")
        print("Replay did not create additional rows.")
