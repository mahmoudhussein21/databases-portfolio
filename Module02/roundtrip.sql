-- Task 5 diagram -> schema, executed in a separate in-memory SQLite database.
PRAGMA foreign_keys=ON;
CREATE TABLE machine (
 machine_id INTEGER PRIMARY KEY,
 machine_name TEXT NOT NULL UNIQUE,
 serial_no TEXT NOT NULL UNIQUE,
 site TEXT NOT NULL,
 installed TEXT NOT NULL
);
CREATE TABLE technician (
 technician_id INTEGER PRIMARY KEY,
 name TEXT NOT NULL
);
CREATE TABLE part (
 part_no TEXT PRIMARY KEY,
 description TEXT NOT NULL,
 unit_price NUMERIC NOT NULL CHECK(unit_price >= 0)
);
CREATE TABLE maint_job (
 job_id INTEGER PRIMARY KEY,
 machine_id INTEGER NOT NULL REFERENCES machine(machine_id),
 technician_id INTEGER NOT NULL REFERENCES technician(technician_id),
 done_on TEXT NOT NULL
);
CREATE TABLE job_part (
 job_id INTEGER NOT NULL REFERENCES maint_job(job_id),
 part_no TEXT NOT NULL REFERENCES part(part_no),
 PRIMARY KEY(job_id, part_no)
);
