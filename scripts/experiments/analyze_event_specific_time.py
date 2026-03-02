import pandas as pd

df = pd.read_csv("data/window_results.csv")
df["timestamp"] = pd.to_datetime(df["timestamp"])

period = df[
    (df["timestamp"] >= "2026-02-21 03:00:00") &
    (df["timestamp"] <= "2026-02-21 03:10:00")
]

print("Windows in period:", len(period))
print()

print("Feature means (03:00–03:10):")
print("trade_count:", period["trade_count"].mean())
print("volume:", period["volume"].mean())
print("volatility:", period["volatility"].mean())
print("Max abs_return:", period["return"].abs().max())
print("Mean abs_return:", period["return"].abs().mean())
print("Anomalies:", (period["prediction"] == -1).sum())
print()

print("Predictions:")
print(period["prediction"].value_counts())