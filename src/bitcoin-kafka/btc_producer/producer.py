import json, time, requests, os
from kafka import KafkaProducer

producer = KafkaProducer(
    bootstrap_servers=os.environ["BOOTSTRAP_SERVERS"],
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

def fetch_btc_minute_candle():
    url = "https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=1m&limit=1"
    r = requests.get(url)
    kline = r.json()[0]
    return {
        "symbol": "BTC/USDT",
        "open_time": kline[0],
        "open": float(kline[1]),
        "high": float(kline[2]),
        "low": float(kline[3]),
        "close": float(kline[4]),
        "volume": float(kline[5]),
        "close_time": kline[6]
    }

last_open_time = None
while True:
    try:
        data = fetch_btc_minute_candle()
        if data["open_time"] != last_open_time:
            producer.send(os.environ["TOPIC_NAME"], value=data)
            print("Produced:", data)
            last_open_time = data["open_time"]
        time.sleep(5)
    except Exception as e:
        print("Error:", e)
        time.sleep(5)
