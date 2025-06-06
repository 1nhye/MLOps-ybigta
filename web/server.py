from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from api import api

app = FastAPI()

# API 라우터 마운트
app.mount("/api", api)

# 정적 파일 서빙
app.mount("/", StaticFiles(directory="web", html=True), name="static")
