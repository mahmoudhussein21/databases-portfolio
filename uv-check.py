import sys
import sqlite3
import duckdb
import datasette
import sqlite_utils
import pydantic
import sqlalchemy

print("Python version:", sys.version.split()[0])
print("SQLite version:", sqlite3.sqlite_version)
print("DuckDB version:", duckdb.__version__)
print("SUCCESS: Database tools are installed!")
