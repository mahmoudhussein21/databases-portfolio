# Round 7 — Curiosities and questions

These are independent study observations with source locations, not a record of a pod swap.

| Source in the Module 5 handout | Curiosity | Follow-up question |
|---|---|---|
| Round 3, generated data | `CROSS JOIN` creates 20,000 × 10 = 200,000 rows. | Why does the cross product multiply row counts? |
| Round 3, generated prices | `printf('%.2f', ...)` creates text, not a numeric type. | What mistakes can text prices cause when sorting? |
| Round 3, `SELECT DISTINCT` | The 3NF load assumes each job has one technician and each machine one site. | What if the real data violates those assumptions? |
| Round 4, query plans | An index scan may be slower than a full table scan. | When does scanning the index require extra table lookups? |
| Round 5, `dbstat` | Report-table storage includes repeated site and technician values. | How much bigger does the report become as more jobs are added? |
| Round 5, data refresh | Updating one machine site requires changing many report rows. | Is a scheduled rebuild safer than a complex set of triggers? |

**Questions to ask in a future discussion:** Which data should be updated immediately in a reporting copy? When is a performance gain large enough to justify duplicated data?
