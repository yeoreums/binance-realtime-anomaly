import websocket
import json
import csv

def on_open(ws):
    print("connected to Binance")

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
csv_file = open("trade_rate.csv", "w", newline="")
csv_writer = csv.writer(csv_file)
csv_writer.writerow(["event_time", "trades_per_sec"])

# =========================
# Measurement duration
# =========================
MEASURE_DURATION = 300  # seconds (5 minutes)
measure_start_time = None

def on_message(ws, message):
    global trade_count, total_volume, printed_sample
    global sec_start_time, sec_trade_count
    global measure_start_time
    global csv_file, csv_writer

    # Parse JSON message
    data = json.loads(message)
    trade_count += 1

    # Extract fields
    price = float(data["p"])
    quantity = float(data["q"])
    trade_time = data["T"] / 1000  # Binance event time (seconds)

    total_volume += quantity

    # =========================
    # Initialize measurement start
    # =========================
    if measure_start_time is None:
        measure_start_time = trade_time

    # =========================
    # Stop after duration
    # =========================
    if trade_time - measure_start_time >= MEASURE_DURATION:
        print("Measurement finished. Closing connection...")
        csv_file.close()   # >>> NEW
        ws.close()
        return

    # =========================
    # Print one sample message (schema check)
    # =========================
    if not printed_sample:
        print("Sample message:")
        print(json.dumps(data, indent=2))
        printed_sample = True

    # =========================
    # 1-second trade rate measurement
    # =========================
    if sec_start_time is None:
        sec_start_time = trade_time

    sec_trade_count += 1

    if trade_time - sec_start_time >= 1:
        print(f"1s rate: {sec_trade_count} trades/sec")

        # save to CSV
        csv_writer.writerow([trade_time, sec_trade_count])
        
        # reset 1-second counter
        sec_start_time = trade_time
        sec_trade_count = 0


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
