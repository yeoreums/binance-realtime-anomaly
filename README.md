# Binance Realtime Anomaly Detection

Realtime anomaly detection on BTCUSDT using Binance WebSocket, window-based feature engineering, and Isolation Forest.

This project builds a continuous market monitoring system and validates whether detected anomalies lead to abnormal future market movement.

---

## Overview

Live trade data is streamed from Binance and aggregated into fixed time windows.
For each window, market activity features are calculated and evaluated using an anomaly detection model.

The system runs continuously to collect long-horizon data for signal validation.

Goal:

Detect **market regime changes** (unusual activity) and evaluate whether they precede increased price movement.

---

## Motivation

This project was inspired by limitations observed in a previous real-time monitoring system built on Upbit trade streams.

The earlier system relied on SMA-based thresholds for anomaly detection, which worked for basic price monitoring but produced frequent false signals and failed to capture sudden market regime changes driven by trading activity rather than price level.

That system was part of the following project:
[Upbit Data Pipeline (team project)](https://github.com/DE7-team6-final/upbit-data-pipeline)

Based on these observations, the current system focuses on **behavior-based detection**, using trade intensity, volume, and volatility features combined with an unsupervised anomaly detection model.

The objective is to detect **market activity regime shifts** and validate whether these events precede abnormal future price movement.

---

## Data Source

* Binance WebSocket: `btcusdt@trade`
* Uses **exchange event timestamp** (not system time)

---

## Window Features (20 seconds)

For each window:

* Trade count
* Total volume
* Average trade size
* Price return
* Price volatility

Window size was selected based on variability analysis (coefficient of variation).

---

## Model

Isolation Forest

* Trained after initial buffer collection
* Real-time scoring for each window
* Outputs anomaly prediction (-1 / 1) and score

Results saved to:

```
data/window_results.csv
```

---

## Key Finding (Signal Validation)

Pre-move analysis shows:

After anomaly windows, the **average absolute price move in the next 5 minutes is ~2× larger** than normal periods.

Interpretation:

The model detects **volatility regime shifts**, not direction.

This acts as a **market risk / activity signal** rather than a trading signal.

---

## Setup

Create environment and install dependencies:

```
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## Run Collector

Run continuously in background:

```
nohup python -u src/collector.py > collector.log 2>&1 &
```

Monitor:

```
tail -f collector.log
wc -l data/window_results.csv
```

Stop:

```
ps aux | grep collector.py
kill <PID>
```

---

## Analysis Scripts

Anomaly statistics:

```
python scripts/analyze_results.py
```

Score distribution:

```
python scripts/check_scores.py
```

Save score summary:

```
python scripts/save_score_summary.py
```

Pre-move (lead-lag validation):

```
python scripts/check_pre_move.py
```

Results are appended to:

```
reports/pre_move_log.txt
```

---

## Project Structure

```
src/
    collector.py

scripts/
    analyze_results.py
    check_scores.py
    save_score_summary.py
    check_pre_move.py

data/        # collected results (gitignored)
reports/     # experiment logs
collector.log
```

---

## Notes

* Designed for long-running data collection
* Raw data and logs are excluded from version control
* Current system focuses on **behavior-based anomaly detection**
* Future work: horizon comparison, directional analysis, feature expansion
