import csv
import statistics

# Load per-second trade counts
rates = []

with open("data/trade_rate.csv") as f:
    reader = csv.DictReader(f)
    for row in reader:
        rates.append(int(row["trades_per_sec"]))

print(f"Loaded {len(rates)} seconds of data\n")

# Candidate window sizes (seconds)
window_sizes = [1, 5, 10, 20, 30]

for w in window_sizes:
    windows = []

    # Aggregate into windows
    for i in range(0, len(rates), w):
        chunk = rates[i:i+w]
        if len(chunk) == w:   # ignore incomplete window at end
            windows.append(sum(chunk))

    if not windows:
        continue

    mean = statistics.mean(windows)
    std = statistics.stdev(windows) if len(windows) > 1 else 0
    cv = std / mean if mean != 0 else 0

    print(f"Window {w:>2}s | samples={len(windows):>3} | mean={mean:.1f} | std={std:.1f} | CV={cv:.3f}")
