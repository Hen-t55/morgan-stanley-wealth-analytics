import os
import sys
import re
import getpass
import pandas as pd
import mysql.connector

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
SQL_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "sql")

def clean_sql(content):
    """Strip SQL comments while preserving active SQL statements."""
    # Remove block comments /* ... */
    content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
    # Remove single line comments starting with -- or #
    lines = []
    for line in content.splitlines():
        trimmed = line.strip()
        if not trimmed.startswith("--") and not trimmed.startswith("#"):
            lines.append(line)
    return "\n".join(lines)

def run_ddl_or_views(cursor, filepath):
    print(f" Executing {os.path.basename(filepath)}...")
    with open(filepath, "r", encoding="utf-8") as f:
        content = clean_sql(f.read())

    # Split by semicolon
    statements = [s.strip() for s in content.split(";") if s.strip()]
    for stmt in statements:
        try:
            cursor.execute(stmt)
        except mysql.connector.Error as err:
            # Ignore harmless drop warnings
            if "Unknown table" in str(err) or "Unknown view" in str(err):
                continue
            print(f"  ⚠️ Statement notice: {err}")

def run_stored_procedures(cursor, filepath):
    print(f" Executing {os.path.basename(filepath)}...")
    with open(filepath, "r", encoding="utf-8") as f:
        raw = clean_sql(f.read())

    # Split on $$ delimiter used in procedure definition file
    chunks = raw.split("$$")
    for chunk in chunks:
        # Filter out DELIMITER command lines which are MySQL CLI specific
        lines = [l for l in chunk.splitlines() if not l.strip().lower().startswith("delimiter")]
        clean_stmt = "\n".join(lines).strip()
        if not clean_stmt:
            continue
        # Split on semicolon if there are pre-procedure statements (like USE or DROP)
        sub_stmts = [s.strip() for s in clean_stmt.split(";") if s.strip()]
        for stmt in sub_stmts:
            try:
                cursor.execute(stmt)
            except mysql.connector.Error as err:
                if "does not exist" in str(err):
                    continue
                print(f"  ⚠️ Procedure notice: {err}")

def main():
    print("=" * 70)
    print("Morgan Stanley Wealth Management - MySQL Database Loader")
    print("=" * 70)

    host = input("Enter MySQL Host [default: localhost]: ").strip() or "localhost"
    port = input("Enter MySQL Port [default: 3306]: ").strip() or "3306"
    user = input("Enter MySQL User [default: root]: ").strip() or "root"
    password = getpass.getpass("Enter MySQL Password (press Enter if none): ")

    try:
        conn = mysql.connector.connect(
            host=host,
            port=int(port),
            user=user,
            password=password,
            allow_local_infile=True
        )
        cursor = conn.cursor()
        print(" Connected to MySQL successfully!\n")
    except mysql.connector.Error as err:
        print(f"❌ Connection failed: {err}")
        sys.exit(1)

    # 1. Ensure target database exists and select it
    print(" Initializing database `morgan_stanley_wm`...")
    cursor.execute("CREATE DATABASE IF NOT EXISTS morgan_stanley_wm;")
    cursor.execute("USE morgan_stanley_wm;")
    conn.commit()

    # 2. Execute DDL Schema (Tables, Constraints, Indexes)
    run_ddl_or_views(cursor, os.path.join(SQL_DIR, "01_schema_ddl.sql"))
    conn.commit()

    # 3. Ingest CSV Data
    csv_table_map = [
        ("branches.csv", "branches", ["branch_id", "branch_code", "branch_name", "city", "country", "region", "head_advisor", "opened_year"]),
        ("advisors.csv", "advisors", ["advisor_id", "advisor_code", "first_name", "last_name", "email", "phone", "branch_id", "title", "target_aum", "hire_date", "status"]),
        ("account_types.csv", "account_types", ["type_id", "type_name", "category", "min_balance", "interest_rate"]),
        ("transaction_categories.csv", "transaction_categories", ["category_id", "category_name", "flow_type", "is_fee", "description"]),
        ("customers.csv", "customers", ["customer_id", "customer_code", "first_name", "last_name", "email", "phone", "date_of_birth", "wealth_tier", "risk_profile", "home_branch_id", "assigned_advisor_id", "kyc_status", "onboarding_date", "annual_income", "status"]),
        ("accounts.csv", "accounts", ["account_id", "account_number", "customer_id", "account_type_id", "branch_id", "current_balance", "currency", "opened_date", "status"]),
        ("transactions.csv", "transactions", ["transaction_id", "transaction_ref", "account_id", "category_id", "amount", "transaction_time", "channel", "status", "description"])
    ]

    for filename, table_name, columns in csv_table_map:
        csv_path = os.path.join(DATA_DIR, filename)
        if not os.path.exists(csv_path):
            print(f"❌ Missing data file: {csv_path}")
            continue

        df = pd.read_csv(csv_path)
        # Replace NaN with None for SQL NULL
        df = df.where(pd.notnull(df), None)

        cols_str = ", ".join(columns)
        placeholders = ", ".join(["%s"] * len(columns))
        insert_query = f"INSERT INTO {table_name} ({cols_str}) VALUES ({placeholders})"

        data_tuples = [tuple(x) for x in df[columns].values]

        print(f" Ingesting {len(data_tuples):,} rows into `{table_name}`...")
        batch_size = 5000
        for i in range(0, len(data_tuples), batch_size):
            batch = data_tuples[i:i + batch_size]
            cursor.executemany(insert_query, batch)
        conn.commit()
        print(f"  Successfully loaded `{table_name}`.")

    # 4. Execute Views & Stored Procedures
    run_ddl_or_views(cursor, os.path.join(SQL_DIR, "02_views.sql"))
    conn.commit()

    run_stored_procedures(cursor, os.path.join(SQL_DIR, "03_stored_procedures.sql"))
    conn.commit()

    cursor.close()
    conn.close()

    print("\n" + "=" * 70)
    print(" SUCCESS: Database `morgan_stanley_wm` is fully provisioned & loaded!")
    print(" You can now run queries in MySQL Workbench or connect Power BI Desktop.")
    print("=" * 70 + "\n")

if __name__ == "__main__":
    main()
