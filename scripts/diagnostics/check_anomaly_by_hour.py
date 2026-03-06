import pandas as pd
import os
from datetime import datetime

# ---------- setup logging ----------
os.makedirs("reports", exist_ok=True)
log_path = "reports/anomaly_by_hour_log.txt"
log_file = open(log_path, "a")

def log(text=""):
    print(text)
    log_file.write(text + "\n")

log("\n" + "="*50)
log(f"Timestamp: {datetime.now()}")
log("="*50)

# ---------- load data ----------
today = datetime.now().strftime("%Y-%m-%d")
df = pd.read_csv(f"data/window_results_{today}.csv")
log(f"Total rows: {len(df)}")

# keep scored only
df = df[df["prediction"].notna()].copy()
log(f"Scored rows: {len(df)}")

df["timestamp"] = pd.to_datetime(df["timestamp"])
df["hour"] = df["timestamp"].dt.hour

# ---------- anomaly rate by hour ----------
hourly_rate = df.groupby("hour")["prediction"].apply(
    lambda x: (x == -1).mean()
)

log("\nAnomaly rate by hour:")
log(hourly_rate.sort_index().to_string())

# ---------- counts by hour ----------
hourly_counts = df.groupby("hour")["prediction"].count()
log("\nWindow count by hour:")
log(hourly_counts.sort_index().to_string())

log_file.close()
print(f"\nAppended to {log_path}")