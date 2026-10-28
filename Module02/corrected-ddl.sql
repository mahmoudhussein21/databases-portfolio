-- SQLAlchemy-generated SQLite CREATE TABLE output.
-- Run contract.py to reproduce.
CREATE TABLE machine (
	machine_id INTEGER NOT NULL, 
	machine_name VARCHAR NOT NULL, 
	serial_no VARCHAR NOT NULL, 
	site VARCHAR NOT NULL, 
	installed DATE NOT NULL, 
	PRIMARY KEY (machine_id), 
	CONSTRAINT uq_machine_serial UNIQUE (serial_no), 
	UNIQUE (machine_name)
);

CREATE TABLE technician (
	technician_id INTEGER NOT NULL, 
	name VARCHAR NOT NULL, 
	PRIMARY KEY (technician_id)
);

CREATE TABLE part (
	part_no VARCHAR NOT NULL, 
	description VARCHAR NOT NULL, 
	unit_price NUMERIC(9, 2) NOT NULL, 
	PRIMARY KEY (part_no), 
	CONSTRAINT ck_part_nonnegative_price CHECK (unit_price >= 0)
);

CREATE TABLE maint_job (
	job_id INTEGER NOT NULL, 
	machine_id INTEGER NOT NULL, 
	technician_id INTEGER NOT NULL, 
	done_on DATE NOT NULL, 
	PRIMARY KEY (job_id), 
	FOREIGN KEY(machine_id) REFERENCES machine (machine_id), 
	FOREIGN KEY(technician_id) REFERENCES technician (technician_id)
);

CREATE TABLE job_part (
	job_id INTEGER NOT NULL, 
	part_no VARCHAR NOT NULL, 
	PRIMARY KEY (job_id, part_no), 
	FOREIGN KEY(job_id) REFERENCES maint_job (job_id), 
	FOREIGN KEY(part_no) REFERENCES part (part_no)
);

