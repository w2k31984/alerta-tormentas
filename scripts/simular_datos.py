#scripts/simular_datos.py
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

#Generar datos simulados por 2 años
np.random.seed(42)
fechas = pd.date_range("2023-01-01", "2024-12-31", freq= "20min")


#Simulando las variables
data= {
       
    "timestamp": fechas,
    "precip_ult_30min": np.random.exponential(3, len(fechas)),  # lluvia mm
    "tendencia_precip": np.random.normal(0, 1, len(fechas)),     # cambio reciente
    "humedad_relativa": np.random.normal(75, 15, len(fechas)),
    "temperatura": np.random.normal(28, 4, len(fechas)),
    "viento_velocidad": np.random.rayleigh(5, len(fechas)),
    "mes": [d.month for d in fechas],
    "hora": [d.hour for d in fechas]
}

df = pd.DataFrame(data)

# Crear etiqueta: tormenta intensa si > 15 mm en 30 min
df["tormenta"] = (df["precip_ult_30min"] > 15).astype(int)

# Añadir efecto estacional (más lluvia en septiembre)
df.loc[(df["mes"].isin([5,6,7,8,9,10])) & (np.random.rand(len(df)) > 0.7), "tormenta"] = 1

# Guardar
df.to_csv(r"C:\Users\cmpme\Documents\Ciencia de Datos\alerta_tormentas\datadatos_simulados.csv", index=False)
print("Datos simulados guardados.")
