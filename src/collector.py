import websocket
import json
from datetime import datetime
import statistics
from sklearn.ensemble import IsolationForest
import numpy as np
import csv
from sklearn.preprocessing import StandardScaler
import time

result_file = open("data/window_results.csv", "a", newline="")
result_writer = csv.writer(result_file)

# write header if file empty
if result_file.tell() == 0:
    result_writer.writerow([
        "timestamp",
        "trade_count",
        "volume",
        "avg_trade_size",
        "return",
        "volatility",
        "score",
        "prediction"
    ])


# =========================
# Model
# =========================
model = None
scaler = None
MODEL_TRAINED = False

# =========================
# Configuration
# =========================
WINDOW_SIZE = 20  # seconds


def on_open(ws):
    print("connected to Binance")

# =========================
# Feature buffer (for model training later)
# =========================
BUFFER_SIZE = 100
feature_buffer = []

# =========================
# Window state
# =========================
window_start_time = None
window_trade_count = 0
window_volume = 0.0
window_prices = []


def reset_window(trade_time):
    global window_start_time, window_trade_count, window_volume, window_prices

    window_start_time = trade_time
    window_trade_count = 0
    window_volume = 0.0
    window_prices = []


def process_window(last_price):
    global window_trade_count, window_volume, window_prices
    global model, scaler, MODEL_TRAINED

    if window_trade_count == 0:
        return

    avg_trade_size = window_volume / window_trade_count

    # Price return
    price_return = (
        (window_prices[-1] - window_prices[0]) / window_prices[0]
        if len(window_prices) > 1
        else 0
    )

    # Volatility
    volatility = (
        statistics.stdev(window_prices)
        if len(window_prices) > 1
        else 0
    )

    print(
        f"[20s window] "
        f"time={datetime.now().strftime('%H:%M:%S')} "
        f"trades={window_trade_count} "
        f"volume={window_volume:.4f} "
        f"avg_size={avg_trade_size:.6f} "
        f"return={price_return:.6f} "
        f"volatility={volatility:.4f}"
    )

    feature_vector = [
        window_trade_count,
        window_volume,
        avg_trade_size,
        price_return,
        volatility,
    ]

    feature_buffer.append(feature_vector)

    if len(feature_buffer) > BUFFER_SIZE:
        feature_buffer.pop(0)

    print(f"buffer_size={len(feature_buffer)}")    

    # Train model when buffer is full (once)
    if not MODEL_TRAINED and len(feature_buffer) == BUFFER_SIZE:
        print("Training Isolation Forest with StandardScaler...")

        # Initialize scaler
        scaler = StandardScaler()
        X = np.array(feature_buffer)

        # Fit scaler and transform data
        X_scaled = scaler.fit_transform(X)

        # Train model
        model = IsolationForest(
            n_estimators=100,
            contamination=0.05,     # updated from 0.01, matches observed anomaly rate
            random_state=42
        )
        model.fit(X_scaled)

        MODEL_TRAINED = True
        print("Model trained")

    # Predict anomaly for current window
    prediction = None
    score = None
    
    if MODEL_TRAINED:
        X_current = np.array([feature_vector])

        # Scale using the same scaler
        X_scaled = scaler.transform(X_current)

        prediction = model.predict(X_scaled)[0]
        score = model.decision_function(X_scaled)[0]

        if prediction == -1:
            print(f"⚠️ ANOMALY detected | score={score:.4f}")
        else:
            print(f"normal | score={score:.4f}")

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    result_writer.writerow([
        timestamp,
        window_trade_count,
        window_volume,
        avg_trade_size,
        price_return,
        volatility,
        score,
        prediction
    ])

    result_file.flush()


def on_message(ws, message):
    global window_start_time, window_trade_count, window_volume, window_prices

    data = json.loads(message)

    price = float(data["p"])
    quantity = float(data["q"])
    trade_time = data["T"] / 1000  # event time

    # Initialize window
    if window_start_time is None:
        reset_window(trade_time)

    # Check if window ended
    if trade_time - window_start_time >= WINDOW_SIZE:
        process_window(price)
        reset_window(trade_time)

    # Aggregate trade
    window_trade_count += 1
    window_volume += quantity
    window_prices.append(price)


def on_error(ws, error):
    print("error:", error)


def on_close(ws, close_status_code, close_msg):
    print("connection closed")


if __name__ == "__main__":
    url = "wss://stream.binance.com:9443/ws/btcusdt@trade"

    while True:
        print("Starting WebSocket connection...")

        ws = websocket.WebSocketApp(
            url,
            on_open=on_open,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close,
        )

        try:
            ws.run_forever()
        except Exception as e:
            print("run_forever exception:", e)

        print("Connection lost. Reconnecting in 5 seconds...")
        time.sleep(5)

    result_file.close()
    print("Result file closed.")