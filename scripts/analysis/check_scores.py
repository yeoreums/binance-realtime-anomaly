import pandas as pd
import glob
import sys

files = glob.glob("data/window_results_*.csv")

if not files:
    print("No data files found")
    sys.exit()

latest_file = max(files)
print("Reading:", latest_file)

df = pd.read_csv(latest_file)
df = df[df["score"].notna()]

print("Total scored windows:", len(df))
print()
print(df["score"].describe())
