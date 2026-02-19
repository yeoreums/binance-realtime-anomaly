# Binance Realtime Anomaly Detection

Realtime anomaly detection on BTCUSDT trades using Binance WebSocket, window-based feature engineering, and Isolation Forest.

## Overview

This project streams live trade data from Binance and aggregates it into time windows.
For each window, market activity features are calculated and evaluated using an anomaly detection model.

The system is designed to run continuously and collect data for analysis and model calibration.

---

## Features

**Data source**

* Binance WebSocket: `btcusdt@trade`
* Uses exchange event timestamp (not system time)

**Window aggregation (20s)**

* Trade count
* Total volume
* Average trade size
* Price return
* Price volatility

**Model**

* StandardScaler
* Isolation Forest
* Trained after initial buffer
* Real-time scoring per window

**Output**

* Results saved to:

```
data/window_results.csv
```

---

## Setup

Create virtual environment and install dependencies:

```
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## Run Collector

Run in background:

```
nohup python -u src/collector.py > collector.log 2>&1 &
```

Monitor logs:

```
tail -f collector.log
```

Check data growth:

```
wc -l data/window_results.csv
```

Stop the process:

```
ps aux | grep collector.py
kill <PID>
```

---

## Analysis Scripts

Save score summary:

```
python scripts/save_score_summary.py
```

Check anomaly rate:

```
python scripts/analyze_results.py
```

Check score distribution:

```
python scripts/check_scores.py
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

data/        # collected results (gitignored)
analysis/    # experiment summaries
collector.log
```

---

## Notes

* Window size selected based on data variability analysis (CV)
* Designed for long-running data collection
* Logs and raw data are excluded from version control
* Model sensitivity is evaluated through score distribution and anomaly rate
