# Power BI Dashboard Implementation Guide
### Project: Wealth Management & Banking Transaction Intelligence

This guide walks you through building an enterprise-grade, 4-page Power BI dashboard modeled after institutional private banking reporting standards.

---

## 1. Connecting Data in Power BI Desktop

You can load the dataset into Power BI Desktop using either of two methods:

### Method A: Direct Connection to MySQL Database (Recommended)
1. Open **Power BI Desktop**.
2. Click **Get Data** $\to$ Select **MySQL database** $\to$ Click **Connect**.
3. In Server, enter: `localhost:3306`
4. In Database, enter: `wealth_management_db`
5. Select **Import** Mode (best for DAX calculations and offline responsiveness).
6. Under Database credentials, enter your MySQL user (`root`) and password.
7. Select all tables (`branches`, `advisors`, `account_types`, `transaction_categories`, `customers`, `accounts`, `transactions`) and click **Load**.

### Method B: Direct CSV Import (Zero Configuration Fallback)
If your Power BI environment prompts for the MySQL .NET Connector, simply use the CSVs generated in the `data/` folder:
1. Click **Get Data** $\to$ **Text/CSV**.
2. Select each CSV in `analyser/data/` (`branches.csv`, `advisors.csv`, `customers.csv`, `accounts.csv`, `transactions.csv`, `account_types.csv`, `transaction_categories.csv`).
3. Click **Load**.

---

## 2. Dimensional Modeling (Star Schema Setup)

In the **Model View** tab (left sidebar in Power BI), verify and configure the following relationships:

```
[branches] (1) --------< (*) [advisors] (1) --------< (*) [customers] (1) --------< (*) [accounts] (1) --------< (*) [transactions]
                                                                                               ^
                                                                                               | (1)
                                                                                     [account_types]
                                                                                               
[transaction_categories] (1) --------------------------------------------------------------------------------< (*) [transactions]

[Dim_Date] (1) -----------------------------------------------------------------------------------------------< (*) [transactions]
```

### Create the Date Dimension (`Dim_Date`)
Go to **Modeling** tab $\to$ **New Table** $\to$ Paste:
```dax
Dim_Date = 
VAR StartDate = DATE(2024, 1, 1)
VAR EndDate = DATE(2026, 12, 31)
RETURN
    ADDCOLUMNS(
        CALENDAR(StartDate, EndDate),
        "Year", YEAR([Date]),
        "MonthNumber", MONTH([Date]),
        "MonthName", FORMAT([Date], "MMMM"),
        "MonthShort", FORMAT([Date], "mmm"),
        "YearMonth", FORMAT([Date], "YYYY-MM"),
        "Quarter", "Q" & FORMAT([Date], "Q"),
        "QuarterYear", "Q" & FORMAT([Date], "Q") & " " & YEAR([Date])
    )
```
*Link `Dim_Date[Date]` to `transactions[transaction_time]` (Date part).*

---

## 3. Institutional Banking Color Palette

Use this color theme for an executive private wealth aesthetic:
- **Primary Deep Navy:** `#002B49` (Headers, KPI background, primary bars)
- **Financial Blue / Accent:** `#0072CE` or `#00A3E0` (Active trends, lines)
- **Wealth Gold:** `#C59B27` (HNW / UHNW highlights)
- **Positive / Inflow Green:** `#00875A`
- **Negative / Outflow Red:** `#DE350B`
- **Neutral Card Gray:** `#F4F5F7`

---

## 4. 4-Page Dashboard Architecture

### Page 1: Executive Wealth & Liquidity Command Center
**Purpose:** High-level summary of firmwide liquidity, Net New Money (NNM), and asset velocity for senior managing directors.
- **Top Filter Slicers:** `Dim_Date[YearMonth]`, `branches[region]`, `customers[wealth_tier]`.
- **Top Row (4 KPI Cards):**
  1. **Total AUM** (Formatted as Currency in Millions/Billions, e.g., `$1.45B`)
  2. **Net New Money (NNM)** (Color formatted: Green if positive, Red if negative)
  3. **Total Transaction Volume** (e.g., `$682M`)
  4. **Advisory Fee Revenue** (e.g., `$14.2M`)
- **Main Visual 1 (Clustered Column + Line Chart):**
  - X-Axis: `Dim_Date[YearMonth]`
  - Column Values: `Total Inflow` (Green) and `Total Outflow` (Red)
  - Line Value: `Net New Money` (Navy)
- **Main Visual 2 (Donut Chart):**
  - Legend: `customers[wealth_tier]`
  - Values: `Total AUM`
  - Insight: Illustrates the 80/20 rule of Wealth Management (HNW/UHNW driving majority of AUM).
- **Bottom Visual (Table / Matrix):**
  - Rows: `branches[branch_name]`
  - Values: `Total AUM`, `Net New Money`, `Total Inflow`, `Inflow-to-Outflow Ratio`.

---

### Page 2: Customer 360 & Wealth Tier Segmentation
**Purpose:** Granular breakdown of client demographics, relationship depth, and cross-sell penetration.
- **Top Slicers:** `customers[wealth_tier]`, `customers[risk_profile]`, `customers[status]`.
- **KPI Cards:** `Active Clients`, `HNW & UHNW Clients`, `Avg AUM per Client`, `Churn Risk Clients`.
- **Visual 1 (Stacked Bar Chart):**
  - Y-Axis: `customers[wealth_tier]`
  - X-Axis: `Active Clients`
  - Legend: `customers[risk_profile]` (Conservative, Moderate, Growth, Aggressive).
- **Visual 2 (Horizontal Bar Chart - Top 10 High-Value Clients):**
  - Y-Axis: `customers[full_name]`
  - X-Axis: `Total Transaction Volume`
  - Tooltip: `Total AUM`, `wealth_tier`, `assigned_advisor`.
- **Visual 3 (Treemap):**
  - Group: `account_types[type_name]`
  - Values: `Total AUM`
  - Insight: Allocation across Brokerage, High-Yield, Trust, and Checking.

---

### Page 3: Advisor Performance & Branch Productivity
**Purpose:** Home Office oversight of Relationship Managers (RMs) and quota attainment.
- **Top Slicers:** `branches[branch_name]`, `advisors[title]`.
- **Visual 1 (Scatter Plot - Advisor Performance Matrix):**
  - X-Axis: `advisors[target_aum]`
  - Y-Axis: `Total AUM`
  - Details: `advisors[advisor_name]`
  - Size: `Active Clients`
  - Reference Line: 100% Target Attainment line ($Y = X$).
- **Visual 2 (Clustered Column Chart):**
  - X-Axis: `advisors[advisor_name]` (Top 15)
  - Values: `Total AUM` vs `Target AUM`
- **Visual 3 (Summary Matrix):**
  - Columns: Advisor Name, Title, Branch, Total Clients, Actual AUM, Target AUM, Target Attainment %.

---

### Page 4: Compliance, AML & Risk Intelligence Desk
**Purpose:** Real-time surveillance of irregular transactions, structuring thresholds, and exception alerts.
- **Top Slicers:** `transactions[channel]`, `transactions[status]`, `Dim_Date[Date]`.
- **Risk KPI Cards:**
  1. `Flagged Transactions`
  2. `Compliance Exception Rate %`
  3. `Structuring Suspect Volume ($9k-$10k)`
- **Visual 1 (Line & Area Chart):**
  - X-Axis: `Dim_Date[Date]`
  - Values: `Flagged Transactions` count over time.
- **Visual 2 (Bar Chart - Flagged Events by Channel):**
  - X-Axis: `transactions[channel]`
  - Y-Axis: `Flagged Transactions`
- **Visual 3 (Detailed Audit Table - High Risk Watchlist):**
  - Pulls directly from View `v_high_risk_transactions`.
  - Columns: `transaction_time`, `transaction_ref`, `customer_code`, `customer_name`, `wealth_tier`, `amount`, `channel`, `risk_classification`.
