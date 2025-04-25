# python-worker/services/price_predictor.py
"""
LSTM-based price prediction service
Loads trained model and makes predictions
"""

import numpy as np
import pandas as pd
from tensorflow.keras.models import load_model
from sklearn.preprocessing import MinMaxScaler
import joblib
import yaml
from typing import Dict, Any

class PricePredictor:
    def __init__(self, config_path: str = 'config/model_config.yaml'):
        with open(config_path) as f:
            self.config = yaml.safe_load(f)
        
        self.model = load_model(self.config['model_path'])
        self.scaler = joblib.load(self.config['scaler_path'])
        self.lookback = self.config['lookback_window']
        self.features = self.config['features']

    def preprocess_data(self, data: pd.DataFrame) -> np.ndarray:
        """Normalize and reshape input data for model prediction"""
        scaled = self.scaler.transform(data[self.features])
        X = []
        for i in range(len(scaled) - self.lookback + 1):
            X.append(scaled[i:(i + self.lookback)])
        return np.array(X)

    def predict(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Make price prediction for next timeframe"""
        X = self.preprocess_data(data)
        prediction = self.model.predict(X[-1:])[0][0]
        
        # Inverse transform to get actual price
        dummy = np.zeros((1, len(self.features)))
        dummy[0, 0] = prediction  # Assuming price is first feature
        predicted_price = self.scaler.inverse_transform(dummy)[0, 0]
        
        return {
            'predicted_price': float(predicted_price),
            'confidence': 0.95,  # Placeholder
            'direction': 'up' if prediction > 0 else 'down'
        }