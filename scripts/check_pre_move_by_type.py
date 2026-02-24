import pandas as pd
import numpy as np
from datetime import datetime
import os

os.makedirs("reports", exist_ok=True)
report_path = "reports/pre_move_log.txt"
report_file = open(report_path, "a")

def log(text=""):
    print(text)
    report_file.write(text + "\n")

log("\n" + "="*50)
log(f"Timestamp: {datetime.now()}")
log("="*50)

df = pd.read_csv("data/window_results.csv")
log(f"Total windows: {len(df)}")

df = df[df["prediction"].notna()]
log(f"Windows with predictions: {len(df)}")

df["timestamp"] = pd.to_datetime(df["timestamp"])
df = df.sort_values("timestamp").reset_index(drop=True)

WINDOW_SIZE_SEC = 20
LOOKAHEAD_MIN = 5
steps = int((LOOKAHEAD_MIN * 60) / WINDOW_SIZE_SEC)
log(f"Lookahead: {LOOKAHEAD_MIN} min ({steps} windows)")

# Volatility threshold
vol_mean = df["volatility"].mean()
vol_std  = df["volatility"].std()
threshold = vol_mean + 2 * vol_std
log(f"Vol threshold: {threshold:.4f}")

# Group labels
if_anom  = df["prediction"] == -1
vol_anom = df["volatility"] > threshold

df["group"] = "normal"
df.loc[vol_anom & ~if_anom, "group"] = "vol_only"
df.loc[if_anom  & ~vol_anom, "group"] = "if_only"
df.loc[if_anom  & vol_anom,  "group"] = "both"

log("\nGroup counts:")
log(df["group"].value_counts().to_string())

# Future absolute return
returns = df["return"].values
future_returns = []
for i in range(len(df)):
    if i + steps < len(df):
        future_returns.append(np.sum(np.abs(returns[i+1:i+1+steps])))
    else:
        future_returns.append(np.nan)

df["future_abs_move"] = future_returns

# Report per group
log("\n=== Pre-move analysis by group ===")
for group in ["normal", "vol_only", "if_only", "both"]:
    subset = df[df["group"] == group]["future_abs_move"].dropna()
    if len(subset) == 0:
        log(f"\n{group}: no samples")
        continue
    log(f"\n{group} (n={len(subset)}):")
    log(f"  mean abs move : {subset.mean():.6f}")
    log(f"  median abs move: {subset.median():.6f}")
    log(f"  std            : {subset.std():.6f}")

# Ratio vs normal baseline
normal_mean = df[df["group"] == "normal"]["future_abs_move"].mean()
log("\n=== Ratio vs normal ===")
for group in ["vol_only", "if_only", "both"]:
    subset = df[df["group"] == group]["future_abs_move"].dropna()
    if len(subset) == 0:
        continue
    ratio = subset.mean() / normal_mean if normal_mean else float("nan")
    log(f"{group}: {ratio:.2f}x normal")

report_file.close()
print(f"\nAppended to {report_path}")