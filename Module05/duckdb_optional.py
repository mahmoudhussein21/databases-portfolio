"""Optional Module 6a bridge: compare a DuckDB aggregate, if duckdb is installed.

Does not make a timing claim when DuckDB is unavailable.
Run after setup: python3 Module05/duckdb_optional.py
"""
from pathlib import Path
from time import perf_counter
import sqlite3

BASE=Path(__file__).resolve().parent
try:
    import duckdb
except ImportError:
    print('DuckDB is not installed: optional comparison not run.')
    raise SystemExit(0)

src=sqlite3.connect(BASE/'normalize.db')
rows=src.execute('SELECT machine_id, site, technician, part_price, done_on FROM report_jobpart').fetchall()
src.close()
con=duckdb.connect(':memory:')
con.execute('CREATE TABLE report_jobpart(machine_id VARCHAR, site VARCHAR, technician VARCHAR, part_price DOUBLE, done_on DATE)')
con.executemany('INSERT INTO report_jobpart VALUES(?,?,?,?,?)',rows)
query="""SELECT machine_id, site, technician, SUM(part_price) AS cost
 FROM report_jobpart WHERE done_on >= DATE '2026-03-01'
 GROUP BY machine_id, site, technician"""
con.execute(query).fetchall() # warm
start=perf_counter(); results=con.execute(query).fetchall();elapsed=(perf_counter()-start)*1000
print('DuckDB groups:',len(results),'warm query time (one run):',round(elapsed,3),'ms')
print('Compare to the SQLite benchmark only as an exploratory result; this load is in-memory and not a controlled engine comparison.')
