import pandas as pd

df = pd.read_csv("data/window_results.csv")

# Keep only scored rows
df = df[df["prediction"].notna()]

total = len(df)
anomalies = df[df["prediction"] == -1]
normal = df[df["prediction"] == 1]

print(f"Total windows: {total}")
print(f"Anomalies: {len(anomalies)}")
print(f"Anomaly rate: {len(anomalies)/total:.4f}")
print()

print("Feature comparison (mean):")
print("                 normal    anomaly")
print(f"trade_count     {normal['trade_count'].mean():.1f}    {anomalies['trade_count'].mean():.1f}")
print(f"volume          {normal['volume'].mean():.4f}    {anomalies['volume'].mean():.4f}")
print(f"avg_trade_size  {normal['avg_trade_size'].mean():.6f}    {anomalies['avg_trade_size'].mean():.6f}")
print(f"abs_return      {normal['return'].abs().mean():.6f}    {anomalies['return'].abs().mean():.6f}")
print(f"volatility      {normal['volatility'].mean():.4f}    {anomalies['volatility'].mean():.4f}")
