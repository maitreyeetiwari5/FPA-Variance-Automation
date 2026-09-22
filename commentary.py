"""
Auto-drafts variance commentary for flagged rows.

For each flagged row:
  1. Look up (business_unit, line_item, month) in the event log.
  2. If a known driver exists, produce a commentary line that states the
     variance AND the driver, ready for an analyst to review and send.
  3. If no known driver exists, produce an objective description of the
     variance only, and mark it "Driver: pending analyst review" — the
     tool does not fabricate a cause it has no basis for.

Output is grouped by business unit so it reads like something you'd
actually hand to a segment finance lead for the monthly close review.
"""

import pandas as pd
from event_log import load_event_log

FLAGGED_PATH = "/home/claude/fpa_project/flagged_variances.csv"
OUT_PATH = "/home/claude/fpa_project/commentary_draft.csv"

def format_month(m: str) -> str:
    return pd.to_datetime(m).strftime("%B %Y")

def build_commentary(row, event_log: pd.DataFrame) -> str:
    match = event_log[
        (event_log["business_unit"] == row["business_unit"])
        & (event_log["line_item"] == row["line_item"])
        & (event_log["month"] == pd.to_datetime(row["month"]).strftime("%Y-%m"))
    ]

    month_str = format_month(row["month"])
    variance_desc = row["flag_reason"]

    base = (
        f"{row['line_item']} in {row['business_unit']} was {variance_desc} "
        f"in {month_str}."
    )

    if len(match) > 0:
        driver = match.iloc[0]["driver"]
        return f"{base} Driver: {driver}."
    else:
        return f"{base} Driver: pending analyst review — no known one-off cause on file."

def generate(flagged: pd.DataFrame) -> pd.DataFrame:
    event_log = load_event_log()
    flagged = flagged[flagged["flagged"]].copy()
    flagged["commentary"] = flagged.apply(lambda r: build_commentary(r, event_log), axis=1)
    flagged["has_known_driver"] = flagged["commentary"].apply(
        lambda c: "pending analyst review" not in c
    )
    return flagged

if __name__ == "__main__":
    flagged = pd.read_csv(FLAGGED_PATH)
    result = generate(flagged)

    cols = ["business_unit", "line_item", "month", "commentary", "has_known_driver"]
    result[cols].to_csv(OUT_PATH, index=False)

    print(f"Wrote {len(result)} commentary rows to {OUT_PATH}\n")
    known = result["has_known_driver"].sum()
    print(f"{known} of {len(result)} flagged rows matched a known driver "
          f"({known/len(result):.0%}) — the rest drafted objectively and "
          f"routed for analyst review.\n")

    print("=" * 90)
    print("SAMPLE — Customer Support, monthly close review draft")
    print("=" * 90)
    sample = result[result["business_unit"] == "Customer Support"].sort_values("month")
    for _, r in sample.head(6).iterrows():
        print(f"- {r['commentary']}")
