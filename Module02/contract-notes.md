# Task 3 — Why these constraints live where they do

**Application (Pydantic):** validates the `SN-` serial prefix, actual calendar dates, IDs `>= 1`, nonblank strings and nonnegative two-decimal monetary values. `part_nos: list[str]` is an API representation, **not** a database CSV cell. The persistence layer must insert one `job_part` record per distinct part code.

**Database (SQLAlchemy/SQLite):** PKs and UNIQUE block duplicate rows; foreign keys prevent orphan jobs or links; NOT NULL protects required fields; a CHECK prevents negative prices; the composite PK of `job_part` enforces each part at most once per job. `PRAGMA foreign_keys=ON` is set for every SQLite connection by `make_engine`.

**Why both?** Pydantic gives early, descriptive errors at the application boundary; database constraints protect integrity even when different applications write the same tables.

**SQLite caveat:** SQLite's `Date` and `Numeric(9,2)` use storage/affinity conventions, **not strict native DATE or exact-decimal enforcement**. Validate through Pydantic and use an appropriate production database or add extra SQLite checks/triggers for writes that bypass the app. This is a structural contract, not a completed migration of the flawed rows: manual remediation is required for `cnc-05`, the bad date and duplicate `P-1003`.

**Extension versus the handout's starter code:** The supplied example leaves `technician` as a string; this version introduces `Technician` and its FK to match Task 1's requested intended ER model.
