# Power BI DAX Measures Library
### Project: Morgan Stanley Wealth Management & Transaction Intelligence

This document contains production-grade DAX measures formatted and ready to copy-paste into Power BI Desktop.

---

## 1. Executive Wealth & AUM (Assets Under Management)

### Total AUM (Firmwide Relationship Balance)
```dax
Total AUM = 
SUM('accounts'[current_balance])
```

### Total Inflow (Capital Additions)
```dax
Total Inflow = 
CALCULATE(
    SUM('transactions'[amount]),
    'transaction_categories'[flow_type] = "Credit",
    'transactions'[status] = "Completed"
)
```

### Total Outflow (Capital Withdrawals)
```dax
Total Outflow = 
CALCULATE(
    SUM('transactions'[amount]),
    'transaction_categories'[flow_type] = "Debit",
    'transactions'[status] = "Completed"
)
```

### Net New Money (NNM / Net Inflows)
*Morgan Stanley's primary organic growth metric reported on earnings calls.*
```dax
Net New Money = 
[Total Inflow] - [Total Outflow]
```

### Inflow to Outflow Ratio
```dax
Inflow-to-Outflow Ratio = 
DIVIDE([Total Inflow], [Total Outflow], 0)
```

---

## 2. Customer & Wealth Tier Metrics

### Total Active Clients
```dax
Active Clients = 
CALCULATE(
    DISTINCTCOUNT('customers'[customer_id]),
    'customers'[status] = "Active"
)
```

### High-Net-Worth (HNW & UHNW) Client Count
```dax
HNW & UHNW Clients = 
CALCULATE(
    DISTINCTCOUNT('customers'[customer_id]),
    'customers'[wealth_tier] IN {"High-Net-Worth (HNW)", "Ultra-HNW (UHNW)"}
)
```

### HNW Client Share %
```dax
HNW Client Share % = 
DIVIDE([HNW & UHNW Clients], [Active Clients], 0)
```

### Average AUM per Client
```dax
Avg AUM per Client = 
DIVIDE([Total AUM], [Active Clients], 0)
```

### Churn Risk Client Count
```dax
Churn Risk Clients = 
CALCULATE(
    DISTINCTCOUNT('customers'[customer_id]),
    'customers'[status] = "Dormant"
)
```

---

## 3. Transaction & Channel Velocity

### Total Transaction Volume (USD)
```dax
Total Transaction Volume = 
CALCULATE(
    SUM('transactions'[amount]),
    'transactions'[status] = "Completed"
)
```

### Total Transaction Count
```dax
Total Transaction Count = 
COUNTROWS('transactions')
```

### Average Ticket Size (Avg Transaction Value)
```dax
Avg Transaction Ticket = 
DIVIDE([Total Transaction Volume], CALCULATE(COUNTROWS('transactions'), 'transactions'[status] = "Completed"), 0)
```

### Digital Channel Adoption %
*Tracks transactions through Online Portal & Mobile App vs Branch/Wire Desk.*
```dax
Digital Adoption % = 
VAR DigitalTxns = 
    CALCULATE(
        COUNTROWS('transactions'),
        'transactions'[channel] IN {"Wealth Online Portal", "Mobile App"}
    )
RETURN
    DIVIDE(DigitalTxns, [Total Transaction Count], 0)
```

---

## 4. Advisory Fees & Revenue

### Total Advisory & Custody Fees Collected
```dax
Advisory Fee Revenue = 
CALCULATE(
    SUM('transactions'[amount]),
    'transaction_categories'[is_fee] = TRUE(),
    'transactions'[status] = "Completed"
)
```

### Fee Yield on AUM (Annualized Basis Points)
```dax
Fee Yield (bps) = 
DIVIDE([Advisory Fee Revenue], [Total AUM], 0) * 10000
```

---

## 5. Compliance, AML & Risk Metrics

### Flagged Transaction Count
```dax
Flagged Transactions = 
CALCULATE(
    COUNTROWS('transactions'),
    'transactions'[status] = "Flagged"
)
```

### Compliance Exception Rate %
```dax
Compliance Exception Rate % = 
DIVIDE([Flagged Transactions], [Total Transaction Count], 0)
```

### Potential Structuring Volume ($9k - $10k Threshold)
```dax
Structuring Suspect Volume = 
CALCULATE(
    SUM('transactions'[amount]),
    'transactions'[amount] >= 9000 && 'transactions'[amount] < 10000,
    'transaction_categories'[category_id] = "CAT_DEP"
)
```

---

## 6. Time Intelligence (MoM Trends)

### Month-over-Month (MoM) Net New Money %
```dax
NNM MoM Growth % = 
VAR CurrentMonthNNM = [Net New Money]
VAR PriorMonthNNM = 
    CALCULATE(
        [Net New Money],
        DATEADD('Dim_Date'[Date], -1, MONTH)
    )
RETURN
    DIVIDE(CurrentMonthNNM - PriorMonthNNM, ABS(PriorMonthNNM), 0)
```
