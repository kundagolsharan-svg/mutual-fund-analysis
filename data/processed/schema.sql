-- Fund Dimension
CREATE TABLE dim_fund (
    fund_id INTEGER PRIMARY KEY,
    amfi_code INTEGER UNIQUE,
    fund_name TEXT,
    category TEXT,
    sub_category TEXT,
    fund_house TEXT
);

-- Date Dimension
CREATE TABLE dim_date (
    date_id INTEGER PRIMARY KEY,
    full_date DATE,
    year INTEGER,
    month INTEGER,
    day INTEGER
);

-- NAV Fact
CREATE TABLE fact_nav (
    nav_id INTEGER PRIMARY KEY,
    amfi_code INTEGER,
    date DATE,
    nav REAL
);

-- Transactions Fact
CREATE TABLE fact_transactions (
    transaction_id INTEGER PRIMARY KEY,
    amfi_code INTEGER,
    transaction_date DATE,
    transaction_type TEXT,
    amount REAL
);

-- Performance Fact
CREATE TABLE fact_performance (
    performance_id INTEGER PRIMARY KEY,
    amfi_code INTEGER,
    return_1yr REAL,
    return_3yr REAL,
    return_5yr REAL,
    expense_ratio REAL
);

-- AUM Fact
CREATE TABLE fact_aum (
    aum_id INTEGER PRIMARY KEY,
    amfi_code INTEGER,
    aum REAL
);