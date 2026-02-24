import pandas as pd
import numpy as np
import os
from datetime import datetime

os.makedirs("reports", exist_ok=True)
log_path = "reports/baseline_comparison_log.txt"
log_file = open(log_path, "a", buffering=1)

def log(text=""):
    print(text)
    log_file.write(text + "\n")

log("\n" + "="*60)
log(f"Timestamp: {datetime.now()}")
log("="*60)

df = pd.read_csv("data/window_results.csv")
log(f"Total rows in CSV: {len(df)}")

df = df[df["prediction"].notna()].copy()
log(f"Rows with predictions: {len(df)}")

df["timestamp"] = pd.to_datetime(df["timestamp"])


if_anom = df["prediction"] == -1

vol_mean = df["volatility"].mean()
vol_std = df["volatility"].std()
threshold = vol_mean + 2 * vol_std
vol_anom = df["volatility"] > threshold

log("=== Volatility baseline ===")
log(f"Vol mean : {vol_mean:.4f}")
log(f"Vol std  : {vol_std:.4f}")
log(f"Threshold (mean + 2*std): {threshold:.4f}")
log(f"Max volatility in dataset: {df['volatility'].max():.4f}")

log("\n=== Counts ===")
log(f"Total windows: {len(df)}")
log(f"IF anomalies : {if_anom.sum()} ({if_anom.mean():.4%})")
log(f"VOL anomalies: {vol_anom.sum()} ({vol_anom.mean():.4%})")

overlap = (if_anom & vol_anom).sum()
union = (if_anom | vol_anom).sum()
jaccard = overlap / union if union > 0 else 0

log("\n=== Overlap ===")
log(f"Overlap count: {overlap}")
log(f"IF-only      : {(if_anom & ~vol_anom).sum()}")
log(f"VOL-only     : {(~if_anom & vol_anom).sum()}")
log(f"Jaccard      : {jaccard:.4f}")

normal_vol = df["volatility"] <= threshold
if_normal_vol_count = (if_anom & normal_vol).sum()

log("\n=== Key test ===")
log(f"IF anomalies in normal-vol windows: {if_normal_vol_count}")

if_only = df[if_anom & ~vol_anom]
if len(if_only) > 0:
    log("\nIF-only anomaly windows:")
    log(if_only[["timestamp","trade_count","volume","volatility","return","score"]].to_string(index=False))
else:
    log("\nNo IF-only anomalies.")

log_file.close()
print(f"\nAppended to {log_path}")