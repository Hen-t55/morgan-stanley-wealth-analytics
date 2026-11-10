-- ====================================================================================================
-- PROJECT: Banking Transaction & Customer Wealth Analytics
-- TARGET INSTITUTION: Morgan Stanley (Wealth Management Division)
-- MODULE: 01_schema_ddl.sql
-- DESCRIPTION: Relational Database Schema DDL with Integrity Constraints, Foreign Keys & Indexes
-- ====================================================================================================

CREATE DATABASE IF NOT EXISTS morgan_stanley_wm;
USE morgan_stanley_wm;

-- Drop dependent tables in reverse FK dependency order
DROP TABLE IF EXISTS transactions;
DROP TABLE IF EXISTS accounts;
DROP TABLE IF EXISTS customers;
DROP TABLE IF EXISTS advisors;
DROP TABLE IF EXISTS transaction_categories;
DROP TABLE IF EXISTS account_types;
DROP TABLE IF EXISTS branches;

-- ----------------------------------------------------------------------------------------------------
-- 1. BRANCHES (Wealth Management Hubs)
-- ----------------------------------------------------------------------------------------------------
CREATE TABLE branches (
    branch_id INT PRIMARY KEY AUTO_INCREMENT,
    branch_code VARCHAR(20) NOT NULL UNIQUE,
    branch_name VARCHAR(100) NOT NULL,
    city VARCHAR(50) NOT NULL,
    country VARCHAR(50) NOT NULL,
    region VARCHAR(30) NOT NULL,
    head_advisor VARCHAR(100) NOT NULL,
    opened_year INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------------------------------------------------------------------------------
-- 2. ADVISORS (Wealth Managers & Financial Advisors)
-- ----------------------------------------------------------------------------------------------------
CREATE TABLE advisors (
    advisor_id INT PRIMARY KEY AUTO_INCREMENT,
    advisor_code VARCHAR(20) NOT NULL UNIQUE,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    phone VARCHAR(30),
    branch_id INT NOT NULL,
    title VARCHAR(50) NOT NULL,
    target_aum DECIMAL(15,2) NOT NULL,
    hire_date DATE NOT NULL,
    status ENUM('Active', 'On Leave', 'Inactive') DEFAULT 'Active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_advisor_branch FOREIGN KEY (branch_id) 
        REFERENCES branches (branch_id) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------------------------------------------------------------------------------
-- 3. ACCOUNT TYPES
-- ----------------------------------------------------------------------------------------------------
CREATE TABLE account_types (
    type_id VARCHAR(20) PRIMARY KEY,
    type_name VARCHAR(60) NOT NULL,
    category ENUM('Transactional', 'Deposit', 'Investment', 'Fiduciary', 'Retirement') NOT NULL,
    min_balance DECIMAL(15,2) DEFAULT 0.00,
    interest_rate DECIMAL(5,4) DEFAULT 0.0000,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------------------------------------------------------------------------------
-- 4. TRANSACTION CATEGORIES
-- ----------------------------------------------------------------------------------------------------
CREATE TABLE transaction_categories (
    category_id VARCHAR(20) PRIMARY KEY,
    category_name VARCHAR(60) NOT NULL,
    flow_type ENUM('Credit', 'Debit', 'Variable', 'Transfer') NOT NULL,
    is_fee BOOLEAN DEFAULT FALSE,
    description VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------------------------------------------------------------------------------
-- 5. CUSTOMERS (Retail, Mass Affluent, HNW, UHNW)
-- ----------------------------------------------------------------------------------------------------
CREATE TABLE customers (
    customer_id INT PRIMARY KEY AUTO_INCREMENT,
    customer_code VARCHAR(20) NOT NULL UNIQUE,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL,
    phone VARCHAR(40),
    date_of_birth DATE NOT NULL,
    wealth_tier ENUM('Retail', 'Mass Affluent', 'High-Net-Worth (HNW)', 'Ultra-HNW (UHNW)') NOT NULL,
    risk_profile ENUM('Conservative', 'Moderate', 'Growth', 'Aggressive') NOT NULL,
    home_branch_id INT NOT NULL,
    assigned_advisor_id INT NOT NULL,
    kyc_status ENUM('Verified', 'Pending Review', 'Exempt') DEFAULT 'Verified',
    onboarding_date DATE NOT NULL,
    annual_income DECIMAL(15,2) NOT NULL,
    status ENUM('Active', 'Inactive', 'Dormant') DEFAULT 'Active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_customer_branch FOREIGN KEY (home_branch_id) 
        REFERENCES branches (branch_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_customer_advisor FOREIGN KEY (assigned_advisor_id) 
        REFERENCES advisors (advisor_id) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------------------------------------------------------------------------------
-- 6. ACCOUNTS (Custodial, Portfolio, Checking, Savings)
-- ----------------------------------------------------------------------------------------------------
CREATE TABLE accounts (
    account_id INT PRIMARY KEY AUTO_INCREMENT,
    account_number VARCHAR(30) NOT NULL UNIQUE,
    customer_id INT NOT NULL,
    account_type_id VARCHAR(20) NOT NULL,
    branch_id INT NOT NULL,
    current_balance DECIMAL(15,2) NOT NULL DEFAULT 0.00,
    currency VARCHAR(3) DEFAULT 'USD',
    opened_date DATE NOT NULL,
    status ENUM('Active', 'Suspended', 'Dormant', 'Closed') DEFAULT 'Active',
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_account_customer FOREIGN KEY (customer_id) 
        REFERENCES customers (customer_id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_account_type FOREIGN KEY (account_type_id) 
        REFERENCES account_types (type_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_account_branch FOREIGN KEY (branch_id) 
        REFERENCES branches (branch_id) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------------------------------------------------------------------------------
-- 7. TRANSACTIONS (Financial Flow & Portfolio Movements)
-- ----------------------------------------------------------------------------------------------------
CREATE TABLE transactions (
    transaction_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    transaction_ref VARCHAR(40) NOT NULL UNIQUE,
    account_id INT NOT NULL,
    category_id VARCHAR(20) NOT NULL,
    amount DECIMAL(15,2) NOT NULL,
    transaction_time DATETIME NOT NULL,
    channel ENUM('Wealth Online Portal', 'Advisor Desk', 'Wire Desk', 'Mobile App', 'ATM') NOT NULL,
    status ENUM('Completed', 'Flagged', 'Pending', 'Failed') DEFAULT 'Completed',
    description VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_txn_account FOREIGN KEY (account_id) 
        REFERENCES accounts (account_id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_txn_category FOREIGN KEY (category_id) 
        REFERENCES transaction_categories (category_id) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------------------------------------------------------------------------------
-- PERFORMANCE OPTIMIZATION INDEXES
-- ----------------------------------------------------------------------------------------------------
-- Index for transaction queries filtered by account and date range
CREATE INDEX idx_txn_account_time ON transactions (account_id, transaction_time);

-- Index for category-level aggregation
CREATE INDEX idx_txn_category ON transactions (category_id);

-- Index for risk and compliance filtering
CREATE INDEX idx_txn_status ON transactions (status);

-- Composite index for monthly trend reporting
CREATE INDEX idx_txn_time_amount ON transactions (transaction_time, amount);

-- Index for customer wealth segmentation
CREATE INDEX idx_customer_wealth_tier ON customers (wealth_tier);

-- Index for advisor client book queries
CREATE INDEX idx_customer_advisor ON customers (assigned_advisor_id);

-- Index for customer account lookups
CREATE INDEX idx_accounts_customer ON accounts (customer_id);
