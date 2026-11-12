# Task 4 — One SQL query as relational algebra

SQL query (same as the plan-safari example):

```sql
SELECT job_id, machine_name
FROM maint_job
WHERE technician = 'Beier';
```

Relational algebra:

\[\pi_{job\_id,\ machine\_name}(\sigma_{technician='Beier'}(maint\_job))\]

`σ` selects only rows whose technician is Beier; `π` keeps the two requested columns. This is a projection of a selection. The SQL and relational algebra use the same filter and output columns.

A more complex example using grouping: the dashboard query first joins `customer`, `orders`, `order_line`, and `product`, filters the order date to 2025, then groups by city, counts distinct customer IDs, and sums `qty × price`. Standard textbook relational algebra requires extended grouping/aggregate operator `γ` and a distinct-count aggregate to express that report.
