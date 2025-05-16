from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
import requests

app = FastAPI()
app.mount("/", StaticFiles(directory="web", html=True), name="static")

@app.post("/predict")
async def predict(request: Request):
    body = await request.json()
    response = requests.post("http://torchserve-container:8080/predictions/stock_predictor", json=body)
    return {"prediction": response.json()}
