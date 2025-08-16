# scripts/validacion_temporal.py
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (recall_score, precision_score, 
                            f1_score, roc_curve, auc)
import matplotlib.pyplot as plt
import joblib

# Cargar datos
df = pd.read_csv(r"C:\Users\cmpme\Documents\Ciencia de Datos\alerta_tormentas\datadatos_simulados.csv")
df['timestamp'] = pd.to_datetime(df['timestamp'])

# ORDENAR por tiempo (¡imprescindible!)
df = df.sort_values('timestamp')

# Dividir en entrenamiento (80% más antiguo) y prueba (20% más reciente)
cutoff = df['timestamp'].quantile(0.8)
train = df[df['timestamp'] < cutoff]
test = df[df['timestamp'] >= cutoff]

# Características
features = ["precip_ult_30min", "tendencia_precip", "humedad_relativa",
            "temperatura", "viento_velocidad", "mes", "hora"]

X_train, y_train = train[features], train['tormenta']
X_test, y_test = test[features], test['tormenta']

# Entrenar modelo
model = RandomForestClassifier(n_estimators=100, 
                              class_weight={0:1, 1:5},  # Penalizar más los FN
                              random_state=42)
model.fit(X_train, y_train)

# EVALUACIÓN CLAVE: Diferentes umbrales
thresholds = np.arange(0.3, 0.9, 0.05)
results = []

for threshold in thresholds:
    y_pred = (model.predict_proba(X_test)[:, 1] >= threshold).astype(int)
    
    results.append({
        'threshold': threshold,
        'recall': recall_score(y_test, y_pred),
        'precision': precision_score(y_test, y_pred),
        'fpr': (y_pred & ~y_test.astype(bool)).sum() / (~y_test.astype(bool)).sum(),
        'f1': f1_score(y_test, y_pred)
    })

results_df = pd.DataFrame(results)
print("\nResultados por umbral:")
print(results_df)

# GUARDAR MODELO CON MEJOR TRADEOFF (ej. máximo F1)
best_threshold = results_df.loc[results_df['f1'].idxmax(), 'threshold']
print(f"\nUmbral óptimo seleccionado: {best_threshold:.2f}")

# Backtesting: Simular alertas en tiempo real
test['prob_tormenta'] = model.predict_proba(X_test)[:, 1]
test['alerta'] = (test['prob_tormenta'] >= best_threshold).astype(int)

# Calcular lead time (ejemplo simplificado)
test['lead_time'] = np.nan
for i in range(len(test)-1, 0, -1):
    if test.iloc[i]['tormenta'] == 1:
        # Buscar primera alerta antes de la tormenta
        j = i - 1
        while j >= 0 and test.iloc[j]['timestamp'] >= test.iloc[i]['timestamp'] - pd.Timedelta(minutes=60):
            if test.iloc[j]['alerta'] == 1:
                test.at[j, 'lead_time'] = (test.iloc[i]['timestamp'] - test.iloc[j]['timestamp']).total_seconds() / 60
                break
            j -= 1

avg_lead_time = test['lead_time'].mean()
print(f"⏱️ Lead time promedio: {avg_lead_time:.1f} minutos")

# GUARDAR RESULTADOS
test.to_csv(r"C:\Users\cmpme\Documents\Ciencia de Datos\alerta_tormentas\resultados\backtesting.csv", index=False)
joblib.dump({'model': model, 'threshold': best_threshold},r"C:\Users\cmpme\Documents\Ciencia de Datos\alerta_tormentas\modelo\modelo_tormenta.pkl")
print("Modelo validado y guardado con umbral óptimo")