import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import KFold
import optuna
import pickle
import sys
from data_preparation import get_input_data3

feature_file = sys.argv[1]
data = pd.read_csv(feature_file)
X = data.iloc[:, 1:]  # Include all columns except the first one
X = X.fillna(-1)
X = X.drop(columns=['SSA'])  # Drop the SSA column from X
y = data['SSA'].values.astype(np.float32)  # Set y as the SSA column

# Feature names
feature_names = X.columns

# Standardize the features
scaler = StandardScaler()
X = scaler.fit_transform(X.values.astype(np.float32))

# Step 2: Cross-validation setup
kf = KFold(n_splits=10, shuffle=True, random_state=42)
kf1 = KFold(n_splits=10, shuffle=True, random_state=142)
kf2 = KFold(n_splits=10, shuffle=True, random_state=242)
kf3 = KFold(n_splits=10, shuffle=True, random_state=342)

def k_fold_model(model:RandomForestRegressor, X, y, kf):
    test_actual = []
    test_pred = []
    train_actual = []
    train_pred = []

    r2_scores = []
    rmse_scores = []
    for kf in [kf1, kf2, kf3, kf]:
        for train_index, test_index in kf.split(X):
            X_train, X_test = X[train_index], X[test_index]
            y_train, y_test = y[train_index], y[test_index]

            model.fit(X_train, y_train)
            
            train_y_pred = model.predict(X_train)
            y_pred = model.predict(X_test)
            
            train_actual.extend(y_train)
            train_pred.extend(train_y_pred)
            test_actual.extend(y_test)
            test_pred.extend(y_pred)

            r2 = r2_score(y_test, y_pred)
            rmse = np.sqrt(mean_squared_error(y_test, y_pred))
            r2_scores.append(r2)
            rmse_scores.append(rmse)
    return r2_scores, rmse_scores, test_actual, test_pred, train_actual, train_pred

def get_model(params):
    return  RandomForestRegressor(
        # n_estimators=100,
        random_state=42,
        n_jobs=-1,
        **params
    )


# Step 3: Optimize model using Optuna
def optimize_model(X, y, kf):
    def objective(trial):
        param={
        'min_samples_split': trial.suggest_int('min_samples_split', 2, 20),
        'min_samples_leaf': trial.suggest_int('min_samples_leaf', 1, 10),
        'max_features': trial.suggest_categorical('max_features', [1, 'sqrt', 'log2', 0.5, 0.8]),
        'max_samples': trial.suggest_float('max_samples', 0.5, 1.0),
        'min_impurity_decrease': trial.suggest_float('min_impurity_decrease', 0.0, 0.1),
        }
        model = get_model(param)
        r2_scores, rmse_scores, test_actual, test_pred, train_actual, train_pred = k_fold_model(model, X, y, kf)
        return r2_score(test_actual, test_pred)

    # Optimize model using Optuna
    study = optuna.create_study(direction='maximize')
    study.optimize(objective, n_trials=100)

    # Get best parameters from Optuna
    best_params = study.best_params
    return best_params

best_params = optimize_model(X, y, kf)
print(feature_file)
print(best_params)
model = get_model(best_params)
r2_scores, rmse_scores, test_actual, test_pred, train_actual, train_pred = k_fold_model(model, X, y, kf)
print(np.mean(r2_scores))
print("best value", r2_score(test_actual, test_pred))
print("train value", r2_score(train_actual, train_pred))
# model = get_model(best_params)
# model.fit(X, y)
# pickle.dump(model, open("model.pkl", "wb"))
# pickle.dump(scaler, open("scaler.pkl", "wb"))