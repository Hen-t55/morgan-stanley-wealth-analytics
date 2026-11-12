# Wealth Management & Financial Analytics — Resume & Interview Guide

This guide equips you to present this project during applications and technical interview rounds for **Data Analyst, Wealth Management Analyst, and Business Intelligence roles** across top-tier financial institutions.

---

## 1. Tailored Resume Entry (Ready to Copy-Paste)

### Option A: Standard 4-Bullet Format (Recommended for Tech & Analyst Resumes)
```text
Banking Transaction & Customer Wealth Analytics | SQL, MySQL, Python, Power BI, Streamlit
• Engineered a normalized relational database in MySQL with 7 interconnected entities (Branches, Advisors, Customers, Accounts, Transactions) managing $1.4B+ in simulated Assets Under Management (AUM).
• Developed advanced SQL queries utilizing Common Table Expressions (CTEs), multi-table joins, and window functions (DENSE_RANK, LAG, rolling averages) to track Net New Money (NNM), client churn risk, and regional branch liquidity.
• Built stored procedures and views for automated Anti-Money Laundering (AML) surveillance, detecting outlier spikes (>4x historical average) and regulatory structuring patterns ($9k–$10k threshold).
• Integrated database with Power BI using Star Schema modeling and authored 15+ DAX measures (AUM, MoM growth %, Inflow-to-Outflow ratios) to construct an executive wealth management dashboard.
• Automated the end-to-end ETL and data generation lifecycle using Python (Faker, Pandas, NumPy), producing 26,000+ statistically calibrated financial transaction records.
```

### Option B: Concise 3-Bullet Format (If Space-Constrained)
```text
Wealth Management & Banking Transaction Analytics | SQL (MySQL), Power BI, Python
• Designed a production-grade relational database and automated Python ETL pipeline simulating 1,000 wealth clients, 2,400+ accounts, and 26,000+ transactions spanning global financial hubs.
• Authored complex SQL suites employing CTEs, window functions (LAG, SUM OVER), and stored procedures to calculate AUM trends, Net New Money, customer dormancy risk, and AML fraud anomalies.
• Connected MySQL to Power BI via Star Schema dimensional modeling, authoring custom DAX measures for executive reporting on advisor quota attainment, wealth tier migrations, and channel adoption.
```

---

## 2. Core Competency Alignment for Financial Analytics Roles

| Financial Analyst & Data Engineering Competency | How This Project Directly Demonstrates It |
| :--- | :--- |
| **Relational Database Design & Production SQL** | DDL schema with primary/foreign keys, check constraints, composite indexing (`idx_txn_account_time`), CTEs, window functions, and ACID-compliant stored procedures. |
| **Ad-Hoc Querying & Metrics Reporting** | 10 dedicated business SQL scripts addressing executive queries, AUM calculations, Net New Money (NNM), and advisor book-of-business metrics. |
| **Python for ETL & Data Engineering** | End-to-end automated Python data generation and batch database loading script (`generate_data.py` and `load_to_mysql.py`). |
| **Business Intelligence & Executive Dashboards** | 4-page executive interactive dashboard with dimensional star schema, time intelligence, custom DAX calculations, and Streamlit interactive web portal. |
| **Financial Domain Modeling & Business Processes** | Modeled the complete client lifecycle: onboarding $\to$ risk profiling $\to$ advisor assignment $\to$ multi-asset transactions $\to$ statement generation $\to$ churn detection. |
| **Stakeholder Collaboration & Commercial Acumen** | Query results are framed around strategic decision-making: fee profitability, advisor rebalancing, and client tier upgrades. |

---

## 3. High-Probability Interview Questions & Model Answers

### Q1: "Why did you build a Wealth Management-focused database rather than a standard retail banking project?"
> **Model Answer:**  
> *"In institutional finance, the primary business value lies in helping clients build, preserve, and manage capital. Standard retail banking projects typically focus merely on ATM withdrawals and basic checking balances. I wanted my project to reflect real institutional wealth operations. I modeled wealth tiers from Mass Affluent to Ultra-HNW, multi-asset portfolios (brokerages, trusts, IRAs), Financial Advisors with quota targets, and key industry metrics like Assets Under Management (AUM) and Net New Money (NNM). This allowed me to write SQL that answers strategic business questions rather than just basic data retrieval."*

---

### Q2: "How did you use Window Functions in your project? Can you give specific examples?"
> **Model Answer:**  
> *"I used window functions in multiple critical analytical queries:*  
> 1. *`LAG()` for Month-over-Month (MoM) Growth:* To calculate capital inflow/outflow growth without performing expensive self-joins on date fields.  
> 2. *`DENSE_RANK()` for Ranking:* To rank top clients and advisors by volume and AUM without skipping ranks in case of ties.  
> 3. *`SUM() OVER()` for Contribution Analysis:* Calculated each branch's percentage share of firmwide transaction volume dynamically in a single pass.  
> 4. *`AVG(...) OVER(PARTITION BY account_id)`:* Computed an account's historical baseline to identify transaction spikes exceeding $3\times$ to $4\times$ the norm."*

---

### Q3: "How did you detect unusual transactions or AML (Anti-Money Laundering) patterns?"
> **Model Answer:**  
> *"I implemented a two-fold surveillance framework in SQL:*  
> *First, I looked for **Structuring / Smurfing**—where bad actors split deposits just below the \$10,000 regulatory reporting threshold. Using `CASE` statements and filtering, I flagged wire deposits between \$9,000 and \$9,999.  
> Second, I created a stored procedure `sp_detect_and_flag_anomalies` that calculates the historical average transaction size for each account and flags any single transaction exceeding a specified multiplier (e.g., $4\times$) of their typical behavior. These are automatically routed to a dedicated compliance view (`v_high_risk_transactions`)."*

---

### Q4: "How did you design the data model in Power BI?"
> **Model Answer:**  
> *"I implemented a clean **Star Schema** to optimize query performance and DAX evaluation:*  
> - *Central Fact Table:* `transactions` (recording transaction amounts, timestamps, status, and foreign keys).  
> - *Dimension Tables:* `customers`, `accounts`, `advisors`, `branches`, `transaction_categories`, `account_types`, and a generated `Dim_Date` table using DAX `CALENDAR()`.  
> *I avoided bidirectional filters to prevent ambiguity and ensure high-speed cross-filtering across wealth tiers, branches, and date ranges."*

---

### Q5: "How did you ensure database performance when querying 26,000+ transactions?"
> **Model Answer:**  
> *"I created targeted composite and single-column B-tree indexes:*  
> - `CREATE INDEX idx_txn_account_time ON transactions (account_id, transaction_time);` *This eliminated full table scans when running customer statement lookups and rolling average calculations.*  
> - `idx_customer_wealth_tier` *and* `idx_customer_advisor` *to optimize aggregations on advisor client books and tier segmentation.*  
> *Additionally, I used CTEs to aggregate data at lower grains before joining to large dimension tables, minimizing Cartesian product overhead."*

---

### Q6: "How does Net New Money (NNM) work in your project?"
> **Model Answer:**  
> *"In wealth management, Net New Money represents organic asset growth. In my database, transaction categories are tagged as either `Credit` (inflow like wire deposits, asset transfers) or `Debit` (outflow like withdrawals, liquidations).  
> In SQL and DAX, I calculated:*  
> $$\text{Net New Money} = \sum(\text{Credit Amounts}) - \sum(\text{Debit Amounts})$$  
> *Filtering only completed transactions. This allowed us to assess whether branches like Mumbai BKC or New York Park Avenue were organically gaining or shedding liquidity."*
