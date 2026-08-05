-- 1. Total NAV records
SELECT COUNT(*) FROM fact_nav;

-- 2. Highest NAV
SELECT * FROM fact_nav
ORDER BY nav DESC
LIMIT 5;

-- 3. Lowest NAV
SELECT * FROM fact_nav
ORDER BY nav ASC
LIMIT 5;

-- 4. Average NAV
SELECT AVG(nav) FROM fact_nav;

-- 5. Latest NAV
SELECT * FROM fact_nav
ORDER BY date DESC
LIMIT 10;

-- 6. NAV by AMFI Code
SELECT amfi_code, AVG(nav)
FROM fact_nav
GROUP BY amfi_code;

-- 7. Maximum NAV per Fund
SELECT amfi_code, MAX(nav)
FROM fact_nav
GROUP BY amfi_code;

-- 8. Minimum NAV per Fund
SELECT amfi_code, MIN(nav)
FROM fact_nav
GROUP BY amfi_code;

-- 9. Number of NAV records per Fund
SELECT amfi_code, COUNT(*)
FROM fact_nav
GROUP BY amfi_code;

-- 10. Top 5 Funds by Average NAV
SELECT amfi_code, AVG(nav) AS avg_nav
FROM fact_nav
GROUP BY amfi_code
ORDER BY avg_nav DESC
LIMIT 5;