-- Run in a scratch database, NOT normalize.db:
-- sqlite3 :memory: < Module05/anomalies.sql
CREATE TABLE flat5(job_id INTEGER, machine_id TEXT, site TEXT,
                   technician TEXT, part_no TEXT, part_price REAL);
INSERT INTO flat5 VALUES
(1,'cnc-01','Gütersloh','tech-0','P-0001',6.00),
(1,'cnc-01','Gütersloh','tech-0','P-0002',7.00),
(2,'cnc-02','Gütersloh','tech-1','P-0001',6.00),
(2,'cnc-02','Gütersloh','tech-1','P-0003',8.50),
(3,'cnc-01','Gütersloh','tech-0','P-0003',8.50);

-- Update anomaly: changes one copy of a site, leaving others inconsistent.
UPDATE flat5 SET site='Bielefeld' WHERE job_id=1 AND part_no='P-0001';
SELECT 'UPDATE ANOMALY', job_id, part_no, site FROM flat5
WHERE machine_id='cnc-01' ORDER BY job_id, part_no;

-- Insert anomaly: a part without a job requires a fake/incomplete job-part row.
INSERT INTO flat5(job_id,machine_id,site,technician,part_no,part_price)
VALUES(NULL,NULL,NULL,NULL,'P-0099',99.00);
SELECT 'INSERT ANOMALY', job_id, part_no, part_price FROM flat5 WHERE part_no='P-0099';

-- Delete anomaly: removing the only use of P-0002 removes its price information.
DELETE FROM flat5 WHERE job_id=1 AND part_no='P-0002';
SELECT 'DELETE ANOMALY', COUNT(*) FROM flat5 WHERE part_no='P-0002';
