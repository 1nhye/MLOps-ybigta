FROM pytorch/pytorch:2.2.0-cuda11.8-cudnn8-runtime

# 작업 디렉토리 설정정
WORKDIR /app

# 필요 파일 복사
COPY train.py .
COPY requirements.txt .
# COPY .env .

# 패키지 설치
RUN pip install --no-cache-dir -r requirements.txt

# SageMaker가 모델을 이 경로에 저장하기를 기대함
ENV SAGEMAKER_MODEL_DIR=/opt/ml/model
ENV SAGEMAKER_OUTPUT_DIR=/opt/ml/output

# train.py 실행이 기본 동작
ENTRYPOINT ["python", "train.py"]
 