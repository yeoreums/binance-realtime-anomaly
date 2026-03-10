import pandas as pd
import numpy as np
from scipy.stats import mannwhitneyu
from datetime import datetime
import os

FILE = "data/raw/window_results_2026-03-06.csv"

# horizons in windows (20s window)
HORIZONS = {
    "1m": 3,
    "5m": 15,
    "15m": 45,
    "30m": 90
}

os.makedirs("reports", exist_ok=True)

log_file = "reports/multi_horizon_log.txt"


def log_print(msg, log):
    print(msg)
    log.write(msg + "\n")


with open(log_file, "a") as log:

    log_print("\n==================================================", log)
    log_print(f"Timestamp: {datetime.now()}", log)
    log_print("==================================================", log)

    df = pd.read_csv(FILE)

    log_print(f"Reading file: {FILE}", log)
    log_print(f"Total rows: {len(df)}", log)

    # keep rows where prediction exists
    df = df[df["prediction"].notna()].reset_index(drop=True)

    log_print(f"Windows with predictions: {len(df)}", log)

    for label, lookahead in HORIZONS.items():

        log_print("\n----------------------------------", log)
        log_print(f"Horizon: {label} ({lookahead} windows)", log)
        log_print("----------------------------------", log)

        moves = []

        for i in range(len(df) - lookahead):

            future_returns = df["return"].iloc[i+1:i+lookahead+1]
            future_move = np.sum(np.abs(future_returns))

            moves.append(future_move)

        df_slice = df.iloc[:len(moves)].copy()
        df_slice["future_move"] = moves

        # volatility threshold
        vol_threshold = df_slice["volatility"].mean() + 2 * df_slice["volatility"].std()

        groups = []

        for _, row in df_slice.iterrows():

            if row["prediction"] == -1 and row["volatility"] >= vol_threshold:
                groups.append("both")

            elif row["prediction"] == -1:
                groups.append("if_only")

            elif row["volatility"] >= vol_threshold:
                groups.append("vol_only")

            else:
                groups.append("normal")

        df_slice["group"] = groups

        group_stats = df_slice.groupby("group")["future_move"].mean()

        log_print("\nMean future move:", log)

        for g in ["normal", "vol_only", "if_only", "both"]:
            if g in group_stats:
                log_print(f"{g:10s}: {group_stats[g]:.6f}", log)

        if "normal" in group_stats:

            base = group_stats["normal"]

            log_print("\nRatio vs normal:", log)

            for g in ["vol_only", "if_only", "both"]:
                if g in group_stats:
                    ratio = group_stats[g] / base
                    log_print(f"{g:10s}: {ratio:.2f}x", log)

        normal_moves = df_slice[df_slice["group"] == "normal"]["future_move"]

        log_print("\nStatistical significance:", log)

        for g in ["vol_only", "if_only", "both"]:

            if g in df_slice["group"].values:

                group_moves = df_slice[df_slice["group"] == g]["future_move"]

                stat, p = mannwhitneyu(group_moves, normal_moves)

                log_print(f"{g} vs normal p-value: {p:.6f}", log)