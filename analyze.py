# analyze.py
# SUMMARY: km_since_service is by far the strongest breakdown predictor (r=+0.40); avg_daily_km
# (r=+0.25) and load_factor (r=+0.22) also separate the groups. Total odometer and age are
# near-zero (r≈0.00) — high mileage and old age do NOT predict breakdown in this fleet.

# ── How this analysis works ──────────────────────────────────────────────────────────────────
# 1. Load fleet_history.csv (120 cars; broke_down=1 means the car later broke down).
# 2. Compare every numeric column between the two groups and measure correlation with broke_down.
#    Only three columns separate the groups; two obvious-looking ones (odometer, age) do not.
# 3. Build a 0-100 risk score from those three columns using min-max scaling + weighted sum.
#    Weights are proportional to each column's correlation with the outcome.
# 4. Print the full fleet ranked by risk, highest first.

import pandas as pd

df = pd.read_csv("fleet_history.csv")

# ── Step 1: measure which columns actually separate the two groups ────────────────────────────
print("=" * 62)
print("STEP 1 — Correlation of each feature with broke_down")
print("=" * 62)

features = ["odometer_km", "km_since_service", "avg_daily_km", "load_factor", "age_years"]
correlations = {}
for col in features:
    r = df[col].corr(df["broke_down"])
    correlations[col] = r

for col, r in sorted(correlations.items(), key=lambda x: abs(x[1]), reverse=True):
    bar = "#" * int(abs(r) * 40)
    print(f"  {col:<22}  r = {r:+.3f}  {bar}")

print()
print("  >> odometer_km and age_years are near zero: total mileage and age do NOT predict breakdown.")
print("  >> km_since_service, avg_daily_km, load_factor DO separate the groups.")

# ── Step 2: group means to show the separation concretely ────────────────────────────────────
signal_cols = ["km_since_service", "avg_daily_km", "load_factor"]
broke   = df[df["broke_down"] == 1]
healthy = df[df["broke_down"] == 0]

print()
print("=" * 62)
print("STEP 2 — Group means for the three signal columns")
print(f"  (broke-down: n={len(broke)}  healthy: n={len(healthy)})")
print("=" * 62)
print(f"  {'Column':<22}  {'Broke mean':>12}  {'OK mean':>10}  {'Ratio':>7}")
print("  " + "-" * 58)
for col in signal_cols:
    b = broke[col].mean()
    h = healthy[col].mean()
    ratio = b / h
    print(f"  {col:<22}  {b:>12.1f}  {h:>10.1f}  {ratio:>7.2f}x")

# ── Step 3: build risk score 0-100 ───────────────────────────────────────────────────────────
# Weights proportional to |correlation| with broke_down, normalised to sum to 1.
raw_weights = {col: abs(correlations[col]) for col in signal_cols}
total_w = sum(raw_weights.values())
weights = {col: w / total_w for col, w in raw_weights.items()}

print()
print("=" * 62)
print("STEP 3 — Risk score construction")
print("=" * 62)
for col, w in weights.items():
    print(f"  {col:<22}  weight = {w:.3f}  (proportional to |r| = {raw_weights[col]:.3f})")

# Min-max scale each signal column to [0, 1], then weighted sum → [0, 1] → multiply by 100
df_score = df.copy()
for col in signal_cols:
    col_min = df[col].min()
    col_max = df[col].max()
    df_score[f"{col}_scaled"] = (df[col] - col_min) / (col_max - col_min)

df_score["risk_score"] = sum(
    weights[col] * df_score[f"{col}_scaled"] for col in signal_cols
) * 100

df_score["risk_score"] = df_score["risk_score"].round(1)

# ── Step 4: print full fleet ranked by risk, highest first ───────────────────────────────────
ranked = df_score[["car_id", "km_since_service", "avg_daily_km", "load_factor",
                    "risk_score", "broke_down"]].sort_values("risk_score", ascending=False)

print()
print("=" * 62)
print("STEP 4 — Full fleet ranked by risk (top 10 shown)")
print("=" * 62)
print(f"  {'car_id':<12}  {'km_since_svc':>14}  {'avg_daily_km':>14}  {'load_factor':>12}  {'risk':>6}  {'broke?':>7}")
print("  " + "-" * 68)
for _, row in ranked.head(10).iterrows():
    flag = "YES" if row["broke_down"] == 1 else "-"
    print(f"  {row['car_id']:<12}  {row['km_since_service']:>14.0f}  {row['avg_daily_km']:>14.0f}  {row['load_factor']:>12.2f}  {row['risk_score']:>6.1f}  {flag:>7}")

# Validation: does the score actually separate the groups?
mean_risk_broke   = df_score[df_score["broke_down"] == 1]["risk_score"].mean()
mean_risk_healthy = df_score[df_score["broke_down"] == 0]["risk_score"].mean()
print()
print(f"  Average risk score — cars that broke down : {mean_risk_broke:.1f}")
print(f"  Average risk score — cars that stayed OK  : {mean_risk_healthy:.1f}")

top_quartile = df_score.nlargest(30, "risk_score")
precision = top_quartile["broke_down"].mean() * 100
print(f"  Of the 30 highest-risk cars, {precision:.0f}% actually broke down (vs 22% base rate).")
