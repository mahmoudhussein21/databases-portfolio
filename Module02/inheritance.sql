-- Task 4: Two separate ALTERNATIVES (safe to execute together because names differ).
PRAGMA foreign_keys=ON;

-- A. Single-table inheritance; subtype rules and disjointness enforced via CHECKs.
CREATE TABLE machine_single (
 machine_id INTEGER PRIMARY KEY,
 machine_type TEXT NOT NULL CHECK (machine_type IN ('CNC','INJECTION')),
 serial_no TEXT NOT NULL UNIQUE,
 cnc_axes INTEGER,
 clamp_force_kn NUMERIC,
 CHECK (
   (machine_type='CNC' AND cnc_axes IS NOT NULL AND cnc_axes > 0 AND clamp_force_kn IS NULL)
   OR
   (machine_type='INJECTION' AND clamp_force_kn IS NOT NULL AND clamp_force_kn > 0 AND cnc_axes IS NULL)
 )
);

-- B. Joined-table inheritance (base + subtype tables).
CREATE TABLE machine_base (
 machine_id INTEGER PRIMARY KEY,
 machine_type TEXT NOT NULL CHECK(machine_type IN ('CNC','INJECTION')),
 serial_no TEXT NOT NULL UNIQUE,
 UNIQUE(machine_id,machine_type)
);
CREATE TABLE cnc_mill (
 machine_id INTEGER PRIMARY KEY,
 machine_type TEXT NOT NULL DEFAULT 'CNC' CHECK(machine_type='CNC'),
 cnc_axes INTEGER NOT NULL CHECK(cnc_axes > 0),
 FOREIGN KEY(machine_id,machine_type)
   REFERENCES machine_base(machine_id,machine_type)
);
CREATE TABLE injection_molder (
 machine_id INTEGER PRIMARY KEY,
 machine_type TEXT NOT NULL DEFAULT 'INJECTION' CHECK(machine_type='INJECTION'),
 clamp_force_kn NUMERIC NOT NULL CHECK(clamp_force_kn > 0),
 FOREIGN KEY(machine_id,machine_type)
   REFERENCES machine_base(machine_id,machine_type)
);

-- Proof examples:
INSERT INTO machine_single VALUES (1,'CNC','SN-100',3,NULL);
INSERT INTO machine_single VALUES (2,'INJECTION','SN-101',NULL,1400);
INSERT INTO machine_base VALUES (1,'CNC','SN-200');
INSERT INTO cnc_mill(machine_id,cnc_axes) VALUES (1,3);
INSERT INTO machine_base VALUES (2,'INJECTION','SN-201');
INSERT INTO injection_molder(machine_id,clamp_force_kn) VALUES (2,1400);
