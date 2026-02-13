import websocket
import json

def on_open(ws):
    print("connected to Binance")

trade_count = 0
total_volume = 0.0
printed_sample = False

def on_message(ws, message):
    global trade_count, printed_sample, total_volume
    data = json.loads(message)
    trade_count += 1
    
    price = float(data["p"])
    quantity = float(data["q"])
    total_volume += quantity

    # Print one sample message
    if not printed_sample:
        print("Sample message:")
        print(json.dumps(data, indent=2))
        printed_sample = True

    # Normal counter
    if trade_count % 100 == 0:
        avg_size = total_volume / trade_count

        print(
            f"trades={trade_count}, "
            f"last_price={price}, "
            f"total_volume={total_volume:.4f}, "
            f"avg_trade_size={avg_size:.6f}"
        )

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
