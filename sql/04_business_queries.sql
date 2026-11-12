-- ====================================================================================================
-- PROJECT: Wealth Management & Banking Transaction Intelligence System
-- MODULE: 04_business_queries.sql
-- DESCRIPTION: Business Intelligence Query Suite using Advanced Joins, CTEs & Window Functions
-- ====================================================================================================

USE wealth_management_db;

-- ====================================================================================================
-- QUESTION 1: Who are the top 10 customers by total transaction volume?
-- CONCEPTS: JOIN, GROUP BY, SUM, DENSE_RANK() Window Function
-- BUSINESS VALUE: Identifies key commercial & wealth relationships driving the firm's liquidity flow.
-- ====================================================================================================
WITH customer_volume_ranked AS (
    SELECT 
        c.customer_id,
        c.customer_code,
        CONCAT(c.first_name, ' ', c.last_name) AS customer_name,
        c.wealth_tier,
        b.branch_name,
        COUNT(t.transaction_id) AS total_transactions,
        SUM(t.amount) AS total_volume_usd,
        ROUND(AVG(t.amount), 2) AS avg_transaction_size,
        DENSE_RANK() OVER (ORDER BY SUM(t.amount) DESC) AS volume_rank
    FROM customers c
    JOIN accounts a ON c.customer_id = a.customer_id
    JOIN transactions t ON a.account_id = t.account_id
    JOIN branches b ON c.home_branch_id = b.branch_id
    WHERE t.status = 'Completed'
    GROUP BY c.customer_id, c.customer_code, c.first_name, c.last_name, c.wealth_tier, b.branch_name
)
SELECT 
    volume_rank,
    customer_code,
    customer_name,
    wealth_tier,
    branch_name,
    total_transactions,
    total_volume_usd,
    avg_transaction_size
FROM customer_volume_ranked
WHERE volume_rank <= 10
ORDER BY volume_rank ASC;


-- ====================================================================================================
-- QUESTION 2: What are the monthly transaction trends and Month-over-Month (MoM) growth rates?
-- CONCEPTS: DATE_FORMAT, Common Table Expressions (CTEs), LAG() Window Function, NULLIF
-- BUSINESS VALUE: Helps Home Office track macro transaction velocity, seasonal dips, and capital growth.
-- ====================================================================================================
WITH monthly_metrics AS (
    SELECT 
        DATE_FORMAT(t.transaction_time, '%Y-%m') AS txn_month,
        COUNT(t.transaction_id) AS monthly_txn_count,
        SUM(t.amount) AS monthly_volume_usd,
        ROUND(AVG(t.amount), 2) AS monthly_avg_ticket
    FROM transactions t
    WHERE t.status = 'Completed'
    GROUP BY DATE_FORMAT(t.transaction_time, '%Y-%m')
),
monthly_mom AS (
    SELECT 
        txn_month,
        monthly_txn_count,
        LAG(monthly_txn_count, 1) OVER (ORDER BY txn_month) AS prev_month_txn_count,
        monthly_volume_usd,
        LAG(monthly_volume_usd, 1) OVER (ORDER BY txn_month) AS prev_month_volume_usd,
        monthly_avg_ticket
    FROM monthly_metrics
)
SELECT 
    txn_month,
    monthly_txn_count,
    ROUND(((monthly_txn_count - prev_month_txn_count) / NULLIF(prev_month_txn_count, 0)) * 100, 2) AS mom_count_growth_pct,
    monthly_volume_usd,
    ROUND(((monthly_volume_usd - prev_month_volume_usd) / NULLIF(prev_month_volume_usd, 0)) * 100, 2) AS mom_volume_growth_pct,
    monthly_avg_ticket
FROM monthly_mom
ORDER BY txn_month DESC;


-- ====================================================================================================
-- QUESTION 3: Which branches generate the most transactions and transaction volume?
-- CONCEPTS: Multiple INNER JOINs, Aggregate Functions, Window SUM() OVER() for Contribution %
-- BUSINESS VALUE: Evaluates regional hub productivity (Mumbai BKC vs NY Park Ave vs London).
-- ====================================================================================================
WITH branch_aggregates AS (
    SELECT 
        b.branch_id,
        b.branch_code,
        b.branch_name,
        b.city,
        b.region,
        COUNT(t.transaction_id) AS branch_txn_count,
        SUM(t.amount) AS branch_volume_usd
    FROM branches b
    JOIN accounts a ON b.branch_id = a.branch_id
    JOIN transactions t ON a.account_id = t.account_id
    WHERE t.status = 'Completed'
    GROUP BY b.branch_id, b.branch_code, b.branch_name, b.city, b.region
)
SELECT 
    branch_name,
    city,
    region,
    branch_txn_count,
    ROUND((branch_txn_count / SUM(branch_txn_count) OVER()) * 100, 2) AS pct_of_firm_txns,
    branch_volume_usd,
    ROUND((branch_volume_usd / SUM(branch_volume_usd) OVER()) * 100, 2) AS pct_of_firm_volume,
    DENSE_RANK() OVER (ORDER BY branch_volume_usd DESC) AS volume_rank
FROM branch_aggregates
ORDER BY branch_volume_usd DESC;


-- ====================================================================================================
-- QUESTION 4: What is the average transaction value segmented across wealth tiers and account types?
-- CONCEPTS: Multi-table JOINs, GROUP BY, AVG, CASE statement conditional metrics
-- BUSINESS VALUE: Informs fee scheduling, ticket-size profiling, and resource allocation.
-- ====================================================================================================
SELECT 
    c.wealth_tier,
    at.type_name AS account_type,
    COUNT(t.transaction_id) AS total_transactions,
    ROUND(AVG(t.amount), 2) AS avg_transaction_value,
    ROUND(MIN(t.amount), 2) AS min_transaction_value,
    ROUND(MAX(t.amount), 2) AS max_transaction_value,
    ROUND(SUM(t.amount), 2) AS total_volume_usd
FROM transactions t
JOIN accounts a ON t.account_id = a.account_id
JOIN customers c ON a.customer_id = c.customer_id
JOIN account_types at ON a.account_type_id = at.type_id
WHERE t.status = 'Completed'
GROUP BY c.wealth_tier, at.type_name
ORDER BY c.wealth_tier, avg_transaction_value DESC;


-- ====================================================================================================
-- QUESTION 5: Which customers have declining activity (Dormancy / Churn Early-Warning System)?
-- CONCEPTS: CTEs, Subqueries, Date Arithmetic, Window Functions, Filtered Conditional Aggregation
-- BUSINESS VALUE: Proactively detects at-risk relationships before they liquidate and leave the institution.
-- ====================================================================================================
WITH period_activity AS (
    SELECT 
        c.customer_id,
        c.customer_code,
        CONCAT(c.first_name, ' ', c.last_name) AS customer_name,
        c.wealth_tier,
        CONCAT(adv.first_name, ' ', adv.last_name) AS advisor_name,
        -- Period 1: Prior 90 to 180 days
        SUM(CASE 
            WHEN t.transaction_time >= DATE_SUB('2026-02-28', INTERVAL 180 DAY)
             AND t.transaction_time < DATE_SUB('2026-02-28', INTERVAL 90 DAY)
            THEN 1 ELSE 0 END) AS prior_period_txn_count,
        SUM(CASE 
            WHEN t.transaction_time >= DATE_SUB('2026-02-28', INTERVAL 180 DAY)
             AND t.transaction_time < DATE_SUB('2026-02-28', INTERVAL 90 DAY)
            THEN t.amount ELSE 0.00 END) AS prior_period_volume,
        -- Period 2: Recent 90 days
        SUM(CASE 
            WHEN t.transaction_time >= DATE_SUB('2026-02-28', INTERVAL 90 DAY)
            THEN 1 ELSE 0 END) AS recent_period_txn_count,
        SUM(CASE 
            WHEN t.transaction_time >= DATE_SUB('2026-02-28', INTERVAL 90 DAY)
            THEN t.amount ELSE 0.00 END) AS recent_period_volume
    FROM customers c
    JOIN advisors adv ON c.assigned_advisor_id = adv.advisor_id
    JOIN accounts a ON c.customer_id = a.customer_id
    LEFT JOIN transactions t ON a.account_id = t.account_id AND t.status = 'Completed'
    WHERE c.status = 'Active'
    GROUP BY c.customer_id, c.customer_code, c.first_name, c.last_name, c.wealth_tier, adv.first_name, adv.last_name
)
SELECT 
    customer_code,
    customer_name,
    wealth_tier,
    advisor_name,
    prior_period_txn_count,
    recent_period_txn_count,
    ROUND(((recent_period_txn_count - prior_period_txn_count) / NULLIF(prior_period_txn_count, 0)) * 100, 2) AS activity_change_pct,
    prior_period_volume,
    recent_period_volume,
    CASE 
        WHEN recent_period_txn_count = 0 AND prior_period_txn_count > 0 THEN 'Critically Inactive'
        WHEN recent_period_txn_count < (prior_period_txn_count * 0.4) THEN 'High Churn Risk (>60% drop)'
        ELSE 'Moderate Slowdown'
    END AS risk_tier
FROM period_activity
WHERE prior_period_txn_count >= 3
  AND recent_period_txn_count < prior_period_txn_count
ORDER BY activity_change_pct ASC
LIMIT 20;


-- ====================================================================================================
-- QUESTION 6: Which transactions are unusual or require AML / Compliance review?
-- CONCEPTS: Window Function AVG() OVER (PARTITION BY), CASE conditional labeling, CTE
-- BUSINESS VALUE: Core risk management query fulfilling Anti-Money Laundering regulatory mandates.
-- ====================================================================================================
WITH account_historical_stats AS (
    SELECT 
        account_id,
        AVG(amount) AS acc_historical_avg,
        STDDEV(amount) AS acc_stddev
    FROM transactions
    WHERE status = 'Completed'
    GROUP BY account_id
),
unusual_txns AS (
    SELECT 
        t.transaction_id,
        t.transaction_ref,
        t.transaction_time,
        c.customer_code,
        CONCAT(c.first_name, ' ', c.last_name) AS customer_name,
        c.wealth_tier,
        tc.category_name,
        t.amount,
        ROUND(ahs.acc_historical_avg, 2) AS account_avg_amount,
        ROUND(t.amount / NULLIF(ahs.acc_historical_avg, 0), 2) AS multiple_of_avg,
        t.channel,
        t.status,
        CASE 
            WHEN t.amount BETWEEN 9000.00 AND 9999.99 AND tc.category_id = 'CAT_DEP' THEN 'Potential Structuring / Smurfing ($9k-$10k)'
            WHEN t.amount > (ahs.acc_historical_avg * 4.0) THEN 'Outlier Spike (>4x Historical Average)'
            WHEN t.amount >= 500000.00 THEN 'Large Value Movement (> $500k)'
            WHEN t.status = 'Flagged' THEN 'System Exception'
            ELSE 'Normal'
        END AS anomaly_flag
    FROM transactions t
    JOIN accounts a ON t.account_id = a.account_id
    JOIN customers c ON a.customer_id = c.customer_id
    JOIN transaction_categories tc ON t.category_id = tc.category_id
    LEFT JOIN account_historical_stats ahs ON t.account_id = ahs.account_id
)
SELECT 
    transaction_ref,
    transaction_time,
    customer_code,
    customer_name,
    wealth_tier,
    category_name,
    amount,
    account_avg_amount,
    multiple_of_avg,
    channel,
    anomaly_flag
FROM unusual_txns
WHERE anomaly_flag <> 'Normal'
ORDER BY amount DESC
LIMIT 25;


-- ====================================================================================================
-- QUESTION 7 (WEALTH SPECIFIC): Net New Money (NNM) & Inflow/Outflow ratio across branches
-- CONCEPTS: CASE WHEN Aggregation, Division by Zero protection (NULLIF), Star schema JOINs
-- BUSINESS VALUE: Net New Money is the primary organic growth metric reported in institutional wealth earnings.
-- ====================================================================================================
SELECT 
    b.branch_name,
    b.city,
    b.region,
    COUNT(t.transaction_id) AS total_txns,
    SUM(CASE WHEN tc.flow_type = 'Credit' THEN t.amount ELSE 0.00 END) AS total_inflow_usd,
    SUM(CASE WHEN tc.flow_type = 'Debit' THEN t.amount ELSE 0.00 END) AS total_outflow_usd,
    SUM(CASE WHEN tc.flow_type = 'Credit' THEN t.amount ELSE -t.amount END) AS net_new_money_usd,
    ROUND(
        SUM(CASE WHEN tc.flow_type = 'Credit' THEN t.amount ELSE 0.00 END) / 
        NULLIF(SUM(CASE WHEN tc.flow_type = 'Debit' THEN t.amount ELSE 0.00 END), 0), 2
    ) AS inflow_to_outflow_ratio
FROM branches b
JOIN accounts a ON b.branch_id = a.branch_id
JOIN transactions t ON a.account_id = t.account_id
JOIN transaction_categories tc ON t.category_id = tc.category_id
WHERE t.status = 'Completed'
GROUP BY b.branch_name, b.city, b.region
ORDER BY net_new_money_usd DESC;


-- ====================================================================================================
-- QUESTION 8 (WEALTH SPECIFIC): High-Value Wealth Tier Migration Opportunities
-- CONCEPTS: HAVING clause, Subqueries, Conditional CASE, Tier upgrade qualification
-- BUSINESS VALUE: Uncovers Mass Affluent clients who qualify for High-Net-Worth private wealth services.
-- ====================================================================================================
SELECT 
    c.customer_id,
    c.customer_code,
    CONCAT(c.first_name, ' ', c.last_name) AS customer_name,
    c.wealth_tier AS current_tier,
    COUNT(a.account_id) AS total_accounts,
    SUM(a.current_balance) AS total_relationship_balance,
    CONCAT(adv.first_name, ' ', adv.last_name) AS current_advisor,
    'Eligible for High-Net-Worth Dedicated RM' AS upgrade_recommendation
FROM customers c
JOIN accounts a ON c.customer_id = a.customer_id
JOIN advisors adv ON c.assigned_advisor_id = adv.advisor_id
WHERE c.wealth_tier = 'Mass Affluent'
GROUP BY c.customer_id, c.customer_code, c.first_name, c.last_name, c.wealth_tier, adv.first_name, adv.last_name
HAVING SUM(a.current_balance) >= 500000.00
ORDER BY total_relationship_balance DESC;


-- ====================================================================================================
-- QUESTION 9 (WEALTH SPECIFIC): Advisor Book of Business Performance & Target Attainment
-- CONCEPTS: DENSE_RANK(), Multi-level aggregation, Percentage calculations
-- BUSINESS VALUE: Core management tool for Managing Directors to evaluate advisor quotas.
-- ====================================================================================================
SELECT 
    adv.advisor_code,
    CONCAT(adv.first_name, ' ', adv.last_name) AS advisor_name,
    adv.title,
    b.branch_name,
    adv.target_aum,
    COALESCE(SUM(a.current_balance), 0.00) AS actual_aum,
    ROUND((COALESCE(SUM(a.current_balance), 0.00) / adv.target_aum) * 100, 2) AS attainment_pct,
    COUNT(DISTINCT c.customer_id) AS total_clients_managed,
    DENSE_RANK() OVER (ORDER BY COALESCE(SUM(a.current_balance), 0.00) DESC) AS firmwide_aum_rank
FROM advisors adv
JOIN branches b ON adv.branch_id = b.branch_id
LEFT JOIN customers c ON adv.advisor_id = c.assigned_advisor_id
LEFT JOIN accounts a ON c.customer_id = a.customer_id
GROUP BY adv.advisor_code, adv.first_name, adv.last_name, adv.title, b.branch_name, adv.target_aum
ORDER BY actual_aum DESC;


-- ====================================================================================================
-- QUESTION 10 (WEALTH SPECIFIC): Fee Revenue & Margin Contribution by Channel
-- CONCEPTS: Filtering on boolean attributes, Grouping by channel, Revenue share calculation
-- BUSINESS VALUE: Demonstrates profitability analysis and digital adoption efficiency.
-- ====================================================================================================
SELECT 
    t.channel,
    COUNT(t.transaction_id) AS total_fee_events,
    SUM(t.amount) AS total_advisory_fees_collected,
    ROUND(AVG(t.amount), 2) AS avg_fee_per_transaction,
    ROUND((SUM(t.amount) / SUM(SUM(t.amount)) OVER()) * 100, 2) AS pct_of_total_fee_revenue
FROM transactions t
JOIN transaction_categories tc ON t.category_id = tc.category_id
WHERE tc.is_fee = TRUE
  AND t.status = 'Completed'
GROUP BY t.channel
ORDER BY total_advisory_fees_collected DESC;
