#!/usr/bin/env python3
"""Count how many recently-sold rows actually carry a sold price, per metro.

Why this exists: a sold/comps endpoint can return a full page of rows, with an address and a sold
date on every one, and still have no price on any of them. The row count looks right, the response
is HTTP 200, and `ok` is true. The only thing missing is the number you asked for.

That is not a bug in any one provider. Twelve US states are "non-disclosure": the sale price is not
filed in a public record, so no data source has it to give you. What differs between providers is
whether they tell you, and what you find out is that mostly they do not, because nobody reports
field-fill rate.

This script measures fill rate, not HTTP success. Run it against ReefAPI, or port the one `fetch`
function to any other provider and run the same count against theirs. The comparison is the point.

Usage:
    export REEFAPI_KEY=...            # https://reefapi.com/signup?utm_source=github&utm_medium=repo&utm_campaign=zillow-sold-price-coverage, 1,000 free credits, no card
    python measure.py                 # writes data/coverage.json and data/coverage.csv
    python measure.py --metros "Austin, TX" "Columbus, OH"

Cost: one call per metro, 2 credits each. The default basket of 8 metros costs 16 credits.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ENDPOINT = "https://api.reefapi.com/zillow/v1/sold"

# Four disclosure states and four non-disclosure ones, so the table has its own control group.
# A result is only interesting if the disclosure metros come back full in the same run.
METROS: list[tuple[str, str, bool]] = [
    # (metro,               state, non_disclosure)
    ("Columbus, OH", "OH", False),
    ("Charlotte, NC", "NC", False),
    ("Phoenix, AZ", "AZ", False),
    ("Denver, CO", "CO", False),
    ("Austin, TX", "TX", True),
    ("Houston, TX", "TX", True),
    ("Salt Lake City, UT", "UT", True),
    ("Jackson, MS", "MS", True),
]

# The twelve states where the sale price is not in a public record. Sources are listed in the README;
# treat this as "the list we measured against", not as legal advice.
NON_DISCLOSURE_STATES = [
    "AK", "ID", "KS", "LA", "MS", "MO", "MT", "NM", "ND", "TX", "UT", "WY",
]


def fetch(metro: str, key: str, timeout: int = 120) -> dict:
    """The only provider-specific function in this file. Port this to compare another API."""
    req = urllib.request.Request(
        ENDPOINT,
        data=json.dumps({"location": metro}).encode(),
        headers={"content-type": "application/json", "x-api-key": key},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        return json.loads(e.read())


def summarise(metro: str, state: str, non_disclosure: bool, payload: dict) -> dict:
    items = ((payload.get("data") or {}).get("items")) or []
    have_price = sum(1 for i in items if i.get("sold_price_usd"))
    have_date = sum(1 for i in items if i.get("sold_date"))
    have_zest = sum(1 for i in items if i.get("zestimate_usd"))
    return {
        "metro": metro,
        "state": state,
        "non_disclosure_state": non_disclosure,
        "rows": len(items),
        "sold_price_present": have_price,
        "sold_date_present": have_date,
        "zestimate_present": have_zest,
        "price_fill_rate": round(have_price / len(items), 4) if items else None,
        "ok": payload.get("ok"),
        "error": (payload.get("error") or {}).get("code"),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--metros", nargs="*", help="override the default basket")
    ap.add_argument("--out", default="data", help="output directory (default: data)")
    args = ap.parse_args()

    key = os.environ.get("REEFAPI_KEY")
    if not key:
        print("REEFAPI_KEY is not set. Get a free key at https://reefapi.com/signup?utm_source=github&utm_medium=repo&utm_campaign=zillow-sold-price-coverage", file=sys.stderr)
        return 2

    basket = METROS
    if args.metros:
        known = {m[0]: m for m in METROS}
        basket = [known.get(m, (m, "??", False)) for m in args.metros]

    rows = []
    for metro, state, nd in basket:
        t0 = time.time()
        row = summarise(metro, state, nd, fetch(metro, key))
        row["latency_s"] = round(time.time() - t0, 2)
        rows.append(row)
        flag = "non-disclosure" if nd else "disclosure    "
        print(f"{metro:22s} {flag}  rows={row['rows']:3d}  "
              f"price={row['sold_price_present']:3d}  date={row['sold_date_present']:3d}  "
              f"{row['latency_s']:5.1f}s")

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    doc = {
        "measured_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "endpoint": ENDPOINT,
        "non_disclosure_states": NON_DISCLOSURE_STATES,
        "results": rows,
        "totals": {
            "rows": sum(r["rows"] for r in rows),
            "sold_price_present": sum(r["sold_price_present"] for r in rows),
            "sold_date_present": sum(r["sold_date_present"] for r in rows),
        },
    }
    (out / "coverage.json").write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    with (out / "coverage.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    t = doc["totals"]
    print(f"\n{t['sold_price_present']} of {t['rows']} rows carried a sold price. "
          f"{t['sold_date_present']} of {t['rows']} carried a sold date.")
    print(f"Wrote {out / 'coverage.json'} and {out / 'coverage.csv'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
