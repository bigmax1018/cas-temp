# python-worker/scripts/preprocess.py
"""
Data preprocessing pipeline with:
- Missing value handling
- Feature engineering
- Normalization strategies
"""
import pandas as pd
import numpy as np
from sklearn.preprocessing import RobustScaler
from ta import add_all_ta_features

def preprocess_data(df: pd.DataFrame) -> pd.DataFrame:
    """Main preprocessing workflow"""
    # 1. Handle missing data
    df = handle_missing_values(df)
    
    # 2. Add technical indicators
    df = add_technical_indicators(df)
    
    # 3. Feature engineering
    df = engineer_features(df)
    
    # 4. Normalize
    df = normalize_features(df)
    
    return df

def handle_missing_values(df):
    """Fill or drop missing values"""
    df = df.ffill().bfill()
    return df.dropna()

def add_technical_indicators(df):
    """Add TA-Lib features"""
    return add_all_ta_features(
        df, 
        open="open", 
        high="high", 
        low="low", 
        close="close", 
        volume="volume"
    )

def engineer_features(df):
    """Create derived features"""
    df['log_ret'] = np.log(df['close'] / df['close'].shift(1))
    df['volatility'] = df['log_ret'].rolling(20).std()
    df['spread_pct'] = (df['high'] - df['low']) / df['open']
    return df

def normalize_features(df):
    """Robust scaling for financial data"""
    scaler = RobustScaler()
    numeric_cols = df.select_dtypes(include=np.number).columns
    df[numeric_cols] = scaler.fit_transform(df[numeric_cols])
    return df