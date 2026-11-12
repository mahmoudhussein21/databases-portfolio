"""Reproducible per-index SQLite benchmark. Python timing is monotonic elapsed time.

Run: python3 Module03/bench.py
Requires Module03/warehouse.db, generated with Module03/setup.sql.
Each stage adds only one index; repeat the query >=3 times, show median and plan.
Database measurements depend on the computer and SQLite version.
"""
from pathlib import Path
from time import perf_counter
from statistics import median
import sqlite3

DB = Path(__file__).with_name('warehouse.db')
DASHBOARD = '''
SELECT c.city, COUNT(DISTINCT c.customer_id) AS customers,
       SUM(ol.qty * p.price) AS revenue
FROM customer c
JOIN orders o ON o.customer_id = c.customer_id
JOIN order_line ol ON ol.order_id = o.order_id
JOIN product p ON p.product_id = ol.product_id
WHERE o.ordered_on >= '2025-01-01' AND o.ordered_on < '2026-01-01'
GROUP BY c.city ORDER BY revenue DESC
'''
DAY_QUERY = '''
SELECT o.order_id, o.ordered_on, c.name
FROM orders o JOIN customer c ON c.customer_id = o.customer_id
WHERE o.ordered_on = '2026-02-14'
'''


def get_plan(conn, sql):
    return [str(row[-1]) for row in conn.execute('EXPLAIN QUERY PLAN ' + sql)]


def timed(conn, sql, repeat=5):
    # Warm the query and file cache before measuring.
    conn.execute(sql).fetchall()
    samples = []
    for _ in range(repeat):
        t0 = perf_counter()
        conn.execute(sql).fetchall()
        samples.append((perf_counter() - t0) * 1000)
    return round(median(samples), 3)


def main():
    if not DB.is_file():
        raise SystemExit('warehouse.db not found; run setup.sql first')
    conn = sqlite3.connect(DB)
    try:
        print('SQLite version:', sqlite3.sqlite_version)
        for index in ('ix_orders_ordered_on', 'ix_orderline_order', 'ix_orderline_product'):
            conn.execute(f'DROP INDEX IF EXISTS {index}')
        steps = [
            ('No additional indexes', None),
            ('Add ordered_on index', 'CREATE INDEX ix_orders_ordered_on ON orders(ordered_on)'),
            ('Add order_line.order_id index', 'CREATE INDEX ix_orderline_order ON order_line(order_id)'),
            ('Add order_line.product_id index', 'CREATE INDEX ix_orderline_product ON order_line(product_id)'),
        ]
        reference_result = None
        for label, ddl in steps:
            if ddl:
                conn.execute(ddl)
            result = conn.execute(DASHBOARD).fetchall()
            if reference_result is None:
                reference_result = result
            else:
                assert result == reference_result, 'An index unexpectedly changed query results'
            elapsed = timed(conn, DASHBOARD)
            print(f'\n{label}: dashboard median of 5 runs = {elapsed:.3f} ms')
            for step in get_plan(conn, DASHBOARD):
                print('   ', step)
            if label == 'No additional indexes':
                print('   Single-day lookup before index median:', timed(conn, DAY_QUERY), 'ms')
                for step in get_plan(conn, DAY_QUERY):
                    print('     ', step)
            if label == 'Add ordered_on index':
                print('   Single-day lookup after index median:', timed(conn, DAY_QUERY), 'ms')
                for step in get_plan(conn, DAY_QUERY):
                    print('     ', step)
        print('\nNegative control: function on ordered_on often defeats the index')
        for step in get_plan(conn, "SELECT * FROM orders WHERE date(ordered_on) = '2026-02-14'"):
            print('   ', step)
        print('Positive control: product_id filter uses the product index')
        for step in get_plan(conn, 'SELECT order_id FROM order_line WHERE product_id = 20'):
            print('   ', step)
    finally:
        conn.close()


if __name__ == '__main__':
    main()
