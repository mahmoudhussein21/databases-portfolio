-- OPTIONAL Task 5: same result in three shapes: aggregate, correlated subquery, window function.
-- One row per customer with at least one late order. All use the same ordering.
-- 1: Standard join and GROUP BY
SELECT c.customer_id, c.name, COUNT(*) AS late_orders
FROM orders o JOIN customer c ON c.customer_id = o.customer_id
WHERE o.status = 'late'
GROUP BY c.customer_id, c.name
ORDER BY late_orders DESC, c.customer_id;

-- 2: Correlated subquery, filtered to positive counts
SELECT c.customer_id, c.name,
       (SELECT COUNT(*) FROM orders o
        WHERE o.customer_id = c.customer_id AND o.status = 'late') AS late_orders
FROM customer c
WHERE EXISTS (SELECT 1 FROM orders o
              WHERE o.customer_id = c.customer_id AND o.status = 'late')
ORDER BY late_orders DESC, c.customer_id;

-- 3: Window, with a single row per customer via outer DISTINCT
SELECT DISTINCT customer_id, name, late_orders
FROM (
  SELECT c.customer_id, c.name,
         COUNT(*) OVER (PARTITION BY c.customer_id) AS late_orders
  FROM orders o JOIN customer c ON c.customer_id = o.customer_id
  WHERE o.status = 'late'
)
ORDER BY late_orders DESC, customer_id;
