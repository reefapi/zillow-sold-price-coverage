# zillow-sold-price-coverage

**How often does a "recently sold" row actually come back with a sold price?**

Measured per metro, because in twelve US states the answer is "almost never" and most real-estate
APIs will not tell you before you build on them.

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

## Why it is worth measuring yourself

The failure is quiet. It does not raise, it does not 404, and it does not show up in an uptime
graph or a success-rate dashboard, because **the request succeeded**. It only appears if you count
how many rows carry the field you actually needed.

That is the general lesson here and it is not specific to real estate: **measure field-fill rate,
not HTTP success.** `ok: true` with a null where the price should be is the failure mode nobody
reports.

## Run it

```bash
export REEFAPI_KEY=...        # free key, 1,000 credits, no card: https://reefapi.com/signup?utm_source=github&utm_medium=repo&utm_campaign=zillow-sold-price-coverage
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

* Zillow API docs: <https://reefapi.com/docs/zillow?utm_source=github&utm_medium=repo&utm_campaign=zillow-sold-price-coverage>
* One key across 300+ data APIs, one credit pool: <https://reefapi.com/?utm_source=github&utm_medium=repo&utm_campaign=zillow-sold-price-coverage>

MIT licensed. Issues and pull requests welcome, especially a `fetch()` for another provider.
