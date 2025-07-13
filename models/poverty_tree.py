from sklearn.tree import DecisionTreeRegressor
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import TimeSeriesSplit
from Config.db_config import get_connection
from models.poverty_forecast import load_poverty_series

def prepare_features(series, max_lag=5):
    df = series.to_frame(name='pobreza_pct')
    for lag in range(1, max_lag+1):
        df[f'lag_{lag}'] = df['pobreza_pct'].shift(lag)
    df = df.dropna()
    X = df[[c for c in df.columns if c.startswith('lag_')]]
    y = df['pobreza_pct']
    return X, y

def train_and_evaluate(X, y, max_depth=4, min_samples_leaf=2, n_splits=3):
    n_samples = X.shape[0]
    max_folds = n_samples - 1  # TS-Split necesita al menos n_splits+1 muestras
    if max_folds < 1:
        print(f"Sólo hay {n_samples} muestra(s), omitiendo validación cruzada.")
        return None

    folds = min(n_splits, max_folds)
    tscv = TimeSeriesSplit(n_splits=folds)
    maes = []
    for train_idx, test_idx in tscv.split(X):
        X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
        y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]
        model = DecisionTreeRegressor(
            max_depth=max_depth,
            min_samples_leaf=min_samples_leaf,
            random_state=42
        )
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        maes.append(mean_absolute_error(y_test, y_pred))

    mae_prom = sum(maes) / len(maes)
    print(f"CV MAE ({folds} folds): {mae_prom:.2f}%")
    return mae_prom

def forecast_next_year_tree(X, y, max_depth=4, min_samples_leaf=2):
    model = DecisionTreeRegressor(
        max_depth=max_depth,
        min_samples_leaf=min_samples_leaf,
        random_state=42
    )
    model.fit(X, y)
    ultimo = X.iloc[-1].values.reshape(1, -1)
    return float(model.predict(ultimo)[0])

def run_tree_pipeline(max_lag, max_depth, min_samples_leaf, n_splits):
    conn = get_connection()
    series = load_poverty_series(conn)

    X, y = prepare_features(series, max_lag=max_lag)

    # 1) Validación cruzada (si hay datos suficientes)
    train_and_evaluate(X, y,
                       max_depth=max_depth,
                       min_samples_leaf=min_samples_leaf,
                       n_splits=n_splits)

    # 2) Entrenamos con toda la serie y predecimos
    next_pct = forecast_next_year_tree(X, y,
                                       max_depth=max_depth,
                                       min_samples_leaf=min_samples_leaf)
    next_year = series.index.year.max() + 1
    print(f"Predicción DecisionTree para {next_year}: {next_pct:.2f}%")
    return next_pct