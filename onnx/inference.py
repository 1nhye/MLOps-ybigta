# onnx/onnx_infer.py

import onnxruntime as ort
import numpy as np

session = None
input_name = None

def load_model(onnx_path: str):
    global session, input_name
    session = ort.InferenceSession(onnx_path)
    input_name = session.get_inputs()[0].name
    print(f"[INFO] ONNX model loaded. Input name: {input_name}")

def run_inference(input_data: list):
    global session, input_name
    if session is None:
        raise RuntimeError("Model not loaded.")

    input_array = np.array(input_data, dtype=np.float32)
    # 입력 shape이 (24, 5)라면 배치 차원 추가
    if input_array.ndim == 2:
        input_array = np.expand_dims(input_array, axis=0)
    if input_array.shape[1:] != (24, 5):
        raise ValueError(f"Input shape must be (batch, 24, 5), got {input_array.shape}")
    outputs = session.run(None, {input_name: input_array})
    return outputs[0].tolist()
