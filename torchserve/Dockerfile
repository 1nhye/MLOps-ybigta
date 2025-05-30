FROM pytorch/torchserve:latest

# 모델 스토어와 설정 복사
COPY model_store/ /home/model-server/model-store/
COPY config.properties /home/model-server/

# TorchServe 실행
CMD ["torchserve", "--start", \
     "--model-store", "/home/model-server/model-store", \
     "--models", "stock_predictor=stock_predictor.mar", \
     "--ts-config", "/home/model-server/config.properties"]
