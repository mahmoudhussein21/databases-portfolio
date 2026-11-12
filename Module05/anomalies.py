"""Run the three flat-table anomalies and capture actual SQLite results."""
from pathlib import Path
import sqlite3

BASE = Path(__file__).resolve().parent


def main():
    con = sqlite3.connect(':memory:')
    con.executescript((BASE / 'anomalies.sql').read_text(encoding='utf-8').split('-- Update anomaly')[0])
    lines = ['Anomalies on the five-row sample (SQLite in-memory database)', '']
    cur = con.execute("UPDATE flat5 SET site='Bielefeld' WHERE job_id=1 AND part_no='P-0001'")
    assert cur.rowcount == 1
    rows = con.execute("SELECT job_id, part_no, site FROM flat5 WHERE machine_id='cnc-01' ORDER BY job_id, part_no").fetchall()
    assert len({r[2] for r in rows}) == 2
    lines += ['UPDATE anomaly: changed one row; the same machine now has conflicting sites.', f'Rows changed: {cur.rowcount}', *map(str,rows), '']
    con.execute("INSERT INTO flat5(job_id,machine_id,site,technician,part_no,part_price) VALUES (NULL,NULL,NULL,NULL,'P-0099',99.0)")
    incomplete = con.execute("SELECT job_id, part_no, part_price FROM flat5 WHERE part_no='P-0099'").fetchone()
    assert incomplete[0] is None
    lines += ['INSERT anomaly: a new unused part fits only as a row without a job.', f'Incomplete row: {incomplete}', '']
    deleted = con.execute("DELETE FROM flat5 WHERE job_id=1 AND part_no='P-0002'")
    left = con.execute("SELECT count(*) FROM flat5 WHERE part_no='P-0002'").fetchone()[0]
    assert deleted.rowcount == 1 and left == 0
    lines += ['DELETE anomaly: deleting the last job-part row erased the part-price fact.', f'Rows deleted: {deleted.rowcount}; remaining P-0002 rows: {left}', '', 'All three anomaly examples reproduced.']
    out='\n'.join(lines)+'\n'
    (BASE/'anomaly_results.txt').write_text(out,encoding='utf-8')
    print(out)
    con.close()

if __name__=='__main__': main()
