"""
Simulates a lightweight analyst-maintained "event log" — the kind of
thing a real FP&A team keeps informally (a shared doc, a tag in the
planning system) noting known one-off drivers as they happen.

The commentary generator looks up flagged rows against this log. Where
a tag exists, it's used directly. Where it doesn't, the tool does NOT
guess — it drafts an objective description and marks the driver as
pending analyst input. This mirrors how these tools should actually
behave: automate the mechanical description, defer judgment on cause.
"""

import pandas as pd

EVENT_LOG = [
    {"business_unit": "Retail Sales", "line_item": "Opex: Marketing", "month": "2025-11",
     "driver": "Q4 campaign spend pulled forward ahead of holiday promotion"},
    {"business_unit": "Retail Sales", "line_item": "Opex: Marketing", "month": "2026-06",
     "driver": "mid-year brand campaign overspend, approved as one-off by marketing lead"},
    {"business_unit": "Digital Products", "line_item": "Revenue", "month": "2026-02",
     "driver": "product launch delayed to next quarter, revenue recognition pushed out"},
    {"business_unit": "Logistics", "line_item": "Opex: Other", "month": "2025-09",
     "driver": "fuel cost spike, regional supplier surcharge"},
    {"business_unit": "Enterprise Services", "line_item": "Headcount Cost", "month": "2026-04",
     "driver": "planned hiring freeze on two open reqs, deferred to next fiscal year"},
    {"business_unit": "Customer Support", "line_item": "Opex: Salaries", "month": "2026-01",
     "driver": "overtime surge covering holiday-period ticket volume"},
]

def load_event_log() -> pd.DataFrame:
    return pd.DataFrame(EVENT_LOG)
