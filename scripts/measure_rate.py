import websocket
import json
import csv
import time
from datetime import datetime, timedelta

def on_open(ws):
    print("connected to Binance")

# =========================
# Runtime tracking
# =========================
start_time = time.time()
print("Run started at:", datetime.now())

# =========================
# Overall counters
# =========================
trade_count = 0
total_volume = 0.0
printed_sample = False

# =========================
# 1-second measurement
# =========================
sec_start_time = None
sec_trade_count = 0

# =========================
# CSV setup
# =========================
csv_file = open("data/trade_rate_long.csv", "a", newline="")   # >>> FIX (append mode)
csv_writer = csv.writer(csv_file)

# Write header only if file is empty
if csv_file.tell() == 0:
    csv_writer.writerow(["event_time", "trades_per_sec"])

def on_message(ws, message):
    global trade_count, total_volume, printed_sample
    global sec_start_time, sec_trade_count
    global csv_file, csv_writer

    # Parse JSON message
    data = json.loads(message)
    trade_count += 1

    # Extract fields
    price = float(data["p"])
    quantity = float(data["q"])
    trade_time = data["T"] / 1000  # Binance event time (seconds)

    total_volume += quantity

    # Print one sample message
    if not printed_sample:
        print("Sample message:")
        print(json.dumps(data, indent=2))
        printed_sample = True

    # 1-second trade rate measurement
    if sec_start_time is None:
        sec_start_time = trade_time

    sec_trade_count += 1

    if trade_time - sec_start_time >= 1:
        print(f"1s rate: {sec_trade_count} trades/sec")

        # save to CSV
        csv_writer.writerow([trade_time, sec_trade_count])
        csv_file.flush()      # >>> NEW (important for long runs)

        # reset counter
        sec_start_time = trade_time
        sec_trade_count = 0


def on_error(ws, error):
    print("error:", error)


def on_close(ws, close_status_code, close_msg):
    print("connection closed")


if __name__ == "__main__":
    try:
        ws = websocket.WebSocketApp(
            "wss://stream.binance.com:9443/ws/btcusdt@trade",
            on_open=on_open,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close,
        )
        ws.run_forever()

    except KeyboardInterrupt:
        print("\nInterrupted by user")

    finally:
        # >>> NEW: runtime summary
        end_time = time.time()
        duration = int(end_time - start_time)

        print("Run stopped at:", datetime.now())
        print("Total runtime:", timedelta(seconds=duration))

        csv_file.close()
