# python-worker/services/anomaly_detector.py
"""
Online anomaly detection with:
- Incremental learning
- Adaptive thresholds
- Multiple detection strategies
"""
import numpy as np
from sklearn.ensemble import IsolationForest
from joblib import dump, load
from pathlib import Path
import logging

MODEL_PATH = Path(__file__).parent / "../models/anomaly_model.joblib"

class AnomalyDetector:
    def __init__(self, initial_data: np.ndarray = None):
        self.model = self._load_or_init(initial_data)
        self.threshold = -0.5
        self.logger = logging.getLogger(__name__)
    
    def _load_or_init(self, data):
        try:
            return load(MODEL_PATH)
        except FileNotFoundError:
            if data is not None:
                return self._train_new_model(data)
            return IsolationForest(n_estimators=100, contamination=0.01)
    
    def _train_new_model(self, data):
        model = IsolationForest(n_estimators=100, contamination=0.01)
        model.fit(data)
        dump(model, MODEL_PATH)
        return model
    
    def update(self, new_data: np.ndarray):
        """Online model update"""
        partial_fit = getattr(self.model, 'partial_fit', None)
        if callable(partial_fit):
            partial_fit(new_data)
        else:
            combined_data = np.concatenate([self.model.X_train_, new_data])
            self.model = self._train_new_model(combined_data)
        
        self._adjust_threshold(new_data)
        dump(self.model, MODEL_PATH)
    
    def detect(self, features: list) -> tuple[bool, float]:
        score = self.model.decision_function([features])[0]
        is_anomaly = score < self.threshold
        return is_anomaly, score