"""Show unsafe SQL string formatting versus safe parameter binding (read-only demo)."""
from pathlib import Path
import sqlite3

DB = Path(__file__).with_name('warehouse.db')
if not DB.is_file():
    raise SystemExit('warehouse.db not found; run setup.sql first')


def vulnerable(conn: sqlite3.Connection, name: str):
    # Unsafe because name becomes executable SQL syntax.
    sql = f"SELECT customer_id, name FROM customer WHERE name = '{name}'"
    return conn.execute(sql).fetchall()


def safe(conn: sqlite3.Connection, name: str):
    # Placeholder binds a string value, so the text cannot change the SQL structure.
    sql = 'SELECT customer_id, name FROM customer WHERE name = ?'
    return conn.execute(sql, (name,)).fetchall()


def main():
    # Query-only database connection, so the demonstration cannot alter data.
    with sqlite3.connect(f'file:{DB.as_posix()}?mode=ro', uri=True) as conn:
        test_value = "' OR '1'='1"
        regular = vulnerable(conn, 'Customer 1')
        attacked = vulnerable(conn, test_value)
        protected = safe(conn, test_value)
        try:
            vulnerable(conn, "O'Brien")
            apostrophe_broke_unsafe = False
        except sqlite3.Error:
            apostrophe_broke_unsafe = True
        apostrophe_safe = safe(conn, "O'Brien")
        assert len(regular) == 1, len(regular)
        assert len(attacked) == 2000, len(attacked)
        assert protected == [], protected
        assert apostrophe_broke_unsafe
        assert apostrophe_safe == []
        print('Normal lookup:', regular)
        print('Unsafe injected lookup returns:', len(attacked), 'rows (should be zero)')
        print('Safe parameterized lookup returns:', protected)
        print('Apostrophe in customer name breaks unsafe lookup:', apostrophe_broke_unsafe)
        print('Apostrophe in customer name is safe when bound:', apostrophe_safe)
        print('Checks passed: only the unsafe SQL is affected by the injection string.')


if __name__ == '__main__':
    main()
