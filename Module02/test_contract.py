"""Proof that the corrected SQLite DDL and two validations work."""
from datetime import date
from sqlalchemy import insert
from sqlalchemy.exc import IntegrityError
from pydantic import ValidationError
from contract import (
    Machine, Part, make_engine, metadata, machine_t,
    technician_t, maint_job_t, part_t, job_part_t,
)

def expect_integrity_error(connection, stmt, label):
    try:
        with connection.begin_nested():
            connection.execute(stmt)
    except IntegrityError:
        print('PASS', label)
    else:
        raise AssertionError('Constraint did not block: ' + label)

def main():
    engine=make_engine()
    metadata.create_all(engine)
    try:
        Machine(machine_id=1, machine_name='cnc-01', serial_no='BAD',
                site='G', installed=date(2019,3,11))
    except ValidationError:
        print('PASS Pydantic serial prefix')
    else:
        raise AssertionError('Pydantic missed bad serial')
    try:
        Machine(machine_id=1, machine_name='cnc-01', serial_no='SN-1',
                site='G', installed='not a date')
    except ValidationError:
        print('PASS Pydantic calendar date')
    else:
        raise AssertionError('Pydantic missed bad date')
    with engine.begin() as conn:
        conn.execute(insert(machine_t).values(machine_id=1, machine_name='cnc-01',
            serial_no='SN-1', site='G', installed=date(2019,3,11)))
        conn.execute(insert(technician_t).values(technician_id=1,name='Beier'))
        conn.execute(insert(part_t).values(part_no='P-1001', description='Bearing', unit_price=12.50))
        conn.execute(insert(maint_job_t).values(job_id=1, machine_id=1,technician_id=1,done_on=date(2026,1,8)))
        conn.execute(insert(job_part_t).values(job_id=1,part_no='P-1001'))
        expect_integrity_error(conn,insert(maint_job_t).values(job_id=2,machine_id=99,technician_id=1,done_on=date(2026,1,8)), 'FK orphan job')
        expect_integrity_error(conn,insert(part_t).values(part_no='P-1001',description='Dup',unit_price=1), 'duplicate part primary key')
        expect_integrity_error(conn,insert(job_part_t).values(job_id=1,part_no='P-1001'), 'duplicate job-part link')
        expect_integrity_error(conn,insert(part_t).values(part_no='X',description='Neg',unit_price=-1), 'negative price')
    print('All contract tests passed.')

if __name__ == '__main__': main()
