import pandas as pd
from datetime import datetime
import os

# File paths
data_path = "data/window_results.csv"
output_dir = "analysis"
output_file = os.path.join(output_dir, "score_summary.txt")

# Make sure analysis folder exists
os.makedirs(output_dir, exist_ok=True)

# Load data
df = pd.read_csv(data_path)

# Use only rows where model produced scores
df = df[df["score"].notna()]

total_windows = len(df)
anomalies = (df["prediction"] == -1).sum()
anomaly_rate = anomalies / total_windows if total_windows > 0 else 0

stats = df["score"].describe()

# Write summary
with open(output_file, "a") as f:
    f.write("\n==============================\n")
    f.write(f"Timestamp: {datetime.now()}\n")
    f.write(f"Total scored windows: {total_windows}\n")
    f.write(f"Anomalies: {anomalies}\n")
    f.write(f"Anomaly rate: {anomaly_rate:.4f}\n\n")
    f.write("Score statistics:\n")
    f.write(stats.to_string())
    f.write("\n")

print(f"Summary saved to {output_file}")
