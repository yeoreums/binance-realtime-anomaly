import matplotlib.pyplot as plt

# results from your experiment
horizons = ["1m", "5m", "15m", "30m"]

vol_only = [2.18, 2.00, 1.89, 1.77]
if_only = [1.33, 1.18, 1.09, 1.05]
both = [2.35, 2.00, 1.79, 1.67]

plt.figure()

plt.plot(horizons, vol_only, marker='o', label="Volatility-only")
plt.plot(horizons, if_only, marker='o', label="IF-only (behavior)")
plt.plot(horizons, both, marker='o', label="Both")

plt.axhline(1.0, linestyle='--')

plt.title("Volatility Expansion After Detected Anomalies")
plt.xlabel("Future Horizon")
plt.ylabel("Future Volatility vs Normal (Ratio)")

plt.grid(True)
plt.legend()

plt.savefig("reports/multi_horizon_signal.png")