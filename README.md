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

Isolation Forest with feature standardization.

* Window features are standardized using **StandardScaler**
* Model trained after an initial buffer collection (**500 windows ≈ 2.8 hours**)
* **Rolling retrain every 100 windows (~33 minutes)** to handle concept drift
* Real-time scoring for each window
* Outputs anomaly prediction (-1 / 1) and anomaly score

Rolling retraining allows the model to adapt to evolving market regimes while maintaining a stable anomaly rate.

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

### 3. Model behavior after sensitivity tuning (contamination = 0.05)

Using a higher contamination level (~5%) increased the anomaly rate to ~16% and broadened the detection boundary.

Pre-move analysis on a full-day dataset (~5,494 scored windows):

| Group   | Mean abs move | vs Normal |
|---------|--------------|-----------|
| Normal  | 0.004649     | 1.00x     |
| IF-only | 0.006360     | 1.37x     |
| Both    | 0.008927     | 1.92x     |

**Statistical significance (Mann-Whitney U test):**
- if_only vs normal: p < 0.001 ✓
- both vs normal: p < 0.001 ✓

Signal is statistically significant across 5,494 windows.

Observations:

- **No volatility-only windows** were observed.
- All high-volatility periods were captured by Isolation Forest.
- IF-only anomalies (normal volatility but unusual trading behavior) still precede significantly larger future moves.
- When both volatility and behavioral signals coincide, the effect is strongest.

Interpretation:

The model now operates as a **broad market regime detector**, capturing both volatility spikes and behavioral structure changes rather than rare outliers.

> Findings are based on multiple sessions (up to ~5,500 windows). Signal strength remains consistent across extended data, though performance varies by market session.

### 4. Results after rolling retrain stabilization (GCP, full session)

After deploying the system on a persistent VM and enabling **rolling retraining**, the model was evaluated on ~4,700 scored windows collected during a full market session.

Rolling retraining uses:

- Buffer size: **500 windows (~2.8 hours)**
- Retrain interval: **100 windows (~33 minutes)**

This prevents concept drift and keeps the anomaly rate aligned with the configured contamination level.

Pre-move analysis results:

| Group    | Mean abs move | vs Normal |
|----------|--------------|-----------|
| Normal   | 0.003492     | 1.00x     |
| VOL-only | 0.008352     | 2.39x     |
| IF-only  | 0.004007     | 1.15x     |
| Both     | 0.008278     | 2.37x     |

Statistical significance (Mann-Whitney U test):

- IF-only vs normal: **p < 0.001 ✓**
- Both vs normal: **p < 0.001 ✓**

Observations:

- Rolling retraining stabilized the anomaly rate to **~2–9% across most hours**.
- **Volatility-driven anomalies** show strong predictive power (~2.39× larger future moves).
- **Combined behavioral + volatility anomalies** produce the strongest signal (~2.37×).
- **Behavior-only anomalies** show a smaller but statistically significant effect (~1.15×).

Interpretation:

The anomaly detector captures **market regime transitions** rather than isolated price spikes.

- Volatility signals capture **high-activity market states**.
- Behavioral signals capture **microstructure changes in trading activity**.
- When both signals occur together, they indicate **strong regime shifts** that precede larger price movement.

> These findings replicate earlier results on a new dataset collected after rolling retrain stabilization, confirming that the signal is not an artifact of model drift.

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
docker run -d \
  --name anomaly \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/reports:/app/reports \
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
python scripts/analysis/analyze_results.py
```

Score distribution:
```
python scripts/analysis/check_scores.py
```

Pre-move lead-lag validation:
```
python scripts/analysis/check_pre_move.py
```

Pre-move by anomaly type (three-group analysis):
```
python scripts/analysis/check_pre_move_by_type.py
```

Baseline comparison (IF vs volatility threshold):
```
python scripts/analysis/compare_baseline.py
```

Anomaly rate by hour:
```
python scripts/diagnostics/check_anomaly_by_hour.py
```

Results are appended to `reports/`.

---

## Project Structure
```
src/
    collector.py          # main streaming collector

scripts/
    analysis/
        analyze_results.py
        check_pre_move.py
        check_pre_move_by_type.py
        check_scores.py
        compare_baseline.py
    diagnostics/
        check_anomaly_by_hour.py
        measure_rate.py
    experiments/
        analyze_event_specific_time.py
        analyze_events.py
        analyze_window.py
        save_score_summary.py

data/
    raw/                  # collected results (gitignored)
    samples/              # sample data for reference

reports/                  # experiment logs
logs/                     # collector logs
docs/
```

---

## Notes

* Designed for long-running data collection
* Deployed on **GCP Compute Engine** for continuous 24/7 operation
* Raw data and logs are excluded from version control
* Current system focuses on **behavior-based anomaly detection**
* Future work: hour-of-day normalization, multi-horizon lookahead, order book features
