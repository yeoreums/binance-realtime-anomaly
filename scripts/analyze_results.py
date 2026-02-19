import pandas as pd

df = pd.read_csv("data/window_results.csv")

total = len(df)
anomalies = (df["prediction"] == -1).sum()

print("Total windows:", total)
print("Anomalies:", anomalies)
print("Anomaly rate:", anomalies / total)
