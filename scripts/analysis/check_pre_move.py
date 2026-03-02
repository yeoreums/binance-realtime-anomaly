import pandas as pd
import numpy as np
from datetime import datetime
import os

os.makedirs("reports", exist_ok=True)

report_path = f"reports/pre_move_log.txt"
report_file = open(report_path, "a")

def log(text=""):
    print(text)
    report_file.write(text + "\n")

log("\n" + "="*50)
log(f"Timestamp: {datetime.now()}")
log("="*50)

# Load data
df = pd.read_csv("data/window_results.csv")
df = df[df["prediction"].notna()]
df["timestamp"] = pd.to_datetime(df["timestamp"])

# Sort just in case
df = df.sort_values("timestamp").reset_index(drop=True)

# --- Configuration ---
WINDOW_SIZE_SEC = 20
LOOKAHEAD_MIN = 5           # test 5-minute future move
steps = int((LOOKAHEAD_MIN * 60) / WINDOW_SIZE_SEC)

log(f"Using lookahead: {LOOKAHEAD_MIN} min ({steps} windows)")

# Future cumulative return (sum of next N window returns)
future_returns = []
returns = df["return"].values

for i in range(len(df)):
    if i + steps < len(df):
        future_returns.append(np.sum(returns[i+1:i+1+steps]))
    else:
        future_returns.append(np.nan)

df["future_return"] = future_returns

# Split groups
anom = df[df["prediction"] == -1]
norm = df[df["prediction"] == 1]

log()
log("Average future move (absolute):")
log(f"Normal  : {norm['future_return'].abs().mean()}")
log(f"Anomaly : {anom['future_return'].abs().mean()}")

log()
log("Median future move (absolute):")
log(f"Normal  : {norm['future_return'].abs().median()}")
log(f"Anomaly : {anom['future_return'].abs().median()}")

log()
log("Sample counts:")
log(f"Normal  : {norm['future_return'].count()}")
log(f"Anomaly : {anom['future_return'].count()}")

report_file.close()
print(f"\nAppended to {report_path}")
