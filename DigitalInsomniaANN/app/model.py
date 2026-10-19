import os
import sys
import pickle
import torch
import torch.nn as nn
import pandas as pd
import numpy as np

# Compatibility shim for scikit-learn version differences (e.g. 1.6.1 -> 1.9+)
import sklearn.compose._column_transformer as ct
if not hasattr(ct, '_RemainderColsList'):
    class _RemainderColsList(list):
        pass
    ct._RemainderColsList = _RemainderColsList

# ANN Architecture matching the trained weights
class InsomniaANN(nn.Module):
    def __init__(self, in_features=31, out_features=3):
        super().__init__()
        self.linear_layer_stack = nn.Sequential(
            nn.Linear(in_features, 15),
            nn.ReLU(),
            nn.Linear(15, 15),
            nn.ReLU(),
            nn.Linear(15, out_features)
        )

    def forward(self, x):
        return self.linear_layer_stack(x)

class ModelService:
    def __init__(self, base_dir: str):
        self.base_dir = base_dir
        self.model = None
        self.preprocessor = None
        self.target_mappings = None
        self.inv_mappings = None
        self.load_artifacts()

    def load_artifacts(self):
        # 1. Load target mappings
        mapping_path = os.path.join(self.base_dir, "target_mappings.pkl")
        with open(mapping_path, "rb") as f:
            self.target_mappings = pickle.load(f)
        self.inv_mappings = {v: k for k, v in self.target_mappings.items()}

        # 2. Load preprocessor
        prep_path = os.path.join(self.base_dir, "preprocessor.pkl")
        with open(prep_path, "rb") as f:
            self.preprocessor = pickle.load(f)

        # 3. Load model weights
        model_path = os.path.join(self.base_dir, "digital_insomnia_nn_model.pth")
        self.model = InsomniaANN(in_features=31, out_features=len(self.target_mappings))
        state_dict = torch.load(model_path, map_location=torch.device("cpu"))
        self.model.load_state_dict(state_dict)
        self.model.eval()

    def predict(self, input_dict: dict) -> dict:
        """
        Takes input dictionary matching the 21 features, transforms with preprocessor,
        runs through PyTorch model, and returns predicted class and probabilities.
        """
        df = pd.DataFrame([input_dict])
        
        # Ensure correct column types
        df["blue_light_filter_on"] = bool(df["blue_light_filter_on"].iloc[0])

        # Preprocess features
        X_trans = self.preprocessor.transform(df)

        # Model inference
        with torch.no_grad():
            tensor_in = torch.tensor(X_trans, dtype=torch.float32)
            logits = self.model(tensor_in)
            probs = torch.softmax(logits, dim=1).squeeze(0).numpy()
            predicted_idx = int(np.argmax(probs))

        predicted_label = self.inv_mappings.get(predicted_idx, "Unknown")
        
        # Build probability dictionary
        probability_dist = {
            self.inv_mappings.get(idx, f"Class {idx}"): round(float(prob), 4)
            for idx, prob in enumerate(probs)
        }

        # Turkish explanation and category translation
        category_tr_map = {
            "No Debt": "Uyku Borcu Yok (Optimal Uyku)",
            "Mild": "Hafif Uyku Borcu",
            "Moderate": "Orta / Belirgin Uyku Borcu"
        }

        return {
            "prediction": predicted_label,
            "prediction_tr": category_tr_map.get(predicted_label, predicted_label),
            "confidence": round(float(probs[predicted_idx]) * 100, 2),
            "probabilities": probability_dist,
            "class_index": predicted_idx
        }
