# Task 4 — Access control without a database server

A SQLite database has no built-in account system equivalent to PostgreSQL roles and `GRANT`. For an edge gateway, the operating system can restrict file access, and the application can open the database in read-only mode using `mode=ro`. A `machine_health` view gives a clear summary, but it does not stop a user who can open the database file from reading the underlying tables.

In the test, the file permission bits were changed to `444`, a read-only connection successfully read five rows, and an attempted `DELETE` was rejected with `attempt to write a readonly database`. The original file permissions were restored. `PRAGMA query_only = ON` also rejected `DELETE` on an otherwise writable connection; see [task4_results.txt](task4_results.txt).

PostgreSQL is different because its server can authenticate multiple users and grant or deny privileges on tables and views. File-based control can be reasonable on a trusted local machine where the application and operating system control access, but it is not enough for a multi-tenant website whose users need different database permissions. In particular, a file owner can change file permissions again, and a reporting view is not an access-control mechanism by itself.
