"""
Generate synthetic monthly budget vs. actuals data for a fictional
mid-size company with 5 business units, across 18 months.

Line items (standard P&L, kept simple and defensible):
- Revenue
- COGS
- Opex: Marketing
- Opex: Salaries
- Opex: Other
- Headcount Cost

Output: budget_vs_actuals.csv
Columns: business_unit, line_item, month, budget, actual
"""

import numpy as np
import pandas as pd
from datetime import date
from dateutil.relativedelta import relativedelta

np.random.seed(42)

BUSINESS_UNITS = [
    "Retail Sales",
    "Digital Products",
    "Enterprise Services",
    "Logistics",
    "Customer Support",
]

LINE_ITEMS = {
    # line_item: (base_monthly_budget, budget_growth_rate_monthly, actual_noise_std, drift_bias)
    "Revenue":            (500_000, 0.010,  0.06,  0.00),
    "COGS":               (220_000, 0.008,  0.05,  0.00),
    "Opex: Marketing":    ( 60_000, 0.005,  0.15,  0.02),   # noisier, more prone to overspend
    "Opex: Salaries":     (150_000, 0.004,  0.03, -0.01),   # steady, slight underspend (attrition)
    "Opex: Other":        ( 25_000, 0.003,  0.10,  0.01),
    "Headcount Cost":     ( 90_000, 0.006,  0.04,  0.00),
}

N_MONTHS = 18
START_MONTH = date(2025, 4, 1)  # gives us through Sep 2026, "today"

# Each BU gets its own scale factor and a couple of "event months" where
# actuals diverge sharply from budget (simulates real one-off events —
# a campaign overspend, a hiring freeze, a client ramp-down, etc.)
BU_SCALE = {
    "Retail Sales": 1.30,
    "Digital Products": 0.85,
    "Enterprise Services": 1.10,
    "Logistics": 0.70,
    "Customer Support": 0.55,
}

EVENT_MONTHS = {
    # (business_unit, line_item): {month_index: multiplier_on_actual}
    ("Retail Sales", "Opex: Marketing"): {7: 1.45, 14: 1.30},        # campaign overspend
    ("Digital Products", "Revenue"): {10: 0.80},                     # product delay
    ("Logistics", "Opex: Other"): {5: 1.60},                         # fuel cost spike
    ("Enterprise Services", "Headcount Cost"): {12: 0.75},           # planned freeze
    ("Customer Support", "Opex: Salaries"): {9: 1.25},               # overtime surge
}

def month_range(start, n):
    return [start + relativedelta(months=i) for i in range(n)]

def generate():
    months = month_range(START_MONTH, N_MONTHS)
    rows = []

    for bu in BUSINESS_UNITS:
        scale = BU_SCALE[bu]
        for line_item, (base, growth, noise_std, drift) in LINE_ITEMS.items():
            for i, m in enumerate(months):
                budget = base * scale * ((1 + growth) ** i)

                # Actual = budget + systematic drift + random noise
                noise = np.random.normal(loc=drift, scale=noise_std)
                actual = budget * (1 + noise)

                # Apply any scripted one-off event for this BU/line_item/month
                event_mult = EVENT_MONTHS.get((bu, line_item), {}).get(i)
                if event_mult is not None:
                    actual = budget * event_mult

                rows.append({
                    "business_unit": bu,
                    "line_item": line_item,
                    "month": m.strftime("%Y-%m"),
                    "budget": round(budget, 2),
                    "actual": round(actual, 2),
                })

    df = pd.DataFrame(rows)
    df.sort_values(["business_unit", "line_item", "month"], inplace=True)
    return df.reset_index(drop=True)

if __name__ == "__main__":
    df = generate()
    out_path = "budget_vs_actuals.csv"
    df.to_csv(out_path, index=False)
    print(f"Wrote {len(df)} rows to {out_path}")
    print(df.head(12).to_string(index=False))
