import os
import random
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from faker import Faker

fake = Faker()
Faker.seed(42)
random.seed(42)
np.random.seed(42)

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
os.makedirs(DATA_DIR, exist_ok=True)

print("🚀 Starting Synthetic Banking & Wealth Management Data Generation...")

# -------------------------------------------------------------
# 1. BRANCHES (Wealth Management Hubs)
# -------------------------------------------------------------
branches_data = [
    {"branch_id": 1, "branch_code": "B-MUM-01", "branch_name": "Mumbai - Bandra Kurla Complex (BKC)", "city": "Mumbai", "country": "India", "region": "APAC", "head_advisor": "Vikram Malhotra", "opened_year": 2008},
    {"branch_id": 2, "branch_code": "B-MUM-02", "branch_name": "Mumbai - Nariman Point", "city": "Mumbai", "country": "India", "region": "APAC", "head_advisor": "Pooja Singhania", "opened_year": 2012},
    {"branch_id": 3, "branch_code": "B-BLR-01", "branch_name": "Bengaluru - Outer Ring Road", "city": "Bengaluru", "country": "India", "region": "APAC", "head_advisor": "Rohan Deshmukh", "opened_year": 2015},
    {"branch_id": 4, "branch_code": "B-NYC-01", "branch_name": "New York - Park Avenue Private Wealth", "city": "New York", "country": "USA", "region": "Americas", "head_advisor": "Eleanor Vance", "opened_year": 1998},
    {"branch_id": 5, "branch_code": "B-NYC-02", "branch_name": "New York - Broadway Center", "city": "New York", "country": "USA", "region": "Americas", "head_advisor": "Marcus Sterling", "opened_year": 2004},
    {"branch_id": 6, "branch_code": "B-LON-01", "branch_name": "London - Canary Wharf", "city": "London", "country": "UK", "region": "EMEA", "head_advisor": "Alistair Campbell", "opened_year": 2001},
    {"branch_id": 7, "branch_code": "B-SGP-01", "branch_name": "Singapore - Marina Bay Financial Centre", "city": "Singapore", "country": "Singapore", "region": "APAC", "head_advisor": "Serene Lim", "opened_year": 2010},
    {"branch_id": 8, "branch_code": "B-HKG-01", "branch_name": "Hong Kong - Two IFC Central", "city": "Hong Kong", "country": "Hong Kong", "region": "APAC", "head_advisor": "David Wong", "opened_year": 2006},
]
df_branches = pd.DataFrame(branches_data)
df_branches.to_csv(os.path.join(DATA_DIR, "branches.csv"), index=False)
print(f" Saved {len(df_branches)} branches.")

# -------------------------------------------------------------
# 2. ADVISORS (Wealth Managers & Relationship Managers)
# -------------------------------------------------------------
advisor_titles = ["Associate Advisor", "Vice President - Wealth", "Senior Vice President", "Executive Director"]
advisors_list = []
advisor_id = 1

for _, branch in df_branches.iterrows():
    # 3 to 4 advisors per branch
    num_adv = random.randint(3, 4)
    for _ in range(num_adv):
        title = random.choices(advisor_titles, weights=[0.25, 0.40, 0.25, 0.10])[0]
        target_aum = {
            "Associate Advisor": random.randint(15_000_000, 35_000_000),
            "Vice President - Wealth": random.randint(40_000_000, 80_000_000),
            "Senior Vice President": random.randint(85_000_000, 160_000_000),
            "Executive Director": random.randint(170_000_000, 300_000_000),
        }[title]

        advisors_list.append({
            "advisor_id": advisor_id,
            "advisor_code": f"ADV-{advisor_id:04d}",
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "email": f"advisor.{advisor_id}@morganstanley.internal",
            "phone": fake.phone_number(),
            "branch_id": branch["branch_id"],
            "title": title,
            "target_aum": target_aum,
            "hire_date": fake.date_between(start_date="-10y", end_date="-1y"),
            "status": "Active"
        })
        advisor_id += 1

df_advisors = pd.DataFrame(advisors_list)
df_advisors.to_csv(os.path.join(DATA_DIR, "advisors.csv"), index=False)
print(f" Saved {len(df_advisors)} advisors.")

# -------------------------------------------------------------
# 3. ACCOUNT TYPES
# -------------------------------------------------------------
account_types_data = [
    {"type_id": "ACC_CHK", "type_name": "Private Wealth Checking", "category": "Transactional", "min_balance": 5000.0, "interest_rate": 0.005},
    {"type_id": "ACC_SAV", "type_name": "High-Yield Wealth Savings", "category": "Deposit", "min_balance": 25000.0, "interest_rate": 0.042},
    {"type_id": "ACC_BRK", "type_name": "Brokerage & Equity Portfolio", "category": "Investment", "min_balance": 50000.0, "interest_rate": 0.0},
    {"type_id": "ACC_TRS", "type_name": "Trust & Estate Preservation", "category": "Fiduciary", "min_balance": 200000.0, "interest_rate": 0.025},
    {"type_id": "ACC_RET", "type_name": "Retirement & IRA Account", "category": "Retirement", "min_balance": 10000.0, "interest_rate": 0.038},
]
df_account_types = pd.DataFrame(account_types_data)
df_account_types.to_csv(os.path.join(DATA_DIR, "account_types.csv"), index=False)
print(f" Saved {len(df_account_types)} account types.")

# -------------------------------------------------------------
# 4. TRANSACTION CATEGORIES
# -------------------------------------------------------------
transaction_categories_data = [
    {"category_id": "CAT_DEP", "category_name": "Wire / Capital Inflow", "flow_type": "Credit", "is_fee": False, "description": "Client deposit or external wire transfer inflow"},
    {"category_id": "CAT_WTH", "category_name": "Withdrawal / Capital Outflow", "flow_type": "Debit", "is_fee": False, "description": "Cash withdrawal or outgoing wire transfer"},
    {"category_id": "CAT_TRD", "category_name": "Securities Trade (Equity/Bonds)", "flow_type": "Variable", "is_fee": False, "description": "Purchase or sale of market securities"},
    {"category_id": "CAT_DIV", "category_name": "Dividend & Yield Credit", "flow_type": "Credit", "is_fee": False, "description": "Passive income and coupon payments"},
    {"category_id": "CAT_FEE", "category_name": "Advisory & Custody Fee", "flow_type": "Debit", "is_fee": True, "description": "Quarterly management and custodial charge"},
    {"category_id": "CAT_TRF", "category_name": "Internal Portfolio Rebalance", "flow_type": "Transfer", "is_fee": False, "description": "Transfer between linked customer accounts"},
]
df_transaction_categories = pd.DataFrame(transaction_categories_data)
df_transaction_categories.to_csv(os.path.join(DATA_DIR, "transaction_categories.csv"), index=False)
print(f" Saved {len(df_transaction_categories)} transaction categories.")

# -------------------------------------------------------------
# 5. CUSTOMERS (1,000 across Wealth Tiers)
# -------------------------------------------------------------
wealth_tiers = ["Retail", "Mass Affluent", "High-Net-Worth (HNW)", "Ultra-HNW (UHNW)"]
tier_weights = [0.45, 0.35, 0.16, 0.04]  # Realistic pyramid distribution
risk_profiles = ["Conservative", "Moderate", "Growth", "Aggressive"]
risk_weights = [0.25, 0.45, 0.20, 0.10]

customers_list = []
start_onboarding = datetime(2021, 1, 1)

for cid in range(1, 1001):
    tier = random.choices(wealth_tiers, weights=tier_weights)[0]
    risk = random.choices(risk_profiles, weights=risk_weights)[0]
    advisor = random.choice(advisors_list)
    branch_id = advisor["branch_id"]

    # Days since onboarding
    onboard_days = random.randint(0, 1500)
    onboard_date = start_onboarding + timedelta(days=onboard_days)

    customers_list.append({
        "customer_id": cid,
        "customer_code": f"CUST-{cid:06d}",
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
        "email": fake.email(),
        "phone": fake.phone_number(),
        "date_of_birth": fake.date_of_birth(minimum_age=24, maximum_age=78),
        "wealth_tier": tier,
        "risk_profile": risk,
        "home_branch_id": branch_id,
        "assigned_advisor_id": advisor["advisor_id"],
        "kyc_status": random.choices(["Verified", "Pending Review", "Exempt"], weights=[0.96, 0.03, 0.01])[0],
        "onboarding_date": onboard_date.strftime("%Y-%m-%d"),
        "annual_income": {
            "Retail": random.randint(45_000, 110_000),
            "Mass Affluent": random.randint(120_000, 300_000),
            "High-Net-Worth (HNW)": random.randint(350_000, 1_200_000),
            "Ultra-HNW (UHNW)": random.randint(1_500_000, 10_000_000),
        }[tier],
        "status": random.choices(["Active", "Inactive", "Dormant"], weights=[0.92, 0.05, 0.03])[0]
    })

df_customers = pd.DataFrame(customers_list)
df_customers.to_csv(os.path.join(DATA_DIR, "customers.csv"), index=False)
print(f" Saved {len(df_customers)} customers.")

# -------------------------------------------------------------
# 6. BANK ACCOUNTS
# -------------------------------------------------------------
accounts_list = []
account_id = 1

for cust in customers_list:
    tier = cust["wealth_tier"]
    cid = cust["customer_id"]
    
    # Decide how many accounts this customer holds
    if tier == "Retail":
        types = ["ACC_CHK"] if random.random() < 0.4 else ["ACC_CHK", "ACC_SAV"]
    elif tier == "Mass Affluent":
        types = ["ACC_CHK", "ACC_SAV", "ACC_BRK"] if random.random() < 0.6 else ["ACC_CHK", "ACC_BRK"]
    elif tier == "High-Net-Worth (HNW)":
        types = ["ACC_CHK", "ACC_SAV", "ACC_BRK", "ACC_RET"] if random.random() < 0.5 else ["ACC_CHK", "ACC_SAV", "ACC_BRK"]
    else:  # Ultra-HNW
        types = ["ACC_CHK", "ACC_SAV", "ACC_BRK", "ACC_TRS", "ACC_RET"]

    for atype in types:
        # Base balance according to tier and type
        if tier == "Retail":
            bal = random.uniform(2_000, 35_000)
        elif tier == "Mass Affluent":
            bal = random.uniform(35_000, 220_000)
        elif tier == "High-Net-Worth (HNW)":
            bal = random.uniform(250_000, 1_500_000)
        else:
            bal = random.uniform(1_800_000, 12_000_000)

        # Scale down checking, scale up brokerage/trust
        if atype == "ACC_CHK":
            bal *= 0.25
        elif atype == "ACC_BRK":
            bal *= 1.8
        elif atype == "ACC_TRS":
            bal *= 2.2

        open_date = datetime.strptime(cust["onboarding_date"], "%Y-%m-%d") + timedelta(days=random.randint(0, 30))

        accounts_list.append({
            "account_id": account_id,
            "account_number": f"MS-{random.randint(1000,9999)}-{account_id:06d}",
            "customer_id": cid,
            "account_type_id": atype,
            "branch_id": cust["home_branch_id"],
            "current_balance": round(bal, 2),
            "currency": "USD",
            "opened_date": open_date.strftime("%Y-%m-%d"),
            "status": "Dormant" if cust["status"] == "Dormant" else random.choices(["Active", "Suspended"], weights=[0.97, 0.03])[0]
        })
        account_id += 1

df_accounts = pd.DataFrame(accounts_list)
df_accounts.to_csv(os.path.join(DATA_DIR, "accounts.csv"), index=False)
print(f" Saved {len(df_accounts)} accounts.")

# -------------------------------------------------------------
# 7. TRANSACTIONS (25,000+ records spanning 2024-2026)
# -------------------------------------------------------------
channels = ["Wealth Online Portal", "Advisor Desk", "Wire Desk", "Mobile App", "ATM"]
txn_statuses = ["Completed", "Flagged", "Pending", "Failed"]

transactions_list = []
txn_id = 1
start_txn_date = datetime(2024, 1, 1)
end_txn_date = datetime(2026, 2, 28)
total_days = (end_txn_date - start_txn_date).days

# Map accounts to their customer tier
account_tier_map = {}
for acc in accounts_list:
    cust = next(c for c in customers_list if c["customer_id"] == acc["customer_id"])
    account_tier_map[acc["account_id"]] = {
        "tier": cust["wealth_tier"],
        "open_date": datetime.strptime(acc["opened_date"], "%Y-%m-%d"),
        "customer_id": cust["customer_id"],
        "branch_id": acc["branch_id"],
        "account_type": acc["account_type_id"]
    }

active_accounts = [acc for acc in accounts_list if acc["status"] == "Active"]

# Target 26,000 transactions
TOTAL_TRANSACTIONS = 26_000

for i in range(TOTAL_TRANSACTIONS):
    acc = random.choice(active_accounts)
    acc_meta = account_tier_map[acc["account_id"]]
    tier = acc_meta["tier"]

    # Transaction date between account open date and end_txn_date
    open_dt = acc_meta["open_date"]
    if open_dt >= end_txn_date:
        txn_date = end_txn_date - timedelta(days=random.randint(1, 30))
    else:
        diff_days = (end_txn_date - open_dt).days
        txn_date = open_dt + timedelta(days=random.randint(0, max(1, diff_days)), seconds=random.randint(0, 86399))

    # Pick category based on account type
    if acc_meta["account_type"] == "ACC_BRK":
        cat_weights = [0.15, 0.10, 0.50, 0.15, 0.08, 0.02]
    elif acc_meta["account_type"] == "ACC_CHK":
        cat_weights = [0.35, 0.45, 0.02, 0.01, 0.02, 0.15]
    else:
        cat_weights = [0.30, 0.20, 0.20, 0.15, 0.05, 0.10]
        
    cat = random.choices(df_transaction_categories["category_id"].tolist(), weights=cat_weights)[0]

    # Amount distribution based on tier
    if tier == "Retail":
        amt = abs(np.random.normal(loc=1_200, scale=1_500)) + 50
    elif tier == "Mass Affluent":
        amt = abs(np.random.normal(loc=8_500, scale=7_000)) + 200
    elif tier == "High-Net-Worth (HNW)":
        amt = abs(np.random.normal(loc=45_000, scale=35_000)) + 1_000
    else:  # UHNW
        amt = abs(np.random.normal(loc=250_000, scale=180_000)) + 10_000

    amt = round(amt, 2)

    # Status & Channel
    channel = random.choices(channels, weights=[0.45, 0.25, 0.15, 0.12, 0.03])[0]
    status = random.choices(txn_statuses, weights=[0.97, 0.015, 0.01, 0.005])[0]

    # Deliberate Anomaly Injections for Business Queries:
    # Anomaly 1: Structuring / Smurfing (Amounts between 9000 and 9999.99 to evade 10K reporting)
    if i % 180 == 0:
        amt = round(random.uniform(9_100, 9_950), 2)
        cat = "CAT_DEP"
        channel = "Wire Desk"
        status = "Flagged"

    # Anomaly 2: Extreme spike (>10x normal)
    if i % 400 == 0:
        amt = round(amt * 12.5, 2)
        status = "Flagged"

    transactions_list.append({
        "transaction_id": txn_id,
        "transaction_ref": f"TXN-{txn_date.strftime('%Y%m%d')}-{txn_id:07d}",
        "account_id": acc["account_id"],
        "category_id": cat,
        "amount": amt,
        "transaction_time": txn_date.strftime("%Y-%m-%d %H:%M:%S"),
        "channel": channel,
        "status": status,
        "description": f"{cat} processed via {channel}"
    })
    txn_id += 1

# Sort transactions by time
transactions_list.sort(key=lambda x: x["transaction_time"])
df_transactions = pd.DataFrame(transactions_list)
df_transactions.to_csv(os.path.join(DATA_DIR, "transactions.csv"), index=False)
print(f" Saved {len(df_transactions)} transactions.")

print("\n Synthetic Data Generation Complete! Files stored in /data directory.")
