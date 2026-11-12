"""Optional experiments: JSON join, Parquet row-group stats, zstd compression."""
import json
from pathlib import Path
import duckdb

HERE = Path(__file__).resolve().parent
PARQUET = HERE / "report_history.parquet"
SORTED = HERE / "sorted.parquet"
ZSTD = HERE / "report_zstd.parquet"
DEVICES = HERE / "devices.json"


def q(path):
    return "'" + str(path).replace("'", "''") + "'"


def main():
    con = duckdb.connect()
    DEVICES.write_text(json.dumps([
        {"machine_id": "cnc-01", "vendor": "Siemens", "firmware": "4.2"},
        {"machine_id": "cnc-02", "vendor": "Fanuc", "firmware": "3.9"},
        {"machine_id": "cnc-03", "vendor": "Siemens", "firmware": "4.0"},
    ], indent=2) + "\n", encoding="utf-8")
    res = con.execute(f"""SELECT d.vendor, r.machine_id,
                             ROUND(SUM(r.part_price),2) AS cost
              FROM read_json_auto({q(DEVICES)}) d
              JOIN read_parquet({q(PARQUET)}) r USING(machine_id)
              GROUP BY d.vendor, r.machine_id ORDER BY cost DESC""").fetchall()
    print("S1: JSON and Parquet join:", res)
    try:
        base_stats = con.execute(f"""SELECT row_group_id, stats_min, stats_max
            FROM parquet_metadata({q(PARQUET)}) WHERE path_in_schema='done_on'
            ORDER BY row_group_id LIMIT 5""").fetchall()
        con.execute(f"""COPY (SELECT * FROM read_parquet({q(PARQUET)}) ORDER BY done_on)
            TO {q(SORTED)} (FORMAT PARQUET)""")
        sorted_stats = con.execute(f"""SELECT row_group_id, stats_min, stats_max
            FROM parquet_metadata({q(SORTED)}) WHERE path_in_schema='done_on'
            ORDER BY row_group_id LIMIT 5""").fetchall()
        print("S2: unsorted row-group date ranges:", base_stats)
        print("S2: sorted row-group date ranges:", sorted_stats)
    except duckdb.Error as exc:
        print("S2: parquet_metadata query unsupported by installed DuckDB:", exc)
    con.execute(f"""COPY (SELECT * FROM read_parquet({q(PARQUET)}))
                       TO {q(ZSTD)} (FORMAT PARQUET, COMPRESSION ZSTD)""")
    count1, total1 = con.execute(f"""SELECT COUNT(*), ROUND(SUM(part_price),2)
                                FROM read_parquet({q(PARQUET)})""").fetchone()
    count2, total2 = con.execute(f"""SELECT COUNT(*), ROUND(SUM(part_price),2)
                                FROM read_parquet({q(ZSTD)})""").fetchone()
    if (count1, total1) != (count2, total2):
        raise AssertionError("ZSTD copy differs in row count or sum")
    print(f"S3: snappy MiB={PARQUET.stat().st_size / (1024**2):.3f}; "
          f"zstd MiB={ZSTD.stat().st_size / (1024**2):.3f}")
    print("S3: same row count and rounded total price.")
    con.close()


if __name__ == "__main__":
    main()
