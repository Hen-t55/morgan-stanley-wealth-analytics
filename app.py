import os
import pandas as pd
import numpy as np
import streamlit as st
import altair as alt

st.set_page_config(
    page_title="Morgan Stanley | Wealth Management Analytics",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

@st.cache_data
def load_all_data():
    branches = pd.read_csv(os.path.join(DATA_DIR, "branches.csv"))
    advisors = pd.read_csv(os.path.join(DATA_DIR, "advisors.csv"))
    customers = pd.read_csv(os.path.join(DATA_DIR, "customers.csv"))
    accounts = pd.read_csv(os.path.join(DATA_DIR, "accounts.csv"))
    transactions = pd.read_csv(os.path.join(DATA_DIR, "transactions.csv"))
    account_types = pd.read_csv(os.path.join(DATA_DIR, "account_types.csv"))
    categories = pd.read_csv(os.path.join(DATA_DIR, "transaction_categories.csv"))

    transactions["transaction_time"] = pd.to_datetime(transactions["transaction_time"])
    transactions["month"] = transactions["transaction_time"].dt.to_period("M").astype(str)

    # Merged transactions for analytical views
    txn_merged = transactions.merge(accounts[["account_id", "customer_id", "branch_id", "account_type_id"]], on="account_id", how="left")
    txn_merged = txn_merged.merge(customers[["customer_id", "wealth_tier", "first_name", "last_name", "customer_code", "assigned_advisor_id"]], on="customer_id", how="left")
    txn_merged = txn_merged.merge(categories[["category_id", "category_name", "flow_type", "is_fee"]], on="category_id", how="left")
    txn_merged = txn_merged.merge(branches[["branch_id", "branch_name", "city", "region"]], on="branch_id", how="left")

    return branches, advisors, customers, accounts, transactions, account_types, categories, txn_merged

try:
    branches, advisors, customers, accounts, transactions, account_types, categories, txn_merged = load_all_data()
except Exception as e:
    st.error(f"Error loading datasets: {e}. Please ensure scripts/generate_data.py has been executed.")
    st.stop()

# -------------------------------------------------------------
# SIDEBAR
# -------------------------------------------------------------
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/3/34/Morgan_Stanley_Logo_1.svg", width=220)
st.sidebar.markdown("### **Wealth Management Analytics**")
st.sidebar.markdown("*Institutional Portfolio & Transaction Intelligence*")
st.sidebar.divider()

selected_region = st.sidebar.multiselect("Filter Region:", options=branches["region"].unique(), default=branches["region"].unique())
selected_tier = st.sidebar.multiselect("Filter Wealth Tier:", options=customers["wealth_tier"].unique(), default=customers["wealth_tier"].unique())

filtered_txns = txn_merged[
    (txn_merged["region"].isin(selected_region)) & 
    (txn_merged["wealth_tier"].isin(selected_tier))
]

# -------------------------------------------------------------
# HEADER & KPI BARS
# -------------------------------------------------------------
st.title("🏦 Morgan Stanley Wealth Management — Intelligence Desk")
st.caption("2027 Wealth Management Analyst Portal | Live SQL Data Model & BI Surveillance Engine")

# KPI Calculations
total_aum = accounts["current_balance"].sum()
total_clients = len(customers)
completed_txns = filtered_txns[filtered_txns["status"] == "Completed"]
inflow = completed_txns[completed_txns["flow_type"] == "Credit"]["amount"].sum()
outflow = completed_txns[completed_txns["flow_type"] == "Debit"]["amount"].sum()
net_new_money = inflow - outflow
advisory_fees = completed_txns[completed_txns["is_fee"] == True]["amount"].sum()
flagged_count = (filtered_txns["status"] == "Flagged").sum()

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Firmwide AUM", f"${total_aum/1e9:.2f}B", "+6.4% YoY")
col2.metric("Net New Money (NNM)", f"${net_new_money/1e6:.1f}M", f"{'▲' if net_new_money > 0 else '▼'} Organic Flow")
col3.metric("Total Txn Volume", f"${completed_txns['amount'].sum()/1e6:.1f}M", f"{len(completed_txns):,} Completed")
col4.metric("Advisory Fee Income", f"${advisory_fees/1e6:.2f}M", "Annualized")
col5.metric("Compliance Flags", f"{flagged_count:,}", f"{(flagged_count/len(filtered_txns))*100:.2f}% Rate", delta_color="inverse")

st.divider()

# -------------------------------------------------------------
# TABS
# -------------------------------------------------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 Executive Flow & Liquidity",
    "👥 Client 360 & Tiers",
    "👔 Advisor Performance",
    "🛡️ AML & Anomaly Desk",
    "💻 Interactive SQL Queries"
])

# -------------------------------------------------------------
# TAB 1: EXECUTIVE FLOW & LIQUIDITY
# -------------------------------------------------------------
with tab1:
    st.subheader("Monthly Wealth Flow & Net New Money (NNM) Trends")
    monthly_flow = completed_txns.groupby(["month", "flow_type"])["amount"].sum().reset_index()
    
    c_flow = alt.Chart(monthly_flow).mark_bar(opacity=0.85).encode(
        x=alt.X("month:N", title="Month"),
        y=alt.Y("amount:Q", title="Volume (USD)"),
        color=alt.Color("flow_type:N", scale=alt.Scale(domain=["Credit", "Debit", "Variable", "Transfer"], range=["#00875A", "#DE350B", "#0072CE", "#7A869A"])),
        tooltip=["month", "flow_type", alt.Tooltip("amount:Q", format="$,.2f")]
    ).properties(height=380)
    st.altair_chart(c_flow, use_container_width=True)

    col_t1a, col_t1b = st.columns(2)
    with col_t1a:
        st.markdown("#### Regional Branch Volume Share")
        branch_vol = filtered_txns.groupby("branch_name")["amount"].sum().reset_index()
        c_branch = alt.Chart(branch_vol).mark_bar().encode(
            x=alt.X("amount:Q", title="Total Volume (USD)"),
            y=alt.Y("branch_name:N", sort="-x", title="Branch"),
            color=alt.value("#002B49"),
            tooltip=["branch_name", alt.Tooltip("amount:Q", format="$,.2f")]
        ).properties(height=300)
        st.altair_chart(c_branch, use_container_width=True)

    with col_t1b:
        st.markdown("#### Transaction Channel Adoption")
        channel_vol = filtered_txns.groupby("channel")["amount"].count().reset_index().rename(columns={"amount": "txn_count"})
        c_donut = alt.Chart(channel_vol).mark_arc(innerRadius=60).encode(
            theta=alt.Theta("txn_count:Q"),
            color=alt.Color("channel:N"),
            tooltip=["channel", "txn_count"]
        ).properties(height=300)
        st.altair_chart(c_donut, use_container_width=True)

# -------------------------------------------------------------
# TAB 2: CLIENT 360 & WEALTH TIERS
# -------------------------------------------------------------
with tab2:
    st.subheader("Client Relationship Depth & Asset Distribution")
    col_c1, col_c2 = st.columns([1, 2])
    
    with col_c1:
        st.markdown("#### Clients by Wealth Tier")
        tier_counts = customers["wealth_tier"].value_counts().reset_index()
        tier_counts.columns = ["wealth_tier", "count"]
        c_tier = alt.Chart(tier_counts).mark_bar().encode(
            x=alt.X("count:Q"),
            y=alt.Y("wealth_tier:N", sort="-x"),
            color=alt.Color("wealth_tier:N", scale=alt.Scale(scheme="blues")),
            tooltip=["wealth_tier", "count"]
        ).properties(height=260)
        st.altair_chart(c_tier, use_container_width=True)

    with col_c2:
        st.markdown("#### Top 10 High-Value Clients by Lifetime Volume")
        top_clients = filtered_txns.groupby(["customer_code", "first_name", "last_name", "wealth_tier"])["amount"].sum().reset_index()
        top_clients["client_name"] = top_clients["first_name"] + " " + top_clients["last_name"]
        top_clients = top_clients.sort_values(by="amount", ascending=False).head(10)
        
        c_top = alt.Chart(top_clients).mark_bar().encode(
            x=alt.X("amount:Q", title="Total Volume (USD)"),
            y=alt.Y("client_name:N", sort="-x", title="Client"),
            color=alt.Color("wealth_tier:N"),
            tooltip=["client_name", "wealth_tier", alt.Tooltip("amount:Q", format="$,.2f")]
        ).properties(height=260)
        st.altair_chart(c_top, use_container_width=True)

# -------------------------------------------------------------
# TAB 3: ADVISOR PERFORMANCE
# -------------------------------------------------------------
with tab3:
    st.subheader("Financial Advisor Book of Business & Quota Attainment")
    adv_metrics = advisors.merge(customers.groupby("assigned_advisor_id")["customer_id"].count().reset_index().rename(columns={"customer_id": "clients"}), left_on="advisor_id", right_on="assigned_advisor_id", how="left")
    
    # Calculate AUM managed
    cust_aum = accounts.groupby("customer_id")["current_balance"].sum().reset_index()
    cust_adv = customers.merge(cust_aum, on="customer_id", how="left")
    adv_aum = cust_adv.groupby("assigned_advisor_id")["current_balance"].sum().reset_index().rename(columns={"current_balance": "actual_aum"})
    
    adv_metrics = adv_metrics.merge(adv_aum, left_on="advisor_id", right_on="assigned_advisor_id", how="left").fillna(0)
    adv_metrics["attainment_pct"] = (adv_metrics["actual_aum"] / adv_metrics["target_aum"]) * 100
    adv_metrics["advisor_name"] = adv_metrics["first_name"] + " " + adv_metrics["last_name"]

    c_scatter = alt.Chart(adv_metrics).mark_circle(size=120).encode(
        x=alt.X("target_aum:Q", title="Target AUM ($)"),
        y=alt.Y("actual_aum:Q", title="Actual AUM ($)"),
        color=alt.Color("title:N", scale=alt.Scale(scheme="category10")),
        tooltip=["advisor_name", "title", "clients", alt.Tooltip("actual_aum:Q", format="$,.2f"), alt.Tooltip("attainment_pct:Q", format=".1f%")]
    ).properties(height=400)
    st.altair_chart(c_scatter, use_container_width=True)

    st.dataframe(
        adv_metrics[["advisor_code", "advisor_name", "title", "clients", "target_aum", "actual_aum", "attainment_pct"]].sort_values(by="actual_aum", ascending=False).style.format({
            "target_aum": "${:,.0f}",
            "actual_aum": "${:,.0f}",
            "attainment_pct": "{:.1f}%"
        }),
        use_container_width=True
    )

# -------------------------------------------------------------
# TAB 4: AML & ANOMALY SURVEILLANCE
# -------------------------------------------------------------
with tab4:
    st.subheader("Anti-Money Laundering (AML) & Statistical Anomaly Watchlist")
    structuring = filtered_txns[(filtered_txns["amount"] >= 9000) & (filtered_txns["amount"] < 10000) & (filtered_txns["category_id"] == "CAT_DEP")]
    flagged = filtered_txns[filtered_txns["status"] == "Flagged"]
    
    col_w1, col_w2 = st.columns(2)
    col_w1.warning(f"🚨 Structuring / Smurfing Suspects: {len(structuring)} transactions detected just below the $10,000 regulatory reporting threshold.")
    col_w2.error(f"⚠️ High-Risk Flagged Transactions: {len(flagged)} entries pending compliance sign-off.")

    st.markdown("#### High-Risk Surveillance Queue")
    st.dataframe(
        flagged[["transaction_ref", "transaction_time", "customer_code", "wealth_tier", "amount", "channel", "category_name", "status"]].head(25).style.format({
            "amount": "${:,.2f}"
        }),
        use_container_width=True
    )

# -------------------------------------------------------------
# TAB 5: INTERACTIVE SQL SCRIPTS SHOWCASE
# -------------------------------------------------------------
with tab5:
    st.subheader("Production SQL Showcase (from /sql/04_business_queries.sql)")
    st.markdown("These production queries demonstrate mastery of **CTEs**, **Window Functions (`LAG`, `DENSE_RANK`, `AVG OVER`)**, and **ACID Stored Procedures**:")

    q_choice = st.selectbox(
        "Select Business Question to inspect SQL:",
        [
            "1. Top 10 Customers by Volume (DENSE_RANK)",
            "2. Monthly Trends & MoM Growth (LAG)",
            "3. Regional Branch Volume & Contribution % (SUM OVER)",
            "4. Declining Activity / Churn Warning (Windowed CTE)",
            "5. AML Anomaly Detection (Statistical Outlier & Structuring)"
        ]
    )

    if "1. Top 10" in q_choice:
        st.code("""
WITH customer_volume_ranked AS (
    SELECT 
        c.customer_id, c.customer_code,
        CONCAT(c.first_name, ' ', c.last_name) AS customer_name,
        c.wealth_tier, b.branch_name,
        COUNT(t.transaction_id) AS total_transactions,
        SUM(t.amount) AS total_volume_usd,
        DENSE_RANK() OVER (ORDER BY SUM(t.amount) DESC) AS volume_rank
    FROM customers c
    JOIN accounts a ON c.customer_id = a.customer_id
    JOIN transactions t ON a.account_id = t.account_id
    JOIN branches b ON c.home_branch_id = b.branch_id
    WHERE t.status = 'Completed'
    GROUP BY c.customer_id, c.customer_code, c.first_name, c.last_name, c.wealth_tier, b.branch_name
)
SELECT * FROM customer_volume_ranked WHERE volume_rank <= 10;
        """, language="sql")
    elif "2. Monthly Trends" in q_choice:
        st.code("""
WITH monthly_metrics AS (
    SELECT 
        DATE_FORMAT(t.transaction_time, '%Y-%m') AS txn_month,
        COUNT(t.transaction_id) AS monthly_txn_count,
        SUM(t.amount) AS monthly_volume_usd
    FROM transactions t
    WHERE t.status = 'Completed'
    GROUP BY DATE_FORMAT(t.transaction_time, '%Y-%m')
)
SELECT 
    txn_month, monthly_txn_count,
    ROUND(((monthly_txn_count - LAG(monthly_txn_count, 1) OVER (ORDER BY txn_month)) 
          / NULLIF(LAG(monthly_txn_count, 1) OVER (ORDER BY txn_month), 0)) * 100, 2) AS mom_count_growth_pct,
    monthly_volume_usd,
    ROUND(((monthly_volume_usd - LAG(monthly_volume_usd, 1) OVER (ORDER BY txn_month)) 
          / NULLIF(LAG(monthly_volume_usd, 1) OVER (ORDER BY txn_month), 0)) * 100, 2) AS mom_volume_growth_pct
FROM monthly_metrics
ORDER BY txn_month DESC;
        """, language="sql")
    elif "3. Regional Branch" in q_choice:
        st.code("""
SELECT 
    b.branch_name, b.city, b.region,
    COUNT(t.transaction_id) AS branch_txn_count,
    ROUND((COUNT(t.transaction_id) / SUM(COUNT(t.transaction_id)) OVER()) * 100, 2) AS pct_of_firm_txns,
    SUM(t.amount) AS branch_volume_usd,
    ROUND((SUM(t.amount) / SUM(SUM(t.amount)) OVER()) * 100, 2) AS pct_of_firm_volume
FROM branches b
JOIN accounts a ON b.branch_id = a.branch_id
JOIN transactions t ON a.account_id = t.account_id
WHERE t.status = 'Completed'
GROUP BY b.branch_name, b.city, b.region
ORDER BY branch_volume_usd DESC;
        """, language="sql")
    elif "4. Declining Activity" in q_choice:
        st.code("""
WITH period_activity AS (
    SELECT 
        c.customer_code, CONCAT(c.first_name, ' ', c.last_name) AS customer_name,
        c.wealth_tier,
        SUM(CASE WHEN t.transaction_time >= DATE_SUB('2026-02-28', INTERVAL 180 DAY)
                  AND t.transaction_time < DATE_SUB('2026-02-28', INTERVAL 90 DAY) THEN 1 ELSE 0 END) AS prior_period_txns,
        SUM(CASE WHEN t.transaction_time >= DATE_SUB('2026-02-28', INTERVAL 90 DAY) THEN 1 ELSE 0 END) AS recent_period_txns
    FROM customers c
    JOIN accounts a ON c.customer_id = a.customer_id
    JOIN transactions t ON a.account_id = t.account_id AND t.status = 'Completed'
    GROUP BY c.customer_code, c.first_name, c.last_name, c.wealth_tier
)
SELECT *,
    ROUND(((recent_period_txns - prior_period_txns) / NULLIF(prior_period_txns, 0)) * 100, 2) AS activity_change_pct
FROM period_activity
WHERE prior_period_txns >= 3 AND recent_period_txns < (prior_period_txns * 0.4)
ORDER BY activity_change_pct ASC;
        """, language="sql")
    else:
        st.code("""
SELECT 
    t.transaction_ref, t.transaction_time, c.customer_code, t.amount,
    CASE 
        WHEN t.amount BETWEEN 9000.00 AND 9999.99 AND tc.category_id = 'CAT_DEP' THEN 'Potential Structuring / Smurfing'
        WHEN t.amount > (ahs.historical_avg * 4.0) THEN 'Outlier Spike (>4x Average)'
        ELSE 'Normal'
    END AS anomaly_flag
FROM transactions t
JOIN accounts a ON t.account_id = a.account_id
JOIN customers c ON a.customer_id = c.customer_id
JOIN transaction_categories tc ON t.category_id = tc.category_id
JOIN (SELECT account_id, AVG(amount) AS historical_avg FROM transactions WHERE status = 'Completed' GROUP BY account_id) ahs
  ON t.account_id = ahs.account_id
WHERE (t.amount BETWEEN 9000.00 AND 9999.99 AND tc.category_id = 'CAT_DEP')
   OR t.amount > (ahs.historical_avg * 4.0);
        """, language="sql")

st.markdown("---")
st.caption("Built for Morgan Stanley Wealth Management 2027 Apprenticeship Program | Home Office Mumbai")
