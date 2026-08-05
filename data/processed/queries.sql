-- 1. Total number of funds
SELECT COUNT(*) AS total_funds
FROM fund_master;

-- 2. Average NAV
SELECT AVG(nav)
FROM nav_history;

-- 3. Highest NAV
SELECT *
FROM nav_history
ORDER BY nav DESC
LIMIT 5;

-- 4. Lowest NAV
SELECT *
FROM nav_history
ORDER BY nav ASC
LIMIT 5;

-- 5. Latest NAV
SELECT *
FROM nav_history
ORDER BY date DESC
LIMIT 10;

-- 6. Total NAV records
SELECT COUNT(*)
FROM nav_history;

-- 7. Average expense ratio
SELECT AVG(expense_ratio)
FROM scheme_performance;

-- 8. Expense ratio below 1%
SELECT *
FROM scheme_performance
WHERE expense_ratio < 1;

-- 9. Highest 1 Year Return
SELECT *
FROM scheme_performance
ORDER BY return_1yr DESC
LIMIT 10;

-- 10. Count schemes by category
SELECT category,
COUNT(*)
FROM fund_master
GROUP BY category;