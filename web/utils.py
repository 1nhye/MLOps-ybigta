from binance.client import Client
from datetime import datetime
import numpy as np
import onnxruntime as ort

class BitcoinDataFetcher:
    def __init__(self):
        self.client = Client()
        self.session = None
        self.input_name = None
        self.last_trained = None
        self.model_path = "models/model.onnx"

    def get_bitcoin_data(self):
        try:
            # 최근 3시간의 1분봉 데이터 가져오기 (180개)
            klines = self.client.get_klines(
                symbol='BTCUSDT',
                interval=Client.KLINE_INTERVAL_1MINUTE,
                limit=180
            )
            
            # 현재 가격 가져오기
            ticker = self.client.get_symbol_ticker(symbol='BTCUSDT')
            current_price = float(ticker['price'])
            
            # 데이터 전처리
            processed_data = []
            chart_data = {
                'timestamps': [],
                'prices': []
            }
            
            for k in klines:
                # OHLCV 데이터 추출 (Open, High, Low, Close, Volume)
                processed_data.append([
                    float(k[1]),  # Open
                    float(k[2]),  # High
                    float(k[3]),  # Low
                    float(k[4]),  # Close
                    float(k[5])   # Volume
                ])
                
                # 차트 데이터 추가
                chart_data['timestamps'].append(k[0])  # Open time
                chart_data['prices'].append(float(k[4]))  # Close price
            
            return {
                "price": f"{current_price:,.2f} USDT",
                "input": processed_data[-24:],  # 최근 24개 데이터만 예측에 사용
                "chart_data": chart_data
            }
        except Exception as e:
            print(f"Error fetching Bitcoin data: {e}")
            return {
                "price": "Error fetching price",
                "input": [[0.0] * 5 for _ in range(24)],
                "chart_data": {
                    "timestamps": [],
                    "prices": []
                }
            }

class ModelManager:
    def __init__(self):
        self.session = None
        self.input_name = None
        self.last_trained = None
        self.model_path = "models/model.onnx"

    def load_model(self):
        self.session = ort.InferenceSession(self.model_path)
        self.input_name = self.session.get_inputs()[0].name
        self.last_trained = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[INFO] ONNX model loaded. Input name: {self.input_name}")

    def run_inference(self, input_data: list):
        if self.session is None:
            raise RuntimeError("Model not loaded.")

        input_array = np.array(input_data, dtype=np.float32)
        # 입력 shape이 (24, 5)라면 배치 차원 추가
        if input_array.ndim == 2:
            input_array = np.expand_dims(input_array, axis=0)
        if input_array.shape[1:] != (24, 5):
            raise ValueError(f"Input shape must be (batch, 24, 5), got {input_array.shape}")
        outputs = self.session.run(None, {self.input_name: input_array})
        return outputs[0].tolist()

    def get_model_info(self):
        return {
            "last_trained": self.last_trained,
            "model_loaded": self.session is not None
        } 