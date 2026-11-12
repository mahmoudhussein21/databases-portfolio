"""Rebuild Module 5 data and capture real timings, query plans, and storage.

Run: python3 Module05/benchmark.py
Measurements depend on the current machine, SQLite build, and cache state.
"""
from pathlib import Path
from statistics import median
from time import perf_counter
import math
import platform
import sqlite3

BASE = Path(__file__).resolve().parent
DB = BASE / 'normalize.db'

NORMALIZED = """
SELECT m.machine_id, m.site, j.technician, SUM(p.part_price) AS cost
FROM job AS j
JOIN machine AS m ON m.machine_id = j.machine_id
JOIN job_part AS jp ON jp.job_id = j.job_id
JOIN part AS p ON p.part_no = jp.part_no
WHERE j.done_on >= date('2026-03-01')
GROUP BY m.machine_id, j.technician
"""

REPORT = """
SELECT machine_id, site, technician, SUM(part_price) AS cost
FROM report_jobpart
WHERE done_on >= date('2026-03-01')
GROUP BY machine_id, technician
"""


def plan(con, sql):
    return [str(row[3]) for row in con.execute('EXPLAIN QUERY PLAN ' + sql)]


def timed(con, sql):
    begin = perf_counter()
    rows = con.execute(sql).fetchall()
    return (perf_counter() - begin) * 1000, rows


def pair(con, query_a, query_b, repeats=5):
    timed(con, query_a)
    timed(con, query_b)  # warm up both sides, discard cold timings
    a_times, b_times = [], []
    for n in range(repeats):
        sequence = ((query_a, a_times), (query_b, b_times)) if n % 2 == 0 else ((query_b, b_times), (query_a, a_times))
        for query, times in sequence:
            ms, _ = timed(con, query)
            times.append(ms)
    return a_times, b_times


def storage(con, objects):
    try:
        marks = ','.join('?' for _ in objects)
        q = f'SELECT COALESCE(SUM(pgsize),0) FROM dbstat WHERE name IN ({marks})'
        return con.execute(q, objects).fetchone()[0]
    except sqlite3.DatabaseError:
        return None


def fmt_storage(n):
    return 'not available (dbstat disabled)' if n is None else f'{n:,} bytes ({n/1024:,.1f} KiB)'


def fmt_ms(numbers):
    return ', '.join(f'{t:.3f}' for t in numbers)


def quote_plan(lines):
    return '\n'.join('  ' + line for line in lines)


def main():
    if DB.exists():
        DB.unlink()
    con = sqlite3.connect(DB)
    con.execute('PRAGMA foreign_keys = ON')
    con.executescript((BASE / 'setup.sql').read_text(encoding='utf-8'))
    con.commit()

    table_names = ('flat_jobpart', 'machine', 'part', 'job', 'job_part', 'report_jobpart')
    counts = {name: con.execute('SELECT COUNT(*) FROM ' + name).fetchone()[0] for name in table_names}
    expected = dict(flat_jobpart=200000, machine=50, part=10, job=20000, job_part=200000, report_jobpart=200000)
    assert counts == expected, (counts, expected)
    assert con.execute('PRAGMA foreign_key_check').fetchall() == []
    assert con.execute('PRAGMA integrity_check').fetchone()[0] == 'ok'

    a_rows = sorted(con.execute(NORMALIZED).fetchall())
    b_rows = sorted(con.execute(REPORT).fetchall())
    assert len(a_rows) == len(b_rows) and len(a_rows) > 0
    for a, b in zip(a_rows, b_rows):
        assert a[:3] == b[:3]
        assert math.isclose(a[3], b[3], rel_tol=1e-10, abs_tol=1e-6), (a,b)

    normalized_times, indexed_report_times = pair(con, NORMALIZED, REPORT)
    n_med, r_med = median(normalized_times), median(indexed_report_times)
    normalized_plan = plan(con, NORMALIZED)
    indexed_report_plan = plan(con, REPORT)
    group_count = len(a_rows)
    total_cost = sum(row[3] for row in a_rows)

    # Row-change counts and times, each update rolled back afterward.
    updates = {}
    for table in ('machine', 'report_jobpart'):
        con.execute('SAVEPOINT measure_update')
        begin = perf_counter()
        cur = con.execute(f"UPDATE {table} SET site='Bielefeld' WHERE machine_id='cnc-02'")
        elapsed = (perf_counter() - begin) * 1000
        updates[table] = (cur.rowcount, elapsed)
        con.execute('ROLLBACK TO SAVEPOINT measure_update')
        con.execute('RELEASE SAVEPOINT measure_update')
    assert updates['machine'][0] == 1
    assert updates['report_jobpart'][0] == 4000

    normalized_table_bytes = storage(con, ('machine','part','job','job_part'))
    report_table_bytes = storage(con, ('report_jobpart',))
    normalized_index_bytes = storage(con, ('sqlite_autoindex_machine_1', 'sqlite_autoindex_part_1', 'sqlite_autoindex_job_part_1'))
    report_index_bytes = storage(con, ('ix_report_machine',))

    # Deliberate negative index experiment. Remove and restore the report index.
    con.execute('DROP INDEX IF EXISTS ix_report_machine')
    con.commit()
    assert not any(row[1] == 'ix_report_machine' for row in con.execute('PRAGMA index_list(report_jobpart)'))
    # Distinct SQL text avoids a cached EXPLAIN statement from before DROP INDEX.
    no_index_plan = [str(row[3]) for row in con.execute('EXPLAIN QUERY PLAN /* after DROP INDEX */ ' + REPORT)]
    assert not any('ix_report_machine' in line for line in no_index_plan), no_index_plan
    timed(con, REPORT)
    no_index_times = [timed(con, REPORT)[0] for _ in range(5)]
    no_index_med = median(no_index_times)
    con.execute('CREATE INDEX ix_report_machine ON report_jobpart(machine_id)')
    con.commit()
    assert 'ix_report_machine' in '\n'.join(r[1] for r in con.execute('PRAGMA index_list(report_jobpart)'))

    plan_text = (
        'SQLite version: ' + sqlite3.sqlite_version + '\n\n'
        'A. Normalized four-way join\n' + quote_plan(normalized_plan) + '\n\n'
        'B. Report table WITH ix_report_machine\n' + quote_plan(indexed_report_plan) + '\n\n'
        'B. Report table WITHOUT ix_report_machine\n' + quote_plan(no_index_plan) + '\n'
    )
    (BASE/'query_plans.txt').write_text(plan_text, encoding='utf-8')

    results = (
        'Module 5 reproducible benchmark — results from this run\n'
        'System: ' + platform.system() + ' / SQLite ' + sqlite3.sqlite_version + '\n'
        'All timings are wall-clock measurements from this run.\n'
        'Hardware and caching affect timings; rerun python3 Module05/benchmark.py to compare.\n\n'
        'Dataset counts: ' + ', '.join(f'{k}={v}' for k,v in counts.items()) + '\n'
        f'Both designs returned identical {group_count} groups; total reported cost: {total_cost:,.2f}.\n'
        'Foreign-key check: passed; integrity check: ok.\n\n'
        'A (normalized), five warm times (ms): ' + fmt_ms(normalized_times) + '\n'
        f'A median (ms): {n_med:.3f}\n'
        'B (report WITH index), five warm times (ms): ' + fmt_ms(indexed_report_times) + '\n'
        f'B median (ms): {r_med:.3f}\n'
        'B (report WITHOUT index), five warm times (ms): ' + fmt_ms(no_index_times) + '\n'
        f'B without-index median (ms): {no_index_med:.3f}\n\n'
        f'3NF site update: {updates["machine"][0]} row(s), {updates["machine"][1]:.3f} ms; rolled back.\n'
        f'Report site update: {updates["report_jobpart"][0]} row(s), {updates["report_jobpart"][1]:.3f} ms; rolled back.\n\n'
        '3NF table storage: ' + fmt_storage(normalized_table_bytes) + '\n'
        'Report table storage: ' + fmt_storage(report_table_bytes) + '\n'
        '3NF autoindex storage (separate, not included above): ' + fmt_storage(normalized_index_bytes) + '\n'
        'Report index storage (separate): ' + fmt_storage(report_index_bytes) + '\n'
    )
    (BASE/'benchmark_results.txt').write_text(results,encoding='utf-8')

    speed_label = ('report table' if r_med<n_med else 'normalized join')
    indexed_effect = ('slower' if r_med>no_index_med else 'faster')
    f_storage = lambda x: 'N/A' if x is None else f'{x/1024:.1f}'
    ratio = r_med/n_med
    comparison = f'index-free report median {no_index_med:.3f} ms vs indexed {r_med:.3f} ms'
    (BASE/'benchmark.md').write_text(f'''# Rounds 4–5 — Benchmark and storage results

The results below were measured with SQLite {sqlite3.sqlite_version} on {platform.system()}. Repeating `python3 Module05/benchmark.py` regenerates them. Hardware and caching affect the numbers.

## Verified data counts

| Table | Rows |
|---|---:|
| Flat job-part | {counts['flat_jobpart']:,} |
| Machine | {counts['machine']:,} |
| Part | {counts['part']:,} |
| Job | {counts['job']:,} |
| Job-part link | {counts['job_part']:,} |
| Denormalized report | {counts['report_jobpart']:,} |

Both queries returned **{group_count:,} matching groups** and the total part cost was **{total_cost:,.2f}**. Foreign-key and SQLite integrity checks passed. The query uses the module's fixed `done_on >= '2026-03-01'` cutoff, not a moving 90-day window.

## Before/after read and write comparison

| Design | Report median (ms; 5 warm runs) | Rows affected by site change | Table data storage (KiB, excludes indexes) | Repeated data? |
|---|---:|---:|---:|---|
| 3NF (`machine`, `part`, `job`, `job_part`) | {n_med:.3f} | {updates['machine'][0]:,} | {f_storage(normalized_table_bytes)} | No repeated site and price |
| Denormalized `report_jobpart` (with index) | {r_med:.3f} | {updates['report_jobpart'][0]:,} | {f_storage(report_table_bytes)} | Site, technician and price repeated |

The row-change comparison is the more stable result: updating one site changes **one 3NF machine row** versus **4,000 report rows**. The measured update statements were rolled back so the example data remains unchanged.

## Index experiment

- Report WITH `ix_report_machine`: median **{r_med:.3f} ms**.
- Report WITHOUT `ix_report_machine`: median **{no_index_med:.3f} ms**.
- In this run, having that index made the report query **{indexed_effect}** than without it ({comparison}). This result is workload-dependent.
- See `query_plans.txt` for actual `EXPLAIN QUERY PLAN` output. An index scan can repeatedly fetch table rows, whereas a full table scan can be more sequential.
- The read benchmark favored the **{speed_label}** at this scale. Do not assume one design always wins.

The raw five-run timings are preserved in [`benchmark_results.txt`](benchmark_results.txt).
''',encoding='utf-8')

    recommendation = (
        '# Round 6 — Recommendation to the operations lead\n\n'
        'I recommend keeping `machine`, `part`, `job`, and `job_part` in 3NF as the trusted transactional data. '
        'The two dashboard queries produced identical results (' + str(group_count) + ' groups), so the comparison is fair. '
        'In this test the normalized query took a median ' + f'{n_med:.3f}' + ' ms, while the indexed report took ' + f'{r_med:.3f}' + ' ms. '
        'A site change affects just one machine row in 3NF, but 4,000 copied rows in the report table. '
        'Therefore, I would not replace the normalized database with the report table; the duplicate facts create a risk of stale or inconsistent data. '
        'If a real dashboard needs faster repeated reads, I would maintain a separate report table and measure it on production-sized data. '
        'A scheduled rebuild after ingest batches is a simple way to refresh the report, with the refresh delay documented; triggers are possible if immediate updates are necessary but add write overhead. '
        'I would repeat the plan, timing, and storage tests after adding a refresh mechanism, because its cost is part of the decision.\n\n'
        'Evidence: [`benchmark.md`](benchmark.md), [`benchmark_results.txt`](benchmark_results.txt), and [`query_plans.txt`](query_plans.txt).\n'
    )
    (BASE/'recommendation-memo.md').write_text(recommendation,encoding='utf-8')

    (BASE/'round5-storage.md').write_text(f'''# Round 5 — Price of copying data

| Measurement | Normalized design | Denormalized report |
|---|---:|---:|
| Rows changed when `cnc-02` moves | {updates['machine'][0]:,} | {updates['report_jobpart'][0]:,} |
| Data table bytes (`dbstat`; indexes excluded) | {fmt_storage(normalized_table_bytes)} | {fmt_storage(report_table_bytes)} |
| Extra index bytes | {fmt_storage(normalized_index_bytes)} | {fmt_storage(report_index_bytes)} |

On this generated dataset, 400 jobs use `cnc-02`, and each job has ten part links, giving **4,000 report rows** for that machine. One machine row represents the same site fact in 3NF.

**The trade-off:** a reporting copy may make frequent reads simpler, but every update to shared facts must refresh many copies. The report is not the authoritative record. Table bytes in the first comparison exclude indexes; index storage is shown separately rather than hidden.

The query-plan comparison with and without `ix_report_machine` is in `query_plans.txt`. The index was restored after the experiment.
''',encoding='utf-8')

    print(f'Module 5 check passed: {counts["flat_jobpart"]:,} flat rows, {counts["job_part"]:,} links, {group_count} matching report groups.')
    print(f'Normalized median: {n_med:.3f} ms; report median with index: {r_med:.3f} ms; without index: {no_index_med:.3f} ms.')
    print(f'Rows changed on site update: 3NF={updates["machine"][0]}, report={updates["report_jobpart"][0]} (updates rolled back).')
    con.close()

if __name__ == '__main__':
    main()
