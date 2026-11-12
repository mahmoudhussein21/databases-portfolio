"""Rebuild the reproducible lab database, execute assertions, and save evidence."""
import sqlite3
from pathlib import Path
from contextlib import redirect_stdout
from io import StringIO

from acceptance import run as acceptance_run
from ingest import ingest, load_rows
from benchmark_triggers import run as benchmark_run
from access_demo import run as access_run
from optional_task5 import run as optional_run

HERE = Path(__file__).resolve().parent
DB = HERE / "edge.db"


def write(name, content):
    (HERE / name).write_text(content.rstrip() + "\n", encoding="utf-8")


def run_acceptance():
    capture = StringIO()
    with redirect_stdout(capture):
        acceptance_run()
    write("acceptance_results.txt", capture.getvalue())


def run_tasks():
    if DB.exists():
        DB.unlink()  # This script intentionally recreates this lab-only database.
    with sqlite3.connect(DB) as db:
        db.execute("PRAGMA foreign_keys = ON")
        assert db.execute("PRAGMA foreign_keys").fetchone()[0] == 1
        db.executescript((HERE / "setup.sql").read_text(encoding="utf-8"))
        db.executescript((HERE / "triggers.sql").read_text(encoding="utf-8"))
        db.executescript((HERE / "access_control.sql").read_text(encoding="utf-8"))
        db.execute("INSERT INTO sensor VALUES (1,'cnc-01','temp_c','degC')")
        db.execute("INSERT INTO sensor VALUES (2,'cnc-01','vib_rms','mm/s')")
        db.execute("INSERT INTO reading(sensor_id, ts, value, interval_s) VALUES (1,'2026-03-01 08:00:00',41.5,1)")
        db.commit()
        lines = [f"SQLite {sqlite3.sqlite_version}",
                 "PRAGMA foreign_keys: ON",
                 "Valid seed reading: (sensor_id=1, ts=2026-03-01 08:00:00, value=41.5, interval_s=1)"]
        energy = db.execute("SELECT energy_j FROM reading WHERE sensor_id=1").fetchone()[0]
        assert energy == 41.5
        lines.append(f"Generated energy_j for seed row: {energy} (value * interval_s)")
        trials = [
            ("temperature 9000", "INSERT INTO reading(sensor_id,ts,value,interval_s) VALUES (1,'2026-03-01 08:00:01',9000,1)", "CHECK"),
            ("text hot in REAL", "INSERT INTO reading(sensor_id,ts,value,interval_s) VALUES (1,'2026-03-01 08:00:02','hot',1)", "type"),
            ("unknown sensor 99", "INSERT INTO reading(sensor_id,ts,value,interval_s) VALUES (99,'2026-03-01 08:00:03',40,1)", "FOREIGN KEY"),
            ("duplicate machine and metric", "INSERT INTO sensor VALUES (3,'cnc-01','temp_c','degC')", "UNIQUE"),
            ("missing machine_id", "INSERT INTO sensor(sensor_id,metric,unit) VALUES (3,'spindle_load','percent')", "NOT NULL"),
            ("zero interval", "INSERT INTO reading(sensor_id,ts,value,interval_s) VALUES (1,'2026-03-01 08:00:04',40,0)", "CHECK"),
        ]
        for name, sql, expected in trials:
            try:
                db.execute(sql)
                raise AssertionError(f"Rule FAILED: {name} was accepted")
            except sqlite3.Error as exc:
                error = str(exc)
                assert expected.lower() in error.lower() or (expected == "type" and "cannot store TEXT" in error), (name,error)
                lines.append(f"{name}: REJECTED -> {type(exc).__name__}: {error}")
        assert db.execute("SELECT COUNT(*) FROM reading").fetchone()[0] == 1
        write("task1_results.txt", "\n".join(lines))

        rows = load_rows()
        before = db.execute("SELECT COUNT(*) FROM reading").fetchone()[0]
        first = ingest(db, rows)
        audit1 = db.execute("SELECT COUNT(*) FROM audit").fetchone()[0]
        alarms1 = db.execute("SELECT COUNT(*) FROM alarm").fetchone()[0]
        second = ingest(db, rows)
        audit2 = db.execute("SELECT COUNT(*) FROM audit").fetchone()[0]
        alarms2 = db.execute("SELECT COUNT(*) FROM alarm").fetchone()[0]
        assert (before, first, second) == (1, 4, 4)
        assert (audit1, audit2, alarms1, alarms2) == (1, 1, 1, 1)
        assert db.execute("SELECT COUNT(*) FROM reading WHERE sensor_id=1 AND ts='2026-03-01 08:00:00'").fetchone()[0] == 1
        assert db.execute("SELECT value FROM reading WHERE sensor_id=1 AND ts='2026-03-01 08:00:00'").fetchone()[0] == 41.7
        write("task2_results.txt", f"Readings before CSV: {before}\nAfter first CSV pass: {first}\nAfter second pass: {second}\n"
              f"Audit rows after first/second pass: {audit1}/{audit2}\n"
              f"Alarm rows after first/second pass: {alarms1}/{alarms2}\n"
              "Repeated (sensor_id, ts) keys were updated instead of duplicated. Unchanged replays did not create extra audits.\n"
              "The stored corrected value for sensor 1 at 08:00:00 is 41.7.\n")

        db.execute("INSERT INTO reading(sensor_id,ts,value,interval_s) VALUES (2,'2026-03-01 09:00:00',2.7,1)")
        alarm = db.execute("SELECT sensor_id, ts, value, reason FROM alarm WHERE ts='2026-03-01 09:00:00'").fetchone()
        assert alarm == (2,'2026-03-01 09:00:00',2.7,'vibration over 2.0 mm/s')
        db.execute("UPDATE reading SET value=1.4 WHERE sensor_id=2 AND ts='2026-03-01 09:00:00'")
        updated_id = db.execute("SELECT reading_id FROM reading WHERE sensor_id=2 AND ts='2026-03-01 09:00:00'").fetchone()[0]
        audit = db.execute("SELECT reading_id, old_value, new_value FROM audit WHERE reading_id=?",(updated_id,)).fetchone()
        assert audit == (updated_id,2.7,1.4)
        db.commit()
        write("task3_results.txt", f"Alarm created by the AFTER INSERT trigger: {alarm}\n"
              f"Audit created by the AFTER UPDATE trigger (reading_id, old_value, new_value): {audit}\n"
              f"Alarm rows in database now: {db.execute('SELECT COUNT(*) FROM alarm').fetchone()[0]}\n"
              f"Audit rows in database now: {db.execute('SELECT COUNT(*) FROM audit').fetchone()[0]}\n"
              "An UPDATE to an already-inserted vibration reading is audited; the sample alarm trigger monitors INSERT events only.\n")

    write("task4_results.txt", access_run())


def main():
    run_acceptance()
    run_tasks()
    write("trigger_benchmark_results.txt", benchmark_run())
    write("task5_results.txt", optional_run())
    print("Module 4 verification passed:")
    for name in ("acceptance_results.txt", "task1_results.txt", "task2_results.txt", "task3_results.txt", "task4_results.txt", "trigger_benchmark_results.txt", "task5_results.txt"):
        print("  verified", name)
    print("Lab-only Module04/edge.db was built locally; do not commit it to GitHub.")


if __name__ == "__main__":
    main()
