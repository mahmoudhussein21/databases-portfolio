"""Task A: show what weak and strict tables accept, using independent trials."""
import sqlite3


def run():
    db = sqlite3.connect(":memory:")
    db.execute("CREATE TABLE loose(sensor_id INTEGER, metric TEXT, value REAL)")
    db.executemany("INSERT INTO loose VALUES (?, ?, ?)", [
        (1, "temp_c", 9000), (1, "temp_c", "hot"), (2, "bogus", -500)
    ])
    print("LOOSE TABLE: all three bad records were accepted")
    for row in db.execute("SELECT sensor_id, metric, value, typeof(value) FROM loose"):
        print("  ", row)

    db.execute("""CREATE TABLE strict_reading(
      sensor_id INTEGER PRIMARY KEY,
      metric TEXT NOT NULL CHECK(metric IN ('temp_c','vib_rms','spindle_load')),
      value REAL NOT NULL CHECK(value BETWEEN -273.15 AND 5000)
    ) STRICT""")
    tests = [
        ("impossible temperature", (1, "temp_c", 9000), False),
        ("text instead of number", (1, "temp_c", "hot"), False),
        ("invalid metric", (2, "bogus", -500), False),
        ("NULL value", (3, "temp_c", None), False),
        ("valid but possibly inaccurate value", (4, "temp_c", 48.0), True),
    ]
    for title, row, expected in tests:
        try:
            db.execute("INSERT INTO strict_reading VALUES (?, ?, ?)", row)
            accepted = True
            result = "accepted"
        except sqlite3.Error as exc:
            accepted = False
            result = f"rejected ({type(exc).__name__}: {exc})"
        assert accepted == expected, (title, result)
        print(f"STRICT TABLE / {title}: {result}")

    # CHECK does not reject NULL by itself: NOT NULL is required for that rule.
    db.execute("CREATE TABLE only_check(value REAL CHECK(value > 0))")
    db.execute("INSERT INTO only_check(value) VALUES (NULL)")
    assert db.execute("SELECT COUNT(*) FROM only_check").fetchone()[0] == 1
    print("CHECK without NOT NULL: NULL accepted")
    print("Notes: a plausible but incorrect sensor value may still pass all constraints.")
    db.close()


if __name__ == "__main__":
    run()
