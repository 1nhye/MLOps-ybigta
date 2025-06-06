from fastapi import FastAPI, UploadFile, File, Request
import os
import shutil
from utils import BitcoinDataFetcher, ModelManager

# 데이터 및 모델 관리자 초기화
bitcoin_fetcher = BitcoinDataFetcher()
model_manager = ModelManager()

# FastAPI 앱 생성
api = FastAPI()

@api.get("/bitcoin")
async def get_bitcoin_data_endpoint():
    return bitcoin_fetcher.get_bitcoin_data()

@api.get("/model-info")
async def get_model_info():
    return model_manager.get_model_info()

@api.post("/upload_model")
async def upload_model(file: UploadFile = File(...)):
    # 저장 경로 만들기
    os.makedirs(os.path.dirname(model_manager.model_path), exist_ok=True)

    # 파일 저장
    with open(model_manager.model_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # 모델 로딩 (메모리에 올리기)
    model_manager.load_model()

    return {"status": "ONNX model uploaded and loaded"}

@api.post("/predict")
async def predict(request: Request):
    data = await request.json()
    input_data = data.get("input")
    if input_data is None:
        return {"error": "No input data provided"}
    try:
        result = model_manager.run_inference(input_data)
        return {"prediction": result}
    except Exception as e:
        return {"error": str(e)} 