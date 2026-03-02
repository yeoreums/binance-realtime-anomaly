import pandas as pd

# Load data
df = pd.read_csv("data/window_results.csv")

# Remove rows before model was trained (score = None)
df = df[df["score"].notna()]

print("Total scored windows:", len(df))
print()

print("Score statistics:")
print(df["score"].describe())
