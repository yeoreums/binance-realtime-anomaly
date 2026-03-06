import pandas as pd
from datetime import datetime

# Load data
today = datetime.now().strftime("%Y-%m-%d")
df = pd.read_csv(f"data/window_results_{today}.csv")

# Remove rows before model was trained (score = None)
df = df[df["score"].notna()]

print("Total scored windows:", len(df))
print()

print("Score statistics:")
print(df["score"].describe())
