import websocket
import json

def on_open(ws):
    print("connected to Binance")

trade_count = 0
total_volume = 0.0
printed_sample = False

window_start_time = None
window_trade_count = 0
window_volume = 0.0
WINDOW_SIZE = 10  # seconds

def on_message(ws, message):
    global trade_count, printed_sample, total_volume
    global window_start_time, window_trade_count, window_volume

    data = json.loads(message)
    trade_count += 1
    
    price = float(data["p"])
    quantity = float(data["q"])
    trade_time = data["T"] / 1000  # convert ms -> seconds

    total_volume += quantity

    # Initialize window start
    if window_start_time is None:
        window_start_time = trade_time

    # Window aggregation
    window_trade_count += 1
    window_volume += quantity

    # Print one sample message
    if not printed_sample:
        print("Sample message:")
        print(json.dumps(data, indent=2))
        printed_sample = True

    # Normal counter
    if trade_time - window_start_time >= WINDOW_SIZE:        
        if window_trade_count > 0:
            avg_size = window_volume / window_trade_count

            print(
                f"[10s window] trades={window_trade_count}, "
                f"volume={window_volume:.4f}, "            
                f"avg_trade_size={avg_size:.6f}, "
                f"last_price={price}"
            )

        # Reset window
        window_start_time = trade_time
        window_trade_count = 0
        window_volume = 0.0


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
