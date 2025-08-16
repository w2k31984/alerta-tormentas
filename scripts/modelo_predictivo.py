# scripts/modelo_predictivo.py
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, roc_auc_score
import joblib

# Cargar datos
df = pd.read_csv(r"C:\Users\cmpme\Documents\Ciencia de Datos\alerta_tormentas\datadatos_simulados.csv")

# Características
features = ["precip_ult_30min", "tendencia_precip", "humedad_relativa",
            "temperatura", "viento_velocidad", "mes", "hora"]

X = df[features]
y = df["tormenta"]

# Dividir datos
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

# Entrenar modelo
model = RandomForestClassifier(n_estimators=100, class_weight="balanced", random_state=42)
model.fit(X_train, y_train)

# Evaluar
y_pred = model.predict(X_test)
print("AUC:", roc_auc_score(y_test, model.predict_proba(X_test)[:, 1]))
print(classification_report(y_test, y_pred))

# Guardar modelo
joblib.dump(model, r"C:\Users\cmpme\Documents\Ciencia de Datos\alerta_tormentas\modelo\modelo_tormenta.pkl")
print("Modelo entrenado y guardado.")

