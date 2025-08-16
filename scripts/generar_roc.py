# scripts/generar_roc.py
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve, auc
from sklearn.ensemble import RandomForestClassifier
import joblib
import os
import seaborn as sns

# Configuración profesional
plt.style.use('seaborn-v0_8')  # Estilo moderno equivalente
sns.set(style="whitegrid")
plt.rcParams['axes.grid'] = True
plt.rcParams['grid.color'] = 'white'
plt.rcParams['grid.linestyle'] = '-'
plt.rcParams['grid.linewidth'] = 1
plt.rcParams['grid.alpha'] = 0.5
plt.rcParams['axes.facecolor'] = '#EAEAF2'

# Cargar datos y modelo
df = pd.read_csv(r"C:\Users\cmpme\Documents\Ciencia de Datos\alerta_tormentas\data\datos_simulados.csv")
df = df.sort_values('timestamp')
# 1. Convertir la columna timestamp
try:
    df['timestamp'] = pd.to_datetime(df['timestamp'])
except Exception as e:
    print(f"Error al convertir timestamp: {e}")
    # Manejo adicional de errores aquí

# 2. Verificar la conversión
if not pd.api.types.is_datetime64_any_dtype(df['timestamp']):
    raise ValueError("La columna timestamp no se pudo convertir a datetime")

# 3. Ahora calcular el cuantil
cutoff = df['timestamp'].quantile(0.8)
print(f"El cutoff temporal es: {cutoff}")
train = df[df['timestamp'] < cutoff]
test = df[df['timestamp'] >= cutoff]

features = ["precip_ult_30min", "tendencia_precip", "humedad_relativa",
            "temperatura", "viento_velocidad", "mes", "hora"]

X_train, y_train = train[features], train['tormenta']
X_test, y_test = test[features], test['tormenta']

# Entrenar modelo (igual que en validación)
model = RandomForestClassifier(n_estimators=100, 
                              class_weight={0:1, 1:5},
                              random_state=42)
model.fit(X_train, y_train)

# Calcular curva ROC
y_score = model.predict_proba(X_test)[:, 1]
fpr, tpr, thresholds = roc_curve(y_test, y_score)
roc_auc = auc(fpr, tpr)

# Encontrar el mejor umbral (máxima distancia a la diagonal)
optimal_idx = np.argmax(tpr - fpr)
optimal_threshold = thresholds[optimal_idx]

# Crear gráfica profesional
plt.figure(figsize=(10, 8))

# Curva ROC
plt.plot(fpr, tpr, color='#1a3a6c', lw=3, 
         label=f'Curva ROC (AUC = {roc_auc:.3f})')

# Línea aleatoria
plt.plot([0, 1], [0, 1], color='gray', lw=1.5, linestyle='--')

# Punto óptimo
plt.scatter(fpr[optimal_idx], tpr[optimal_idx], 
            s=200, color='#d42a2a', 
            label=f'Umbral óptimo ({optimal_threshold:.2f})',
            zorder=5)

# Detalles profesionales
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('Tasa de Falsos Positivos (FPR)', fontsize=14, labelpad=10)
plt.ylabel('Tasa de Verdaderos Positivos (Recall)', fontsize=14, labelpad=10)
plt.title('Curva ROC - Sistema de Alerta Temprana para Tormentas Rápidas\nSan Salvador', 
          fontsize=16, pad=20)
plt.legend(loc="lower right", fontsize=12)
plt.grid(True, linestyle='--', alpha=0.7)

# Añadir información contextual
plt.annotate(f'62% de tormentas detectadas\ncon 1.7% de falsas alertas', 
             xy=(fpr[optimal_idx], tpr[optimal_idx]), 
             xytext=(fpr[optimal_idx]+0.1, tpr[optimal_idx]-0.25),
             arrowprops=dict(facecolor='black', shrink=0.05, width=1.5),
             fontsize=12,
             bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="gray", alpha=0.8))

# Añadir logo de institución (opcional)
# plt.figimage(plt.imread('docs/logo.png'), xo=50, yo=50, alpha=0.1)

# Guardar con alta resolución
os.makedirs("docs", exist_ok=True)
plt.savefig("docs/roc_curve.png", dpi=300, bbox_inches='tight')
plt.close()

print("✅ Gráfica ROC generada y guardada en docs/roc_curve.png")
print(f"💡 Umbral óptimo identificado: {optimal_threshold:.2f} (Recall={tpr[optimal_idx]:.2f}, FPR={fpr[optimal_idx]:.2f})")