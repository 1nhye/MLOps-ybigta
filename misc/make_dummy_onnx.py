import torch
import torch.nn as nn
import numpy as np
import os

# ---------- 모델 정의 ----------
class NLinear(nn.Module):
    def __init__(self, input_size, window_size):
        super().__init__()
        self.linear = nn.Linear(window_size * input_size, 1)

    def forward(self, x):  # (B, T, F)
        x = x.view(x.size(0), -1)  # (B, T*F)
        return self.linear(x)  # (B, 1)

# ---------- 임의의 데이터 생성 ----------
N = 100  # 샘플 개수
T = 24   # 시간 구간
F = 5    # feature 개수

x = np.random.rand(N, T, F).astype(np.float32)
y = np.random.rand(N, 1).astype(np.float32)

x_tensor = torch.tensor(x)
y_tensor = torch.tensor(y)

# ---------- 모델 학습 ----------
model = NLinear(input_size=F, window_size=T)
criterion = nn.MSELoss()
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

for epoch in range(5):
    optimizer.zero_grad()
    pred = model(x_tensor)
    loss = criterion(pred, y_tensor)
    loss.backward()
    optimizer.step()
    print(f"Epoch {epoch+1}: Loss = {loss.item():.4f}")

# ---------- ONNX 변환 ----------
os.makedirs("models", exist_ok=True)
onnx_path = "models/model.onnx"

dummy_input = torch.randn(1, T, F, dtype=torch.float32)
torch.onnx.export(
    model,
    dummy_input,
    onnx_path,
    input_names=["input"],
    output_names=["output"],
    dynamic_axes={"input": {0: "batch_size"}, "output": {0: "batch_size"}},
    opset_version=12
)
print(f"✅ ONNX 모델 저장 완료: {onnx_path}")