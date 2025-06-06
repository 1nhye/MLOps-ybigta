from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
import requests

app = FastAPI()
app.mount("/static", StaticFiles(directory="web", html=True), name="static")

#ONNX_SERVER_URL = "http://onnx-server:8000/predict" 
ONNX_SERVER_URL = "http://127.0.0.1:8000/predict"

@app.post("/predict")
async def predict(request: Request):
    body = await request.json()
    # 필요하다면 model_name 등도 body에 추가
    response = requests.post(ONNX_SERVER_URL, json=body)
    return {"prediction": response.json()}
