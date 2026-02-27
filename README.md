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

Results saved daily to:

```
data/window_results_YYYY-MM-DD.csv
```

Daily rotation prevents unbounded file growth and supports long-running collection.

---

## Key Findings (Signal Validation)

### 1. Isolation Forest detects behavioral anomalies beyond volatility
A baseline comparison against a simple volatility threshold (mean + 2×std) shows:
- 55 windows flagged by both methods
- 27 windows flagged by IF only (normal volatility, unusual trade behavior)
- Jaccard similarity: 0.567

33% of IF anomalies occur in normal-volatility conditions, indicating the model
captures order-flow microstructure signals invisible to threshold-based methods.

### 2. All anomaly types precede larger future price moves (5-min lookahead)

| Group    | Mean abs move | vs Normal |
|----------|--------------|-----------|
| Normal   | 0.005511     | 1.00x     |
| VOL-only | 0.009147     | 1.66x     |
| IF-only  | 0.008027     | 1.46x     |
| Both     | 0.010719     | 1.94x     |

IF-only anomalies — detected during calm volatility — precede 1.46× larger moves
than baseline. When both signals coincide, the effect reaches 1.94×.

Interpretation:
The model detects **behavioral regime shifts** (order fragmentation, activity bursts),
not just price volatility. This acts as a **market activity signal** rather than a
directional trading signal.

> Note: Based on ~1,849 windows (one session). Findings are preliminary pending
> longer data collection.

---

## Setup

Create environment and install dependencies:

```
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## Run with Docker (recommended)

Build image:

```
docker build -t binance-realtime-anomaly .
```

Run continuously in background:

```
docker run -d
--name anomaly
-v $(pwd)/data:/app/data
-v $(pwd)/reports:/app/reports
binance-realtime-anomaly
```

view logs:
```
docker logs -f anomaly
```

Stop:
```
docker stop anomaly
docker rm anomaly    # removes container instance (data is preserved)
```


Collected data is stored locally under the `data/` directory.

---

### Run locally (optional)

```
nohup python -u src/collector.py > collector.log 2>&1 &
```

This mode is mainly for development.

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
Baseline comparison (IF vs volatility threshold):
```
python scripts/baseline_comparison.py
```
Results are appended to:
```
reports/baseline_comparison_log.txt
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
* Future work: extended data collection, hour-of-day normalization, contamination retuning, directional analysis
