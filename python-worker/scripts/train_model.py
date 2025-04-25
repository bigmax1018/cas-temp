# python-worker/scripts/train_model.py
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from sklearn.preprocessing import MinMaxScaler
import numpy as np
import json
import yaml
import os
from datetime import datetime

def load_config():
    """Load model configuration"""
    with open('config/model_config.yaml') as f:
        return yaml.safe_load(f)

def create_model(input_shape):
    """Create LSTM model architecture"""
    model = Sequential([
        LSTM(50, return_sequences=True, input_shape=input_shape),
        Dropout(0.2),
        LSTM(50, return_sequences=False),
        Dropout(0.2),
        Dense(25),
        Dense(1)
    ])
    model.compile(optimizer='adam', loss='mean_squared_error')
    return model

def train():
    config = load_config()
    
    # Load and preprocess data
    data = np.loadtxt('data/training_data.csv', delimiter=',')
    scaler = MinMaxScaler(feature_range=(0,1))
    scaled_data = scaler.fit_transform(data.reshape(-1,1))
    
    # Save scaler
    import joblib
    joblib.dump(scaler, 'models/scaler.pkl')
    
    # Prepare training data
    x_train, y_train = [], []
    for i in range(config['lookback'], len(scaled_data)):
        x_train.append(scaled_data[i-config['lookback']:i, 0])
        y_train.append(scaled_data[i, 0])
    
    x_train, y_train = np.array(x_train), np.array(y_train)
    x_train = np.reshape(x_train, (x_train.shape[0], x_train.shape[1], 1))
    
    # Train model
    model = create_model((x_train.shape[1], 1))
    history = model.fit(
        x_train, y_train,
        batch_size=config['batch_size'],
        epochs=config['epochs'],
        validation_split=0.1
    )
    
    # Save model
    model.save('models/lstm_model.h5')
    
    # Save metadata
    metadata = {
        'version': '1.0.0',
        'training_date': datetime.now().isoformat(),
        'metrics': {
            'final_loss': history.history['loss'][-1],
            'final_val_loss': history.history['val_loss'][-1]
        },
        'input_shape': x_train.shape[1:]
    }
    
    with open('models/metadata/model_version.json', 'w') as f:
        json.dump(metadata, f)
    
    with open('models/metadata/training_metrics.json', 'w') as f:
        json.dump(history.history, f)

if __name__ == '__main__':
    train()