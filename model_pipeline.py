import os
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.ensemble import AdaBoostRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import joblib

def load_data(data_path):
    """Load the dataset from CSV file"""
    df = pd.read_csv(data_path)
    print(f"Dataset loaded successfully. Shape: {df.shape}")
    return df

def explore_data(df):
    """Explore dataset structure and statistics"""
    print("*** Dataset Info ***:")
    print(df.info())
    print("\n*** Missing Values per Column ***:")
    print(df.isnull().sum())
    print("\n*** Summary Statistics ***:")
    print(df.describe())
    return df

def clean_data(df):
    """Clean the dataset - handle missing values and outliers"""
    # Strip whitespace in string columns
    for col in ['department', 'quarter', 'day']:
        df[col] = df[col].astype(str).str.strip()

    # Fix unexpected values in 'quarter'
    df['quarter'] = df['quarter'].replace({'Quarter5': 'Quarter4'})

    # Convert 'date' to datetime
    df['date'] = pd.to_datetime(df['date'], errors='coerce')

    # Impute missing values for numeric columns (except 'wip')
    numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
    numeric_cols.remove('wip')
    for col in numeric_cols:
        df[col] = df[col].fillna(df[col].mean())

    # Categorical columns
    cat_cols = ['day', 'department', 'quarter']
    for col in cat_cols:
        df[col] = df[col].replace('nan', np.nan)
        df[col] = df[col].fillna(df[col].mode()[0])

    # Impute 'wip' with median
    df['wip'] = df['wip'].fillna(df['wip'].median())

    # Drop rows with missing 'actual_productivity' (target)
    df = df.dropna(subset=['actual_productivity'])

    # Remove outliers from 'over_time'
    df = df[(df['over_time'] >= -6840.0) & (df['over_time'] <= 15240.0)]

    print("Data cleaning complete.")
    return df

def engineer_features(df):
    """Create new features from existing data"""
    df['wip_per_worker'] = df['wip'] / df['no_of_workers']
    df['over_time_per_worker'] = df['over_time'] / df['no_of_workers']
    df['idle_time_per_worker'] = df['idle_time'] / df['idle_men'].replace(0, 1)
    
    print("Feature engineering complete.")
    return df

def prepare_data(df):
    """Prepare data for training - setup preprocessor and split data"""
    target = 'actual_productivity'
    X_cols = df.drop(columns=[target, 'date']).columns.tolist()
    
    X = df[X_cols]
    y = df[target]

    # Preprocessing setup
    categorical_cols = ['day', 'department', 'quarter']
    numeric_cols = [col for col in X_cols if col not in categorical_cols]
    
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), numeric_cols),
            ('cat', OneHotEncoder(drop='first', handle_unknown='ignore'), categorical_cols)
        ]
    )

    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    print("Data preparation complete.")
    return X_train, X_test, y_train, y_test, preprocessor

def train_model(X_train, y_train, preprocessor):
    """Train the AdaBoost model"""
    ada_pipeline = Pipeline([
        ('pre', preprocessor),
        ('model', AdaBoostRegressor(
            n_estimators=100,
            random_state=42,
            learning_rate=1.0
        ))
    ])
    
    ada_pipeline.fit(X_train, y_train)
    print("Model training complete.")
    return ada_pipeline

def evaluate_model(model, X_test, y_test):
    """Evaluate model performance"""
    y_pred = model.predict(X_test)
    
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    
    metrics = {
        'rmse': rmse,
        'mae': mae,
        'r2': r2
    }
    
    return metrics

def save_model(model, filename='tuned_ada_productivity_model.pkl'):
    """Save the trained model"""
    joblib.dump(model, filename)
    print(f"Model saved as '{filename}'")

def load_model(filename='tuned_ada_productivity_model.pkl'):
    """Load a saved model"""
    model = joblib.load(filename)
    print(f"Model loaded from '{filename}'")
    return model

