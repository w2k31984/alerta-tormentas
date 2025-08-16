# 🌧️ Sistema de Alerta Temprana para Tormentas Rápidas - San Salvador

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

⚠️ **¡Prototipo v0.1 en fase de validación!** Este sistema predice tormentas intensas (>15 mm en 30 minutos) con 30-60 minutos de anticipación para activar alertas en zonas vulnerables de San Salvador.

![Diagrama del sistema](docs/diagrama_sistema.png)

## 🎯 Objetivo
Predecir eventos de **lluvia extrema en tiempo reducido** (≤30 minutos) para:
- Activar protocolos de emergencia en zonas críticas
- Reducir falsas alarmas mediante umbral adaptable
- Proporcionar 20+ minutos de anticipación para reacción

## 📊 Métricas de Validación (simulación)
| Métrica | Valor | Interpretación |
|---------|-------|----------------|
| **Recall** | 62% | 62 de cada 100 tormentas serán detectadas |
| **Precisión** | 65% | 65 de cada 100 alertas serán correctas |
| **Falsos Positivos** | 1.7% | Bajo riesgo de alarmas innecesarias |
| **Lead Time** | 22.5 min | Tiempo promedio de anticipación |
| **Umbral Óptimo** | 0.60 | Configuración actual del sistema |

> ℹ️ *Nota: Estos resultados son de simulación. En implementación real con datos históricos de San Salvador, se espera mejor rendimiento.*

## 🛠️ Arquitectura del Sistema
[Sensores/Satélites] → [Preprocesamiento] → [Modelo ML] → [Sistema de Alertas]
│ │ │
├─→ CHIRPS/GPM ├─→ Limpieza ├─→ Random Forest
├─→ Estaciones locales ├─→ Feature Eng. ├─→ Umbral adaptable
└─→ GFS └─→ Normalización └─→ Notificaciones

## 🚀 Cómo Ejecutar el Prototipo

### Requisitos
- Python 3.8+
- Dependencias: `pandas`, `scikit-learn`, `numpy`, `joblib`

### Pasos
```bash
# 1. Clonar repositorio
git clone https://github.com/w2k31984/alerta-tormentas.git
cd alerta-tormentas

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Generar datos simulados (solo primera vez)
python scripts/simular_datos.py

# 4. Entrenar y validar modelo
python scripts/validacion_temporal.py

# 5. Ejecutar predicción de ejemplo
python scripts/prediccion.py


## 📎 Archivos Adicionales Recomendados

Para completar tu documentación, crea estos archivos:

### 1. `requirements.txt`
```text
pandas==2.0.3
scikit-learn==1.3.0
numpy==1.25.2
joblib==1.3.2
matplotlib==3.7.2

# 📊 Interpretación de Niveles de Alerta

## 🟢 Verde (0-49%)
- **Acción**: Monitoreo normal
- **Explicación**: Baja probabilidad de tormenta intensa
- **Recomendación**: Mantener vigilancia estándar

## 🟠 Naranja (50-79%)
- **Acción**: Alerta preventiva
- **Explicación**: Probabilidad moderada-alta de lluvia intensa
- **Recomendación**: 
  * Notificar a equipos de emergencia
  * Verificar sistemas de drenaje
  * Alertar a zonas críticas mediante canales oficiales

## 🔴 Rojo (80%+)
- **Acción**: Alerta crítica - Activar protocolo
- **Explicación**: Alta probabilidad de tormenta intensa
- **Recomendación inmediata**:
  * Activar sirenas en zonas vulnerables
  * Notificar a Protección Civil y Bomberos
  * Iniciar evacuación preventiva en zonas críticas
  * Cerrar accesos a zonas de riesgo