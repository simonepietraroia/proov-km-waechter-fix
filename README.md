# KM-Wächter — Vossberg Mobility Fleet Service Monitor

A Python service that decides when each car in a fleet needs a service and prints a nightly
health report. Originally written in 2013, this repo contains the fixed and modernised version.

---

## What it does

**Service alerting** — given a car's odometer reading and the km at which it was last serviced,
`km_wachter.py` calculates how much of the 15,000 km service interval has been used and flags any
car at or above 80% wear.

**Nightly fleet report** — `fleet_report.py` prints a summary across the whole fleet: how many
cars are due, average wear percentage, and total fleet distance converted to miles for a UK
partner garage.

**Breakdown-risk analysis** — `analyze.py` uses historical data (120 cars, labelled by whether
they later broke down) to rank the current fleet by breakdown risk *before* the 80% rule would
ever flag them.

---

## Quick start

```bash
pip install pytest pandas
pytest                # all 4 tests should pass
python verify.py      # acceptance check — should print 10/11 PASS (NOTES.md is yours to write)
python analyze.py     # run the breakdown-risk analysis
```

---

## Files

| File | Purpose |
|---|---|
| `km_wachter.py` | Core logic: `wear_percent()`, `needs_service()`, `check_fleet()` |
| `fleet_report.py` | Nightly report: `fleet_summary()`, `print_report()` |
| `fleet_utils.py` | Helper functions: unit conversion, formatting, utilities |
| `config_loader.py` | Reads `settings.cfg` at runtime |
| `log_util.py` | Minimal timestamped logger |
| `settings.cfg` | Rule values: 15,000 km interval, 80% warn threshold |
| `analyze.py` | Pandas-based breakdown-risk analysis and ranking |
| `fleet_history.csv` | 120 labelled cars used for the risk analysis |
| `fleet_sample.json` | Small sample fleet for manual testing |
| `test_km_wachter.py` | Tests for wear and service-flag logic |
| `test_fleet_report.py` | Tests for fleet summary (including missing-reading edge case) |
| `verify.py` | Acceptance check — run before handing in |

---

## Bugs fixed

### `km_wachter.py` — `wear_percent()`
**Before:** `km_since_service // interval * 100` — integer floor division returned `0` for any
car that had not yet completed a full 15,000 km interval. A car at 14,900 km (99.3% worn) was
never flagged.  
**After:** `km_since_service / interval * 100` — true division; 14,900 / 15,000 = 99.3%.

### `km_wachter.py` — `needs_service()`
**Before:** `car.get("last_service_km", 0)` — a missing reading defaulted to 0, making any
high-odometer car with no service history appear catastrophically overdue.  
**After:** `car.get("last_service_km")` returning `None` → `return False`. Unknown history means
do not flag.

### `fleet_report.py` — `car_wear()`
**Before:** `car["last_service_km"]` — bare key access raised `KeyError` on any car without a
service reading.  
**After:** `.get("last_service_km")` with a `None` guard; returns `0.0` for unknown history.

### `fleet_report.py` — `fleet_summary()`
**Before:** `total // len(fleet)` — integer division truncated the average wear to 0 for any
fleet where no single car had crossed a full interval.  
**After:** `total / len(fleet)` — correct float average.

### `fleet_utils.py` — `MILES_PER_KM`
**Before:** `1.609` — this is the number of *kilometres per mile*, not miles per km. `km_to_miles(100)` returned 160.9 instead of 62.1.  
**After:** `0.621371` — 100 km now correctly converts to 62.1 miles.

---

## Modernisation (style changes, no behaviour change)

Across all touched files:

- `%`-format strings replaced with f-strings
- Type hints and short docstrings added to every function
- `== True` comparisons removed; pointless `if/else: return True/False` collapsed to direct `return`
- `open()` calls wrapped in `with` statements (fixes file-handle leaks on exceptions)
- `path == None` corrected to `path is None`
- `line.split("=")` in `config_loader` changed to `split("=", 1)` so values containing `=` are preserved
- `get_setting()` body replaced with `dict.get()` (it was always a hand-rolled duplicate)
- `del LOG_LINES[:]` replaced with `LOG_LINES.clear()` (Python 3 idiom)

---

## Breakdown-risk analysis

`analyze.py` answers the question: *which cars are most likely to break down before the 80% rule
would flag them?*

**What the data says** (120 cars, `broke_down` column = 1 if it later broke down):

| Column | Correlation with breakdown | Verdict |
|---|---|---|
| `km_since_service` | r = +0.40 | Strong signal — overdue cars break more |
| `avg_daily_km` | r = +0.25 | Harder-driven cars break more |
| `load_factor` | r = +0.22 | Heavier load use correlates with breakdown |
| `odometer_km` | r = +0.002 | **Near zero — total mileage does not predict breakdown** |
| `age_years` | r = −0.001 | **Near zero — age does not predict breakdown** |

The naive assumption ("old, high-mileage cars break down") is not supported by this data. A car
with 100,000 km on the clock is no more likely to break down than one with 20,000 km. What
matters is how overdue it is for service and how hard it is being driven right now.

**Risk score** — each car receives a 0–100 score built from min-max scaling of the three signal
columns, weighted by their correlation strength (46% `km_since_service`, 29% `avg_daily_km`,
25% `load_factor`). Cars that actually broke down average a score of 61.6 vs 41.4 for healthy
cars. The top 30 by score contain 53% of all breakdowns against a 22% base rate.

---

## Rules that must not change

The 15,000 km service interval and the 80% warning threshold are defined in both
`km_wachter.py` (`SERVICE_INTERVAL_KM`, `WARN_AT_PERCENT`) and `settings.cfg`. They must stay
identical and must not be altered without sign-off from Fleet Ops.
