"""Task 4: show the view, read-only URI, file permissions and query_only."""
import os
import sqlite3
import stat
from pathlib import Path

HERE = Path(__file__).resolve().parent
DB = HERE / "edge.db"


def run():
    assert DB.exists(), "Run python3 Module04/run_all.py first"
    lines = []
    original_mode = stat.S_IMODE(DB.stat().st_mode)
    os.chmod(DB, 0o444)
    try:
        mode = stat.S_IMODE(DB.stat().st_mode)
        lines.append(f"chmod 444: file permission bits now {oct(mode)}")
        ro_uri = DB.resolve().as_uri() + "?mode=ro"
        with sqlite3.connect(ro_uri, uri=True) as db:
            count = db.execute("SELECT COUNT(*) FROM reading").fetchone()[0]
            lines.append(f"mode=ro SELECT COUNT(*) FROM reading: {count}")
            try:
                db.execute("DELETE FROM reading")
                raise AssertionError("Read-only connection allowed DELETE")
            except sqlite3.OperationalError as err:
                lines.append(f"mode=ro DELETE rejected: {err}")
            rows = db.execute("SELECT machine_id, metric, peak, n FROM machine_health ORDER BY metric").fetchall()
            lines.append(f"machine_health view (machine_id, metric, peak, n): {rows}")
    finally:
        os.chmod(DB, original_mode)
        lines.append(f"Restored original permission mode: {oct(original_mode)}")

    with sqlite3.connect(DB) as db:
        db.execute("PRAGMA query_only = ON")
        assert db.execute("PRAGMA query_only").fetchone()[0] == 1
        try:
            db.execute("DELETE FROM reading")
            raise AssertionError("query_only connection allowed DELETE")
        except sqlite3.OperationalError as err:
            lines.append(f"PRAGMA query_only DELETE rejected: {err}")
    lines.append("A view is a convenient report interface, not a security boundary for someone with raw database-file access.")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    print(run(), end="")
