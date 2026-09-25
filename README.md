# Zillow sold price coverage — does a "recently sold" row actually carry a price? (measured, 2026)

**Short answer: in four US metros, 41 out of 41. In Austin, Texas, 0 out of 41.**

Measured per metro, because in twelve US states the answer is "almost never" and most real-estate
APIs will not tell you before you build on them.

Run it yourself with a [free ReefAPI key](https://reefapi.com/signup?utm_source=github&utm_medium=repo&utm_campaign=zillow-sold-price-coverage) (1,000 credits, no card), or point the one provider-specific function at any other [real estate data API](https://reefapi.com/docs/zillow?utm_source=github&utm_medium=repo&utm_campaign=zillow-sold-price-coverage) and compare.

This is a dataset and a script, not a client library. Run it against ReefAPI, or port one function
and run the same count against any other provider. **The comparison is the point.**

---

## The finding

A sold/comps endpoint can return a full page of rows, with an address and a sold date on every one,
and still carry **no price on any of them**. Row count looks right. HTTP is 200. The response says
success. The only thing missing is the number you asked for.

Measured 2026-09-25, 41 recently-sold listings per metro, 8 metros, **n = 328**:

| metro | state | rows | sold price present | sold date present |
|---|---|---:|---:|---:|
| Columbus, OH | OH | 41 | **41 (100%)** | 41 |
| Charlotte, NC | NC | 41 | **41 (100%)** | 41 |
| Phoenix, AZ | AZ | 41 | **41 (100%)** | 41 |
| Denver, CO | CO | 41 | **41 (100%)** | 41 |
| Austin, TX | TX | 41 | **0 (0%)** | 41 |
| Houston, TX | TX | 41 | **1 (2%)** | 41 |
| Salt Lake City, UT | UT | 41 | **1 (2%)** | 35 |
| Jackson, MS | MS | 41 | **1 (2%)** | 41 |

**167 of 328 rows carried a sold price. 322 of 328 carried a sold date.**

The row count is identical in all eight metros. The date column is nearly identical. Only the price
column empties, and it empties along a state line.

The same script produced the same figures on 2026-09-24 and again on 2026-09-25, including the
Salt Lake City date anomaly (35 rather than 41), so this is a property of the source rather than a
bad afternoon.

## Why

Twelve states are **non-disclosure**: the sale price is not recorded in a public record, so it is
not there for anyone to sell you. No provider can fix this, and a provider claiming full US sold
coverage is either quoting list price, quoting an estimate, or not counting.

`AK · ID · KS · LA · MS · MO · MT · NM · ND · TX · UT · WY`

Rules vary within a state and change over time. Treat the list as *what this measurement was run
against*, not as legal advice.

## What one row actually looks like, on both sides of the state line

Two complete rows from `zillow/v1/sold`, returned 2026-09-25, with nothing removed except
the street address. The same query shape, the same field set, one from a disclosure state
and one from a non-disclosure state. Every field name the endpoint can return is here.

```json
{
  "austin_tx__non_disclosure_state": {
    "zpid": 29476953,
    "source": "zillow",
    "url": "https://www.zillow.com/homedetails/3403-Clawson-Rd-Austin-TX-78704/29476953_zpid/",
    "list_price_usd": null,
    "price_display": null,
    "status": "RECENTLY_SOLD",
    "status_text": "Sold",
    "property_type": "MULTI_FAMILY",
    "beds": null,
    "baths": 2.0,
    "sqft": 1560.0,
    "lot_sqft": 8572.0,
    "zestimate_usd": null,
    "rent_zestimate_usd": 2643,
    "tax_assessed_value_usd": 514912.0,
    "days_on_market": 2,
    "address_line": "<redacted in this README only — see the note below>",
    "city": "Austin",
    "state_code": "TX",
    "postal_code": "78704",
    "address": "3403 Clawson Rd, Austin, TX 78704",
    "latitude": 30.236038,
    "longitude": -97.77868,
    "broker_name": "<redacted in this README only — see the note below>",
    "is_showcase": false,
    "photos": [
      "https://photos.zillowstatic.com/fp/f7610667b67d997aac04b0fbe8aecea3-p_e.jpg"
    ],
    "is_building": false,
    "identifier_type": "zpid",
    "sold_price_usd": null,
    "sold_date": "2026-09-23",
    "price_unavailable_reason": "non_disclosure_state",
    "price_unavailable_detail": "This is a non-disclosure state: the sale price is not a public record there, Zillow carries no number for it, and no retry or other endpoint can produce one."
  },
  "columbus_oh__disclosure_state": {
    "zpid": 33899544,
    "source": "zillow",
    "url": "https://www.zillow.com/homedetails/47-Meadowlark-Ln-Columbus-OH-43214/33899544_zpid/",
    "list_price_usd": 390000.0,
    "price_display": "$390,000",
    "status": "RECENTLY_SOLD",
    "status_text": "Sold",
    "property_type": "SINGLE_FAMILY",
    "beds": 4.0,
    "baths": 3.0,
    "sqft": 1906.0,
    "lot_sqft": 13503.6,
    "zestimate_usd": 396200,
    "rent_zestimate_usd": 2787,
    "tax_assessed_value_usd": 395900.0,
    "days_on_market": 0,
    "address_line": "<redacted in this README only — see the note below>",
    "city": "Columbus",
    "state_code": "OH",
    "postal_code": "43214",
    "address": "47 Meadowlark Ln, Columbus, OH 43214",
    "latitude": 40.073128,
    "longitude": -83.01732,
    "broker_name": "<redacted in this README only — see the note below>",
    "is_showcase": false,
    "photos": [
      "https://photos.zillowstatic.com/fp/9856cc43e3c84d56119b923a14105a63-p_e.jpg"
    ],
    "is_building": false,
    "identifier_type": "zpid",
    "sold_price_usd": 390000.0,
    "sold_date": "2026-09-25"
  }
}
```

> **Only this README hides those values.** The API returns them populated: seller name, street
> address and the contact fields all come back in your own calls, and for most customers that is
> the point of the endpoint. They are masked here because a public README is not the right place to
> republish an individual's details, not because the data is unavailable.

The two rows are the finding in miniature: identical structure, `sold_date` present on both,
and `sold_price_usd` populated in Columbus and `null` in Austin.

## Why it is worth measuring yourself

The failure is quiet. It does not raise, it does not 404, and it does not show up in an uptime
graph or a success-rate dashboard, because **the request succeeded**. It only appears if you count
how many rows carry the field you actually needed.

That is the general lesson here and it is not specific to real estate: **measure field-fill rate,
not HTTP success.** `ok: true` with a null where the price should be is the failure mode nobody
reports.

## Run it

Get one at [reefapi.com/signup](https://reefapi.com/signup?utm_source=github&utm_medium=repo&utm_campaign=zillow-sold-price-coverage) — 1,000 credits, no card.

```bash
export REEFAPI_KEY=...        # free key, 1,000 credits, no card
python measure.py             # writes data/coverage.json and data/coverage.csv
```

One call per metro, 2 credits each. The default basket of 8 metros costs 16 credits.

```bash
python measure.py --metros "Austin, TX" "Columbus, OH"
```

### Comparing another provider

`fetch()` in `measure.py` is the only provider-specific function. Point it at another sold/comps
endpoint, keep `summarise()` as it is, and the table is directly comparable. If you publish the
result, a link back is welcome but not expected.

## What is in here

| file | what |
|---|---|
| `measure.py` | the script, one provider-specific function |
| `data/coverage.json` | full result including per-metro latency and the state list |
| `data/coverage.csv` | the same table, for a spreadsheet |

## Caveats, stated rather than buried

* **A snapshot.** Dated 2026-09-25. Re-run it; do not cite the table as a current fact.
* **One basket per metro.** 41 rows is what the endpoint returns for a metro-level query. It is not
  a random sample of every sale in that metro.
* **Presence, not accuracy.** This counts whether a field is populated. It does not check whether
  the populated value is correct.
* **A ReefAPI repo.** We build the API this runs against, so read the numbers as reproducible rather
  than disinterested. That is exactly why the script is here and the raw output is committed: run it
  and see, and run it against somebody else too.

## Related

* [Zillow API documentation — endpoints, parameters and a runnable example](https://reefapi.com/docs/zillow?utm_source=github&utm_medium=repo&utm_campaign=zillow-sold-price-coverage)
* [One API key for 300+ web data sources](https://reefapi.com/?utm_source=github&utm_medium=repo&utm_campaign=zillow-sold-price-coverage), one shared credit pool

MIT licensed. Issues and pull requests welcome, especially a `fetch()` for another provider.
