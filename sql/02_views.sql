-- ====================================================================================================
-- PROJECT: Wealth Management & Banking Transaction Intelligence System
-- MODULE: 02_views.sql
-- DESCRIPTION: Analytical & Reporting Views for Business Intelligence & Power BI Integration
-- ====================================================================================================

USE wealth_management_db;

-- ----------------------------------------------------------------------------------------------------
-- VIEW 1: Customer 360 & Wealth Portfolio Aggregation
-- Provides a holistic client profile combining balances, tier, activity velocity, and advisor info.
-- ----------------------------------------------------------------------------------------------------
DROP VIEW IF EXISTS v_client_360_summary;

CREATE VIEW v_client_360_summary AS
SELECT 
    c.customer_id,
    c.customer_code,
    CONCAT(c.first_name, ' ', c.last_name) AS full_name,
    c.wealth_tier,
    c.risk_profile,
    c.annual_income,
    c.kyc_status,
    c.status AS customer_status,
    c.onboarding_date,
    b.branch_name,
    b.city AS branch_city,
    CONCAT(adv.first_name, ' ', adv.last_name) AS assigned_advisor,
    adv.title AS advisor_title,
    COUNT(DISTINCT a.account_id) AS total_accounts,
    COALESCE(SUM(a.current_balance), 0.00) AS total_aum,
    COALESCE(COUNT(t.transaction_id), 0) AS total_lifetime_transactions,
    COALESCE(SUM(t.amount), 0.00) AS total_transaction_volume,
    MAX(t.transaction_time) AS latest_transaction_time,
    DATEDIFF(CURRENT_DATE(), MAX(t.transaction_time)) AS days_since_last_activity
FROM customers c
LEFT JOIN branches b ON c.home_branch_id = b.branch_id
LEFT JOIN advisors adv ON c.assigned_advisor_id = adv.advisor_id
LEFT JOIN accounts a ON c.customer_id = a.customer_id
LEFT JOIN transactions t ON a.account_id = t.account_id
GROUP BY 
    c.customer_id, c.customer_code, c.first_name, c.last_name, 
    c.wealth_tier, c.risk_profile, c.annual_income, c.kyc_status, 
    c.status, c.onboarding_date, b.branch_name, b.city, 
    adv.first_name, adv.last_name, adv.title;

-- ----------------------------------------------------------------------------------------------------
-- VIEW 2: Monthly Wealth Flow Trends & Net New Money (NNM)
-- Essential for executive quarterly metrics reporting on client asset movements.
-- ----------------------------------------------------------------------------------------------------
DROP VIEW IF EXISTS v_monthly_wealth_flows;

CREATE VIEW v_monthly_wealth_flows AS
SELECT 
    DATE_FORMAT(t.transaction_time, '%Y-%m') AS activity_month,
    COUNT(t.transaction_id) AS total_transactions,
    COUNT(DISTINCT t.account_id) AS transacting_accounts,
    SUM(CASE WHEN tc.flow_type = 'Credit' THEN t.amount ELSE 0.00 END) AS total_inflow,
    SUM(CASE WHEN tc.flow_type = 'Debit' THEN t.amount ELSE 0.00 END) AS total_outflow,
    SUM(CASE WHEN tc.flow_type = 'Credit' THEN t.amount ELSE -t.amount END) AS net_new_money,
    SUM(CASE WHEN tc.is_fee = TRUE THEN t.amount ELSE 0.00 END) AS advisory_fees_collected,
    ROUND(AVG(t.amount), 2) AS avg_transaction_value
FROM transactions t
JOIN transaction_categories tc ON t.category_id = tc.category_id
WHERE t.status = 'Completed'
GROUP BY DATE_FORMAT(t.transaction_time, '%Y-%m');

-- ----------------------------------------------------------------------------------------------------
-- VIEW 3: Advisor Book of Business & Performance Matrix
-- Used by Wealth Management Home Office leadership to track advisor productivity and AUM targets.
-- ----------------------------------------------------------------------------------------------------
DROP VIEW IF EXISTS v_advisor_book_of_business;

CREATE VIEW v_advisor_book_of_business AS
SELECT 
    adv.advisor_id,
    adv.advisor_code,
    CONCAT(adv.first_name, ' ', adv.last_name) AS advisor_name,
    adv.title,
    b.branch_name,
    b.region,
    adv.target_aum,
    COUNT(DISTINCT c.customer_id) AS total_clients,
    COUNT(DISTINCT CASE WHEN c.wealth_tier IN ('High-Net-Worth (HNW)', 'Ultra-HNW (UHNW)') THEN c.customer_id END) AS hnw_clients,
    COALESCE(SUM(a.current_balance), 0.00) AS current_aum,
    ROUND((COALESCE(SUM(a.current_balance), 0.00) / adv.target_aum) * 100, 2) AS target_attainment_pct,
    ROUND(COALESCE(SUM(a.current_balance), 0.00) / NULLIF(COUNT(DISTINCT c.customer_id), 0), 2) AS avg_client_aum
FROM advisors adv
JOIN branches b ON adv.branch_id = b.branch_id
LEFT JOIN customers c ON adv.advisor_id = c.assigned_advisor_id
LEFT JOIN accounts a ON c.customer_id = a.customer_id
GROUP BY 
    adv.advisor_id, adv.advisor_code, adv.first_name, adv.last_name, 
    adv.title, b.branch_name, b.region, adv.target_aum;

-- ----------------------------------------------------------------------------------------------------
-- VIEW 4: AML & Compliance Risk Watchlist
-- Captures high-risk transactions, structuring patterns, and flagged entries for audit teams.
-- ----------------------------------------------------------------------------------------------------
DROP VIEW IF EXISTS v_high_risk_transactions;

CREATE VIEW v_high_risk_transactions AS
SELECT 
    t.transaction_id,
    t.transaction_ref,
    t.transaction_time,
    t.amount,
    t.status,
    t.channel,
    tc.category_name,
    a.account_number,
    c.customer_code,
    CONCAT(c.first_name, ' ', c.last_name) AS customer_name,
    c.wealth_tier,
    b.branch_name,
    CASE 
        WHEN t.amount BETWEEN 9000.00 AND 9999.99 THEN 'Structuring / Smurfing Alert'
        WHEN t.amount > 1000000.00 THEN 'Ultra-High-Value Wire (> $1M)'
        WHEN t.status = 'Flagged' THEN 'System Exception Flag'
        ELSE 'Compliance Review Required'
    END AS risk_classification
FROM transactions t
JOIN accounts a ON t.account_id = a.account_id
JOIN customers c ON a.customer_id = c.customer_id
JOIN branches b ON a.branch_id = b.branch_id
JOIN transaction_categories tc ON t.category_id = tc.category_id
WHERE t.status = 'Flagged' 
   OR (t.amount BETWEEN 9000.00 AND 9999.99 AND tc.category_id = 'CAT_DEP')
   OR t.amount >= 250000.00;
