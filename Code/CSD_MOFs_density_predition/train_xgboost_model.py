import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score
import xgboost as xgb
from sklearn.model_selection import KFold
import optuna
import sys

np.seterr(divide='ignore', invalid="ignore")
# Read data
version = sys.argv[1]
merged_features = pd.read_csv(f'{version}/merged_features.csv')

# Filter data with density between 0 and 6
filtered_data = merged_features[(merged_features['density'] >= 0) & (merged_features['density'] <= 6)]

# Prepare data
X = filtered_data.drop(columns=['mof_identifier', 'pld', 'lcd', 'gcd', 'density', 'unitcell_volume'])
feature_names = X.columns  # Get feature names
# X = X.fillna(-1)
X = X.values.astype(np.float32)
y = filtered_data['density'].values.astype(np.float32)

# Standardize data
scaler = StandardScaler()
X = scaler.fit_transform(X)
# Cross-validation
kf = KFold(n_splits=10, shuffle=True, random_state=42)

# Function to perform cross-validation and record predictions
def cross_val_predict(X, y, kf, model_params):
    test_actual = []
    test_pred = []
    
    for train_index, test_index in kf.split(X):
        X_train, X_test = X[train_index], X[test_index]
        y_train, y_test = y[train_index], y[test_index]

        model = xgb.XGBRegressor(**model_params)

        model.fit(X_train, y_train, verbose=False)

        y_pred = model.predict(X_test)
        
        test_actual.extend(y_test)
        test_pred.extend(y_pred)
    
    return np.array(test_actual), np.array(test_pred)

def objective(trial):
    param = {
        'objective': 'reg:squarederror',
        'n_estimators': 1000,
        'learning_rate': trial.suggest_float('learning_rate', 0.001, 0.1, log=True),
        'max_depth': trial.suggest_int('max_depth', 3, 12),
        'subsample': trial.suggest_float('subsample', 0.3, 1.0),
        'colsample_bytree': trial.suggest_float('colsample_bytree', 0.3, 1.0),
        'random_state': 42,
        'tree_method': 'gpu_hist', 'gpu_id': 0
    }
    
    test_actual, test_pred = cross_val_predict(X, y, kf, param)
    return r2_score(test_actual, test_pred)

# Optimize model using Optuna
study = optuna.create_study(direction='maximize')
study.optimize(objective, n_trials=100)

# Get best parameters from Optuna
best_params = study.best_params
best_value = study.best_trial.value

print("Dataset", version)
print("Best params:", best_params)
print("Best value:", best_value)