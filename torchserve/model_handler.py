import torch
from ts.torch_handler.base_handler import BaseHandler

class StockPredictorHandler(BaseHandler):
    def __init__(self):
        super().__init__()
        self.initialized = False

    def initialize(self, context):
        self.manifest = context.manifest
        properties = context.system_properties
        model_dir = properties.get("model_dir")
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = torch.jit.load(f"{model_dir}/model.pt")
        self.model.to(self.device)
        self.model.eval()
        self.initialized = True

    def preprocess(self, data):
        input_data = data[0]['body']
        tensor = torch.tensor(input_data, dtype=torch.float32).to(self.device)
        return tensor.unsqueeze(0)  # (1, 24, 5)

    def inference(self, input_tensor):
        with torch.no_grad():
            output = self.model(input_tensor)
        return output

    def postprocess(self, inference_output):
        return [inference_output.item()]
