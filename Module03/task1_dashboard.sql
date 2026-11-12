-- Prompt: SQLite schema customer, product, orders, order_line.
-- Return for each city distinct customers and 2025 order revenue (qty * price), highest revenue first.
-- This is the LLM-assisted query, checked against the locally generated dataset.
SELECT c.city, COUNT(DISTINCT c.customer_id) AS customers,
       ROUND(SUM(ol.qty * p.price), 2) AS revenue
FROM customer AS c
JOIN orders AS o ON o.customer_id = c.customer_id
JOIN order_line AS ol ON ol.order_id = o.order_id
JOIN product AS p ON p.product_id = ol.product_id
WHERE o.ordered_on >= '2025-01-01' AND o.ordered_on < '2026-01-01'
GROUP BY c.city
ORDER BY revenue DESC;
