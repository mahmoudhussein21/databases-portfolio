"""Measure 10,000 inserts with and without the alarm trigger, three runs each."""
import sqlite3
from pathlib import Path
from statistics import median
from time import perf_counter

HERE = Path(__file__).resolve().parent
SETUP = (HERE / "setup.sql").read_text(encoding="utf-8")
TRIGGERS = (HERE / "triggers.sql").read_text(encoding="utf-8")
ROWS = [(2, f"2026-03-02 {n//3600:02d}:{(n%3600)//60:02d}:{n%60:02d}",
         2.7 if n % 3 == 0 else 1.1, 1) for n in range(10000)]


def single_run(with_alarm):
    db = sqlite3.connect(":memory:")
    db.execute("PRAGMA foreign_keys = ON")
    db.executescript(SETUP)
    db.executescript(TRIGGERS)
    db.execute("INSERT INTO sensor VALUES (2,'cnc-01','vib_rms','mm/s')")
    if not with_alarm:
        db.execute("DROP TRIGGER trg_vib_alarm")
    start = perf_counter()
    with db:
        db.executemany("""INSERT INTO reading(sensor_id, ts, value, interval_s)
                          VALUES (?, ?, ?, ?)""", ROWS)
    elapsed_ms = (perf_counter() - start) * 1000
    readings = db.execute("SELECT COUNT(*) FROM reading").fetchone()[0]
    alarms = db.execute("SELECT COUNT(*) FROM alarm").fetchone()[0]
    assert readings == len(ROWS)
    assert alarms == (3334 if with_alarm else 0)
    db.close()
    return elapsed_ms, alarms


def run():
    lines = [f"SQLite {sqlite3.sqlite_version}",
             "10,000 inserts per run; in-memory database; 3 runs per case; times include transaction commit."]
    results = {}
    for name, flag in [("Without alarm trigger", False), ("With alarm trigger", True)]:
        samples = [single_run(flag) for _ in range(3)]
        times = [round(x[0], 2) for x in samples]
        med = round(median(x[0] for x in samples), 2)
        results[name] = med
        lines.append(f"{name}: runs (ms) = {times}; median = {med} ms; alarm rows = {samples[-1][1]}")
    lines.append(f"Median difference (with - without): {round(results['With alarm trigger'] - results['Without alarm trigger'], 2)} ms")
    lines.append("The audit trigger is present in both scenarios to isolate the alarm-trigger cost.")
    lines.append("Timings vary between computers; run this script locally for Mac-specific results.")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    print(run(), end="")
