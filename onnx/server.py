# onnx/server.py

from fastapi import FastAPI, UploadFile, File, Request
import os
import shutil
from inference import load_model, run_inference

app = FastAPI()

ONNX_MODEL_PATH = "models/model.onnx"

@app.post("/upload_model")
async def upload_model(file: UploadFile = File(...)):
    # 저장 경로 만들기
    os.makedirs(os.path.dirname(ONNX_MODEL_PATH), exist_ok=True)

    # 파일 저장
    with open(ONNX_MODEL_PATH, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # 모델 로딩 (메모리에 올리기)
    load_model(ONNX_MODEL_PATH)

    return {"status": "ONNX model uploaded and loaded"}

@app.post("/predict")
async def predict(request: Request):
    data = await request.json()
    input_data = data.get("input")
    if input_data is None:
        return {"error": "No input data provided"}
    try:
        result = run_inference(input_data)
        return {"result": result}
    except Exception as e:
        return {"error": str(e)}
