# ai_engine/ml_model.py
import os, joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

MODEL_DIR = 'models'
os.makedirs(MODEL_DIR, exist_ok=True)

def model_path_for(user_id):
    return os.path.join(MODEL_DIR, f'user_{user_id}_model.pkl')

def train_model_for_user(user_id, feature_df, target_series):
    """ feature_df: pandas.DataFrame, target_series: 0/1 series """
    if feature_df.empty:
        return None
    X_train, X_test, y_train, y_test = train_test_split(feature_df, target_series, test_size=0.2, random_state=42)
    model = LogisticRegression(max_iter=200)
    model.fit(X_train, y_train)
    path = model_path_for(user_id)
    joblib.dump(model, path)
    return path

def predict_for_user(user_id, X):
    """X: DataFrame or 2D array"""
    path = model_path_for(user_id)
    if not os.path.exists(path):
        return None
    model = joblib.load(path)
    probs = model.predict_proba(X)[:,1]
    return probs
