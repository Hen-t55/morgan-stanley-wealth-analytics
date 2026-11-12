-- ====================================================================================================
-- PROJECT: Wealth Management & Banking Transaction Intelligence System
-- MODULE: 03_stored_procedures.sql
-- DESCRIPTION: Production Stored Procedures Demonstrating Transactions, Control Flow & Error Handling
-- ====================================================================================================

USE wealth_management_db;

DELIMITER $$

-- ----------------------------------------------------------------------------------------------------
-- PROCEDURE 1: Client Portfolio & Transaction Statement Generator
-- Generates an executive client statement across all accounts for an arbitrary date window.
-- ----------------------------------------------------------------------------------------------------
DROP PROCEDURE IF EXISTS sp_generate_client_portfolio_statement$$

CREATE PROCEDURE sp_generate_client_portfolio_statement (
    IN p_customer_id INT,
    IN p_start_date DATE,
    IN p_end_date DATE
)
BEGIN
    -- Declare local tracking variables
    DECLARE v_customer_exists INT DEFAULT 0;
    DECLARE v_client_name VARCHAR(100);
    DECLARE v_wealth_tier VARCHAR(50);
    DECLARE v_current_aum DECIMAL(15,2);

    -- 1. Validate customer existence
    SELECT COUNT(*), CONCAT(first_name, ' ', last_name), wealth_tier
    INTO v_customer_exists, v_client_name, v_wealth_tier
    FROM customers
    WHERE customer_id = p_customer_id
    GROUP BY first_name, last_name, wealth_tier;

    IF v_customer_exists = 0 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Client statement generation failed: customer_id does not exist.';
    END IF;

    -- 2. Fetch current total AUM across all accounts
    SELECT COALESCE(SUM(current_balance), 0.00)
    INTO v_current_aum
    FROM accounts
    WHERE customer_id = p_customer_id;

    -- 3. Return Section 1: Client Portfolio Header Summary
    SELECT 
        p_customer_id AS customer_id,
        v_client_name AS client_name,
        v_wealth_tier AS wealth_tier,
        v_current_aum AS total_portfolio_aum,
        p_start_date AS statement_start_date,
        p_end_date AS statement_end_date,
        COUNT(t.transaction_id) AS transactions_in_period,
        SUM(CASE WHEN tc.flow_type = 'Credit' THEN t.amount ELSE 0.00 END) AS total_credits,
        SUM(CASE WHEN tc.flow_type = 'Debit' THEN t.amount ELSE 0.00 END) AS total_debits,
        SUM(CASE WHEN tc.flow_type = 'Credit' THEN t.amount ELSE -t.amount END) AS net_period_flow
    FROM accounts a
    JOIN transactions t ON a.account_id = t.account_id
    JOIN transaction_categories tc ON t.category_id = tc.category_id
    WHERE a.customer_id = p_customer_id
      AND DATE(t.transaction_time) BETWEEN p_start_date AND p_end_date;

    -- 4. Return Section 2: Detailed Line-Item Ledger
    SELECT 
        t.transaction_id,
        t.transaction_ref,
        a.account_number,
        at.type_name AS account_type,
        t.transaction_time,
        tc.category_name,
        tc.flow_type,
        t.amount,
        t.channel,
        t.status,
        t.description
    FROM accounts a
    JOIN account_types at ON a.account_type_id = at.type_id
    JOIN transactions t ON a.account_id = t.account_id
    JOIN transaction_categories tc ON t.category_id = tc.category_id
    WHERE a.customer_id = p_customer_id
      AND DATE(t.transaction_time) BETWEEN p_start_date AND p_end_date
    ORDER BY t.transaction_time DESC;

END$$


-- ----------------------------------------------------------------------------------------------------
-- PROCEDURE 2: AML / Risk Engine - Detect & Flag Statistical Anomalies
-- Flags transactions exceeding N times the account's historical rolling average.
-- ----------------------------------------------------------------------------------------------------
DROP PROCEDURE IF EXISTS sp_detect_and_flag_anomalies$$

CREATE PROCEDURE sp_detect_and_flag_anomalies (
    IN p_threshold_multiplier DECIMAL(4,2),
    OUT p_flagged_count INT
)
BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    START TRANSACTION;

    -- Update transactions that exceed multiplier * account's historical average
    UPDATE transactions t
    JOIN (
        SELECT 
            t_inner.transaction_id,
            t_inner.amount,
            acc_avg.avg_amount
        FROM transactions t_inner
        JOIN (
            SELECT account_id, AVG(amount) AS avg_amount
            FROM transactions
            WHERE status = 'Completed'
            GROUP BY account_id
            HAVING COUNT(transaction_id) >= 5
        ) acc_avg ON t_inner.account_id = acc_avg.account_id
        WHERE t_inner.amount > (acc_avg.avg_amount * p_threshold_multiplier)
          AND t_inner.status <> 'Flagged'
    ) anomalies ON t.transaction_id = anomalies.transaction_id
    SET t.status = 'Flagged',
        t.description = CONCAT('Auto-Flagged: Amount exceeds ', p_threshold_multiplier, 'x historical average');

    SET p_flagged_count = ROW_COUNT();

    COMMIT;
END$$


-- ----------------------------------------------------------------------------------------------------
-- PROCEDURE 3: Reassign Client Book Between Advisors (With ACID Transaction Safety)
-- Enables Wealth Management Ops to rebalance client relationships with rollback safety.
-- ----------------------------------------------------------------------------------------------------
DROP PROCEDURE IF EXISTS sp_reassign_client_advisor$$

CREATE PROCEDURE sp_reassign_client_advisor (
    IN p_customer_id INT,
    IN p_new_advisor_id INT
)
BEGIN
    DECLARE v_advisor_exists INT DEFAULT 0;
    DECLARE v_customer_exists INT DEFAULT 0;

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    START TRANSACTION;

    -- Validate target advisor
    SELECT COUNT(*) INTO v_advisor_exists FROM advisors WHERE advisor_id = p_new_advisor_id AND status = 'Active';
    IF v_advisor_exists = 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Target advisor does not exist or is inactive.';
    END IF;

    -- Validate customer
    SELECT COUNT(*) INTO v_customer_exists FROM customers WHERE customer_id = p_customer_id;
    IF v_customer_exists = 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Customer does not exist.';
    END IF;

    -- Update customer's assigned advisor
    UPDATE customers 
    SET assigned_advisor_id = p_new_advisor_id 
    WHERE customer_id = p_customer_id;

    COMMIT;

    SELECT 
        c.customer_id,
        CONCAT(c.first_name, ' ', c.last_name) AS customer_name,
        CONCAT(adv.first_name, ' ', adv.last_name) AS new_assigned_advisor,
        adv.title AS advisor_title,
        'Successfully Reassigned' AS status_message
    FROM customers c
    JOIN advisors adv ON c.assigned_advisor_id = adv.advisor_id
    WHERE c.customer_id = p_customer_id;

END$$

DELIMITER ;
