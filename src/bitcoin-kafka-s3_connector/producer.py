import json, time, requests, os
from kafka import KafkaProducer

producer = KafkaProducer(
    bootstrap_servers=os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka:9092'),
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

def fetch_btc_minute_candle():
    url = "https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=1m&limit=1"
    r = requests.get(url)
    kline = r.json()[0]
    return {
        "symbol": "BTCUSDT",
        "open_time": int(kline[0]),
        "open": float(kline[1]),
        "high": float(kline[2]),
        "low": float(kline[3]),
        "close": float(kline[4]),
        "volume": float(kline[5]),
        "close_time": int(kline[6]),
        "quote_asset_volume": float(kline[7]),
        "number_of_trades": int(kline[8]),
        "taker_buy_base_asset_volume": float(kline[9]),
        "taker_buy_quote_asset_volume": float(kline[10]),
        "timestamp": int(kline[0])
    }

last_open_time = None
print("🚀 바이낸스 데이터 프로듀서 시작...")

while True:
    try:
        data = fetch_btc_minute_candle()
        if data["open_time"] != last_open_time:
            # 구조화된 데이터를 직접 토픽으로 전송
            producer.send('btc_1m_kline_structured', value=data)
            print(f"✅ 데이터 전송: {data}")
            last_open_time = data["open_time"]
        time.sleep(5)
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        time.sleep(5) 