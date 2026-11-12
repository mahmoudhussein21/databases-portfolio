# Task 2 — Index benchmark

## Method

The warehouse dataset was generated from `setup.sql`. I measured the same four-city report after adding one index at a time. `bench.py` warms the cache, times **five** executions per stage, and reports the median in milliseconds. The query results were checked for equality after every index. The plans and measurements were captured using Python's SQLite 3.46.1 on the test environment, **not on my Mac**. Results may differ on other machines and versions.

## Measurements

| Stage (indexes accumulated) | Median report time | Main plan change |
|---|---:|---|
| No additional indexes | 90.384 ms | `SCAN ol`, primary-key lookups in `orders`, `customer`, `product` |
| `ix_orders_ordered_on` | 96.543 ms | No change to the report plan |
| `ix_orderline_order` | 269.758 ms | Begins with indexed `orders` range search, then indexed `order_line` lookups |
| `ix_orderline_product` | 286.799 ms | No further change to the report plan |

**Conclusion:** The extra indexes did not make this aggregate-heavy report faster. The index on `order_line.order_id` changed the plan but slowed the report by adding many individual lookups. Timing differences between runs are possible; the plan is stronger evidence of the engine's access strategy.

## Where the date index helped

| Query | Before | After `ix_orders_ordered_on` |
|---|---:|---:|
| Single-day lookup for `2026-02-14` | 2.206 ms | 0.082 ms |

The single-day lookup switched from `SCAN o` to `SEARCH o USING INDEX ix_orders_ordered_on (ordered_on=?)`. It selects a small portion of the orders table, so the index helps.

## Negative results

- `ix_orderline_product` did not help the *city revenue report* because the join reached the `product` table by its `INTEGER PRIMARY KEY`. It **did** help a different query filtering `order_line.product_id`.
- `WHERE date(ordered_on) = '2026-02-14'` caused a `SCAN orders` even though an index on `ordered_on` existed. Wrapping the column in a function prevented use of this ordinary index.
- An index is not automatically good or bad: **it depends on the query**.

See [`benchmark_results.txt`](benchmark_results.txt) for full plans, median measurements and both controls. Run `python3 Module03/bench.py` on the target machine to reproduce the measurements there.
