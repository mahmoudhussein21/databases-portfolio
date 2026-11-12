# Task 1 — LLM-assisted SQL and query plan

## Prompt used

> SQLite schema: `customer(customer_id, name, city)`, `product(product_id, sku, price)`, `orders(order_id, customer_id, ordered_on, status)`, `order_line(order_id, product_id, qty)`. Write a query that returns, for each city, the number of distinct customers and the total revenue (sum of `qty*price`) of orders placed in 2025, ordered by revenue descending.

The query is saved in [`task1_dashboard.sql`](task1_dashboard.sql). It joins the four tables, applies a date range for 2025, groups by city, and uses `COUNT(DISTINCT c.customer_id)` so the same customer is not counted once per order line.

## Predicted and observed plan

I expected the large `order_line` table to be scanned, with rowid-based lookups into the other three tables. This prediction was confirmed by the baseline `EXPLAIN QUERY PLAN`. SQLite also uses temporary B-trees for `GROUP BY`, `COUNT(DISTINCT)`, and the final `ORDER BY`.

The full observed plan appears in [`task1_results.txt`](task1_results.txt).

## Verification

All four cities appeared. Each had 500 distinct customers with at least one 2025 order. The reported revenues were:

| City | Customers | Revenue |
|---|---:|---:|
| Bielefeld | 500 | 11,242,176.00 |
| Gütersloh | 500 | 8,422,344.00 |
| Münster | 500 | 5,493,504.00 |
| Paderborn | 500 | 2,815,656.00 |

I checked every result independently using a separate query that compared the year using `substr(ordered_on,1,4) = '2025'` and recomputed the distinct-customer count and revenue. The results matched.

## An important edge case

The `JOIN` operations are inner joins. A city with no qualifying 2025 orders would not appear in this report. That is reasonable for a report *of 2025 orders*, but if the requirement is to show **all** cities, including those with zero orders, a different outer-join design is needed. This is why a query can run correctly yet still need business-rule verification.
