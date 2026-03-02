import pandas as pd
from datetime import datetime
import os

# Create reports folder if not exists
os.makedirs("reports", exist_ok=True)

# Create report file name
report_path = f"reports/event_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
report_file = open(report_path, "w")

def log(text=""):
    print(text)
    report_file.write(text + "\n")

# Load data
df = pd.read_csv("data/window_results.csv")

# Keep scored rows only
df = df[df["prediction"].notna()]

# Convert timestamp to datetime
df["timestamp"] = pd.to_datetime(df["timestamp"])

# Separate anomaly and normal
anomalies = df[df["prediction"] == -1]
normal = df[df["prediction"] == 1]

log(f"Total windows: {len(df)}")
log(f"Total anomalies: {len(anomalies)}")
log()
log(f"Anomaly rate: {len(anomalies)/len(df):.4f}")
log()

# =========================
# 1. Anomalies per hour
# =========================
anomalies_per_hour = anomalies.groupby(anomalies["timestamp"].dt.hour).size()

log("Anomalies per hour:")
log(str(anomalies_per_hour.sort_values(ascending=False)))
log()

# =========================
# 2. Top anomaly windows
# =========================
log("Top anomaly windows (highest volatility):")
top_vol = anomalies.sort_values("volatility", ascending=False).head(10)

log(str(top_vol[[
    "timestamp",
    "return",
    "volatility",
    "trade_count",
    "volume"
]]))
log()

# =========================
# 3. Compare hourly volatility vs anomaly count
# =========================
hourly_vol = df.groupby(df["timestamp"].dt.hour)["volatility"].mean()
hourly_anom = anomalies.groupby(anomalies["timestamp"].dt.hour).size()

comparison = pd.DataFrame({
    "avg_volatility": hourly_vol,
    "anomaly_count": hourly_anom
}).fillna(0)

log("Hourly comparison (volatility vs anomalies):")
log(str(comparison.sort_values("anomaly_count", ascending=False)))

report_file.close()
print(f"\nReport saved to: {report_path}")