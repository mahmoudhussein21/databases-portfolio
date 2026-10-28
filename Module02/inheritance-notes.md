# Task 4 (optional) — EER generalization/disjointness

Two executable alternatives appear in [`inheritance.sql`](inheritance.sql):

1. **Single-table inheritance:** one `machine_single` table with `machine_type` discriminator and subtype-specific fields; CHECK ensures CNC and injection molder fields are mutually exclusive and required for the selected type.
2. **Joined-table inheritance:** `machine_base`, `cnc_mill`, `injection_molder`, linked by PK/FK. Type-specific composite FKs and fixed discriminator values prohibit a CNC parent from being populated as an injection subtype (disjointness). **However, the parent can exist with no child**; total specialization needs additional application logic or triggers.

**Choice:** I would ship the **single-table design** while there are only two stable machine types because its constraints are simple, disjoint and complete in one row; choose joined tables later if types proliferate and differ substantially. (Assumption: every machine is exactly one of the two types.)

**Test evidence:** `inheritance.sql` was executed against SQLite in a separate database. See `inheritance-test.txt` for an invalid-subtype and incompatible parent test.
