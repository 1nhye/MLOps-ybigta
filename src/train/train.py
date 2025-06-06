import os
import json
import argparse
import boto3
import mlflow
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from datetime import datetime
from dotenv import load_dotenv
from torch.utils.data import DataLoader, TensorDataset

# ---------- 데이터 로드 ----------
def load_data_from_s3(bucket: str, prefix: str):
    s3 = boto3.client("s3")
    response = s3.list_objects_v2(Bucket=bucket, Prefix=prefix)

    all_features = []
    all_targets = []

    for obj in response.get("Contents", []):
        key = obj["Key"]
        if not key.endswith(".json"):
            continue
        obj_body = s3.get_object(Bucket=bucket, Key=key)['Body'].read()
        try:
            data = json.loads(obj_body.decode('utf-8'))
            features = np.array(data["features"], dtype=np.float32).reshape(1, 24, 5)  # (1, 24, 5)
            target = np.array([[data["target"]]], dtype=np.float32)  # (1, 1)
            all_features.append(features)
            all_targets.append(target)
        except Exception as e:
            print(f"❌ Failed to parse {key}: {e}")
            continue

    if not all_features:
        raise ValueError("No valid data found in S3.")

    x = np.concatenate(all_features, axis=0)  # (N, 24, 5)
    y = np.concatenate(all_targets, axis=0)  # (N, 1)

    return torch.tensor(x), torch.tensor(y)


# ---------- 모델 정의 ----------
## 지갑이 가볍?무겁?가벼우면서무거?워지는...Linear...
class NLinear(nn.Module):
    def __init__(self, input_size, output_size):
        super().__init__()
        self.linear = nn.Linear(output_size * input_size, 1)

    def forward(self, x):  # (B, T, F)
        x = x.view(x.size(0), -1)  # (B, T*F)
        return self.linear(x)  # (B, 1)
    
# ---------- 학습 ----------
def train(x_tensor, y_tensor):
    dataset = TensorDataset(x_tensor, y_tensor)
    dataloader = DataLoader(dataset, batch_size=16, shuffle=True)

    model = NLinear(input_size=5, window_size=24)
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)

    mlflow.start_run()
    for epoch in range(10):
        total_loss = 0.0
        for xb, yb in dataloader:
            pred = model(xb)
            loss = criterion(pred, yb)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            total_loss += loss.item()

        avg_loss = total_loss / len(dataloader)
        print(f"Epoch {epoch+1}: Loss = {avg_loss:.4f}")
        mlflow.log_metric("loss", avg_loss, step=epoch)

    mlflow.pytorch.log_model(model, "model")
    mlflow.end_run()
    return model

# ---------- 메인 ----------
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--bucket", type=str, required=True)
    parser.add_argument("--prefix", type=str, required=True)
    args = parser.parse_args()

    load_dotenv()
    mlflow_uri = os.getenv("MLFLOW_TRACKING_URI")
    mlflow.set_tracking_uri(mlflow_uri)

    print(f"📥 Loading data from s3://{args.bucket}/{args.prefix}")
    x_tensor, y_tensor = load_data_from_s3(args.bucket, args.prefix)

    print(f"🧠 Training NLinear model on {len(x_tensor)} samples...")
    model = train(x_tensor, y_tensor)

    output_dir = os.environ.get("SAGEMAKER_MODEL_DIR", "/opt/ml/model")
    os.makedirs(output_dir, exist_ok=True)
    model_path = os.path.join(output_dir, "model.pth")
    torch.save(model.state_dict(), model_path)
    print(f"✅ 모델 저장 완료: {model_path}")