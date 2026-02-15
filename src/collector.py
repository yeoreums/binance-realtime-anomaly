import websocket
import json
from datetime import datetime
import statistics

# =========================
# Configuration
# =========================
WINDOW_SIZE = 20  # seconds


def on_open(ws):
    print("connected to Binance")


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
    ws = websocket.WebSocketApp(
        "wss://stream.binance.com:9443/ws/btcusdt@trade",
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close,
    )

    ws.run_forever()
