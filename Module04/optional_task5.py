"""Optional: show why AFTER INSERT is a clearer default than BEFORE INSERT."""
import sqlite3
from pathlib import Path

HERE = Path(__file__).resolve().parent
SETUP = (HERE / "setup.sql").read_text(encoding="utf-8")
TRIGGERS = (HERE / "triggers.sql").read_text(encoding="utf-8")


def check(kind):
    db = sqlite3.connect(":memory:")
    db.execute("PRAGMA foreign_keys = ON")
    db.executescript(SETUP)
    db.executescript(TRIGGERS)
    db.execute("INSERT INTO sensor VALUES (2,'cnc-01','vib_rms','mm/s')")
    db.execute("DROP TRIGGER trg_vib_alarm")
    db.execute("CREATE TABLE timing_observation(stage TEXT, already_visible INTEGER)")
    # The same alarm action is performed; only trigger timing changes.
    db.executescript(f"""CREATE TRIGGER trg_vib_alarm {kind} INSERT ON reading
      WHEN NEW.value > 2.0 AND
      (SELECT metric FROM sensor WHERE sensor_id=NEW.sensor_id)='vib_rms'
      BEGIN
        INSERT INTO timing_observation(stage, already_visible)
        SELECT '{kind}', COUNT(*) FROM reading
          WHERE sensor_id=NEW.sensor_id AND ts=NEW.ts;
        INSERT INTO alarm(sensor_id, ts, value, reason)
        VALUES (NEW.sensor_id, NEW.ts, NEW.value, 'vibration over 2.0 mm/s');
      END;""")
    db.execute("INSERT INTO reading(sensor_id, ts, value, interval_s) VALUES (2,'2026-03-01 09:00:00',2.7,1)")
    already_visible = db.execute("SELECT already_visible FROM timing_observation").fetchone()[0]
    alarm_count = db.execute("SELECT COUNT(*) FROM alarm").fetchone()[0]
    assert already_visible == (0 if kind == "BEFORE" else 1)
    assert alarm_count == 1
    try:
        db.execute("INSERT INTO reading(sensor_id, ts, value, interval_s) VALUES (2,'2026-03-01 09:00:01',9000,1)")
        raise AssertionError("Invalid reading was accepted")
    except sqlite3.IntegrityError:
        pass
    assert db.execute("SELECT COUNT(*) FROM alarm").fetchone()[0] == 1
    assert db.execute("SELECT COUNT(*) FROM timing_observation").fetchone()[0] == 1
    db.close()
    return f"{kind} INSERT: the reading was {'not yet' if kind == 'BEFORE' else 'already'} in reading (matching rows = {already_visible}); alarm rows = {alarm_count}. Invalid reading rolled back without an alarm."


def run():
    return check("BEFORE") + "\n" + check("AFTER") + "\n"


if __name__ == "__main__":
    print(run(), end="")
