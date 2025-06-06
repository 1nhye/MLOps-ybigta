# onnx/onnx_infer.py

import onnxruntime as ort
import numpy as np

session = None

def load_model(onnx_path: str):
    global session
    session = ort.InferenceSession(onnx_path)
    print("[INFO] ONNX model loaded.")

def run_inference(input_data: list):
    global session
    if session is None:
        raise RuntimeError("Model not loaded.")

    input_array = np.array(input_data, dtype=np.float32)
    outputs = session.run(None, {"input": input_array})
    return outputs[0].tolist()
