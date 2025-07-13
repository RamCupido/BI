import pandas as pd
from ETL.transform import transform_persona_data, transform_vivienda_data
from ETL.extract import extract_csvs
from sklearn.ensemble import RandomForestRegressor
import joblib

# 1. Carga de datos crudos
persona_raw = extract_csvs('Data/Personas')
vivienda_raw = extract_csvs('Data/Viviendas')

# 2. Transformaciones ETL
persona = transform_persona_data(persona_raw)
vivienda = transform_vivienda_data(vivienda_raw)

# 3. Agregación nacional de variables de persona
# Columnas categóricas y numéricas de persona
cat_cols = [
    "area", "SEXO", "ESTADO_CIVIL", "NIVEL_INSTRUCCION",
    "ANALFABETO", "empleo"
]
num_cols = ["EDAD", "ingrl", "INGRESO_PENSION"]

# 3.1. Dummies para categóricas
pers_dummies = pd.get_dummies(
    persona[["periodo"] + cat_cols],
    columns=cat_cols,
    prefix=cat_cols,
    prefix_sep="="
)
pers_dummies_ag = pers_dummies.groupby("periodo").mean().reset_index()

# 3.2. Medias para numéricas
pers_num_ag = (
    persona[["periodo"] + num_cols]
    .groupby("periodo")
    .mean()
    .reset_index()
)

# 3.3. Tasa de pobreza objetivo
persona["POBREZA_bin"] = persona["POBREZA"].map({"Si":1,"No":0})
pers_target = (
    persona.groupby("periodo")["POBREZA_bin"]
    .mean()
    .reset_index()
    .rename(columns={"POBREZA_bin":"pobreza_rate"})
)

# 3.4. Unión de todo lo de persona
pers_ag = (pers_target
           .merge(pers_num_ag,    on="periodo")
           .merge(pers_dummies_ag,on="periodo")
          )

# 4. Agregación nacional de variables de vivienda
cols_cat_viv = [
    "TIPO_VIVIENDA","MATERIAL_TECHO","MATERIAL_PISO",
    "MATERIAL_PARED","ACCESO_AGUA","ACCESO_ELECTRICIDAD"
]
viv_dummies = pd.get_dummies(
    vivienda[["periodo"] + cols_cat_viv],
    columns=cols_cat_viv,
    prefix=cols_cat_viv,
    prefix_sep="="
)
viv_ag = viv_dummies.groupby("periodo").mean().reset_index()

# 5. Construcción del DataFrame final
df = pers_ag.merge(viv_ag, on="periodo", how="left")

# 6. Preparar serie temporal y rezagos
# Convertir periodo a datetime (ajusta el formato si tu columna es distinta)
df["periodo"] = pd.to_datetime(df["periodo"])
df = df.set_index("periodo").sort_index()

# Número de rezagos que usarás
nlags = 12

for lag in range(1, nlags+1):
    df[f"lag_{lag}"] = df["pobreza_rate"].shift(lag)

df_model = df.dropna()  # descarta los primeros 'nlags' periodos

# 7. Entrenamiento del RandomForestRegressor
feature_cols = [c for c in df_model.columns if c != "pobreza_rate"]
X = df_model[feature_cols]
y = df_model["pobreza_rate"]

model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X, y)

# Guardar el modelo entrenado
joblib.dump(model, "rf_forecast_pobreza.pkl")
print("Modelo de forecasting guardado en rf_forecast_pobreza.pkl")

# 8. Función de pronóstico recursivo para los próximos 12 meses
def forecast_future(model, df_full, nlags, steps):
    history = df_full["pobreza_rate"].tolist()
    # columnas estáticas (exógenas): todo menos target y rezagos
    static_cols = [c for c in df_full.columns 
                   if not c.startswith("lag_") and c != "pobreza_rate"]
    static_vals = df_full.iloc[-1][static_cols].to_dict()
    
    last_date = df_full.index[-1]
    future = []
    
    for _ in range(steps):
        feat = {}
        # añadir rezagos dinámicos
        for lag in range(1, nlags+1):
            feat[f"lag_{lag}"] = history[-lag]
        # añadir variables exógenas fijas
        feat.update(static_vals)
        
        # predecir un paso
        x_new = pd.DataFrame([feat])
        y_new = model.predict(x_new)[0]
        # registrar
        history.append(y_new)
        # avanzar fecha (suponer mensual; usa DateOffset(years=1) para anual)
        last_date = last_date + pd.DateOffset(years=1)
        future.append({"periodo": last_date, "pobreza_rate": y_new})
    
    return pd.DataFrame(future).set_index("periodo")

forecast_df = forecast_future(model, df, nlags=nlags, steps=12)

# 9. Exportar pronóstico a Excel
forecast_df.to_excel("pronostico_pobreza_12m.xlsx")
print("Pronóstico para próximos 12 periodos guardado en pronostico_pobreza_12m.xlsx")
