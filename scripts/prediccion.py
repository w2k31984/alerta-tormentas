# scripts/prediccion.py
import pandas as pd
import joblib
from datetime import datetime

model = joblib.load(r"C:\Users\cmpme\Documents\Ciencia de Datos\alerta_tormentas\modelo\modelo_tormenta.pkl")

# Datos nuevos (ej. de una API o estación)
nuevos_datos = pd.DataFrame([{
    "precip_ult_30min": 12.5,
    "tendencia_precip": 2.1,
    "humedad_relativa": 88,
    "temperatura": 26.5,
    "viento_velocidad": 14,
    "mes": 4,
    "hora": 15
}])

prob = model.predict_proba(nuevos_datos)[0, 1]

print(f"📅 {datetime.now()}")
print(f"🚨 Probabilidad de tormenta intensa: {prob:.2%}")

if prob > 0.7:
    print("🔴 ALERTA ROJA: Activar protocolo de emergencia")
elif prob > 0.5:
    print("🟠 ALERTA NARANJA: Monitorear zona vulnerable")
else:
    print("🟢 Sin alerta")