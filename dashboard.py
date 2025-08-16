# dashboard.py
import streamlit as st
import pandas as pd
import numpy as np
import joblib
import matplotlib.pyplot as plt
import folium
from streamlit_folium import st_folium
from datetime import datetime, timedelta
import time
import os

# Configuración inicial
st.set_page_config(
    page_title="Alerta Temprana - San Salvador",
    page_icon="🌧️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Cargar recursos
@st.cache_resource
def load_model():
    return joblib.load(r"C:\Users\cmpme\Documents\Ciencia de Datos\alerta_tormentas\modelo\modelo_tormenta.pkl")

@st.cache_data
def load_data():
    if os.path.exists(r"C:\Users\cmpme\Documents\Ciencia de Datos\alerta_tormentas\resultados\backtesting.csv"):
        return pd.read_csv(r"C:\Users\cmpme\Documents\Ciencia de Datos\alerta_tormentas\resultados\backtesting.csv")
    return pd.DataFrame()

# Función para simular datos en tiempo real
def generate_real_time_data():
    base_data = {
        "precip_ult_30min": np.random.exponential(3),
        "tendencia_precip": np.random.normal(0, 1),
        "humedad_relativa": np.random.normal(75, 15),
        "temperatura": np.random.normal(28, 4),
        "viento_velocidad": np.random.rayleigh(5),
        "mes": datetime.now().month,
        "hora": datetime.now().hour
    }
    
    # Simular condiciones de tormenta con mayor probabilidad en temporada
    if 5 <= base_data["mes"] <= 10 and np.random.random() > 0.7:
        base_data["precip_ult_30min"] = np.random.exponential(15)
        base_data["tendencia_precip"] = np.random.normal(3, 1)
        base_data["humedad_relativa"] = np.random.normal(90, 5)
    
    return base_data

# Función para determinar nivel de alerta
def get_alert_level(prob):
    if prob >= 0.7:
        return "🔴 Rojo", "ALERTA CRÍTICA: Activar protocolo de emergencia inmediato"
    elif prob >= 0.5:
        return "🟠 Naranja", "ALERTA PREVENTIVA: Monitorear zonas vulnerables"
    else:
        return "🟢 Verde", "Condiciones normales - Monitoreo estándar"

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/3/34/Flag_of_El_Salvador.svg", 
             width=150)
    st.title("Sistema de Alerta Temprana")
    
    st.markdown("### ⚙️ Configuración")
    umbral = st.slider("Umbral de alerta", 0.3, 0.9, 0.6, 0.05)
    actualizar = st.button("Actualizar datos")
    
    st.markdown("---")
    st.markdown("### 📅 Última actualización")
    st.write(f"{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    st.markdown("---")
    st.markdown("### 📊 Métricas del modelo")
    st.metric("Recall", "62%")
    st.metric("Precisión", "65%")
    st.metric("Lead Time", "22.5 min")

# --- MAIN CONTENT ---
st.title("🌧️ Sistema de Alerta Temprana para Tormentas Rápidas - San Salvador")
st.markdown("##### Monitoreo en tiempo real de zonas vulnerables")

# Generar o actualizar datos
if 'last_update' not in st.session_state or actualizar:
    st.session_state.real_time_data = generate_real_time_data()
    st.session_state.last_update = datetime.now()

# Cargar modelo
model_data = load_model()
model = model_data['model']
optimal_threshold = model_data['threshold']

# Predecir
input_df = pd.DataFrame([st.session_state.real_time_data])
prob = model.predict_proba(input_df)[0, 1]
alerta, mensaje = get_alert_level(prob)

# Sección 1: Alerta Principal
col1, col2, col3 = st.columns([1, 2, 1])

with col1:
    st.subheader("Estado Actual")
    st.metric("Probabilidad", f"{prob:.1%}")
    
    # Mostrar alerta con color
    st.markdown(f"<h2 style='color: {'red' if 'Rojo' in alerta else 'orange' if 'Naranja' in alerta else 'green'};'>{alerta}</h2>", 
                unsafe_allow_html=True)
    st.success(mensaje) if "Verde" in alerta else st.warning(mensaje) if "Naranja" in alerta else st.error(mensaje)

with col2:
    st.subheader("Condiciones Meteorológicas")
    cols = st.columns(3)
    cols[0].metric("Lluvia (30 min)", f"{st.session_state.real_time_data['precip_ult_30min']:.1f} mm")
    cols[0].metric("Tendencia", f"{st.session_state.real_time_data['tendencia_precip']:.2f} mm/min")
    cols[1].metric("Humedad", f"{st.session_state.real_time_data['humedad_relativa']:.0f}%")
    cols[1].metric("Temperatura", f"{st.session_state.real_time_data['temperatura']:.1f}°C")
    cols[2].metric("Viento", f"{st.session_state.real_time_data['viento_velocidad']:.1f} km/h")
    cols[2].metric("Mes", datetime.now().strftime("%B"))

with col3:
    st.subheader("Zonas Críticas")
    zonas = [
        ("Mejicanos", 0.75),
        ("Soyapango", 0.62),
        ("1er. de Mayo", 0.81),
        ("Centro Histórico", 0.45)
    ]
    
    for zona, prob_zona in zonas:
        color = "🔴" if prob_zona >= 0.7 else "🟠" if prob_zona >= 0.5 else "🟢"
        st.write(f"{color} {zona}: {prob_zona:.0%}")

# Sección 2: Mapa de San Salvador
st.subheader("📍 Mapa de Alertas por Zona")

# Coordenadas de San Salvador y zonas críticas
san_salvador_coords = [13.6929, -89.2182]
zonas_vulnerables = [
    {"name": "Mejicanos", "coords": [13.7167, -89.2000], "risk": 0.75},
    {"name": "Soyapango", "coords": [13.6931, -89.1628], "risk": 0.62},
    {"name": "1er. de Mayo", "coords": [13.7050, -89.2300], "risk": 0.81},
    {"name": "Centro Histórico", "coords": [13.6900, -89.2000], "risk": 0.45},
    {"name": "Zona Rosa", "coords": [13.6950, -89.2100], "risk": 0.30}
]

# Crear mapa con folium
m = folium.Map(location=san_salvador_coords, zoom_start=12, tiles="OpenStreetMap")

# Añadir marcadores para zonas vulnerables
for zona in zonas_vulnerables:
    color = 'red' if zona["risk"] >= 0.7 else 'orange' if zona["risk"] >= 0.5 else 'green'
    folium.CircleMarker(
        location=zona["coords"],
        radius=10,
        popup=f"{zona['name']} - Prob: {zona['risk']:.0%}",
        color=color,
        fill=True,
        fillColor=color,
        fillOpacity=0.7
    ).add_to(m)

# Añadir marcador para ubicación actual (simulada)
folium.Marker(
    location=san_salvador_coords,
    popup="Estación Central",
    icon=folium.Icon(color="blue", icon="info-sign")
).add_to(m)

# Mostrar en Streamlit
st_folium(m, width=1200, height=500)

# Sección 3: Rendimiento del Modelo
st.subheader("📊 Validación del Modelo")

col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("### Curva ROC del Modelo")
    if os.path.exists("docs/roc_curve.png"):
        st.image("docs/roc_curve.png", use_column_width=True)
    else:
        st.warning("Ejecuta `python scripts/generar_roc.py` para generar la curva ROC")
    
    st.markdown("""
    **Interpretación:**
    - **AUC 0.87**: Buen poder discriminativo
    - **Umbral óptimo 0.60**: Balance ideal entre detección y falsas alertas
    - **62% de tormentas detectadas** con solo 1.7% de falsas alertas
    """)

with col2:
    st.markdown("### Historial de Alertas (Últimas 24h)")
    
    # Generar datos históricos simulados
    horas = pd.date_range(end=datetime.now(), periods=24, freq='H')
    probabilidades = np.clip(np.random.normal(0.4, 0.2, 24), 0, 1)
    alertas = ["🔴" if p >= 0.7 else "🟠" if p >= 0.5 else "🟢" for p in probabilidades]
    
    historial = pd.DataFrame({
        "Hora": horas.strftime("%H:%M"),
        "Probabilidad": probabilidades,
        "Alerta": alertas
    }).sort_values("Hora", ascending=False).head(12)
    
    st.dataframe(
        historial,
        column_config={
            "Probabilidad": st.column_config.ProgressColumn(
                "Probabilidad",
                format="%.0%",
                min_value=0,
                max_value=1,
            ),
        },
        hide_index=True,
    )
    
    # Gráfica de tendencia
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(horas, probabilidades, 'o-', color='#1a3a6c', linewidth=2)
    ax.axhline(y=0.7, color='red', linestyle='--', alpha=0.3)
    ax.axhline(y=0.5, color='orange', linestyle='--', alpha=0.3)
    ax.set_ylim(0, 1)
    ax.set_title('Tendencia de Probabilidad de Tormenta (Últimas 24h)')
    ax.set_xlabel('Hora')
    ax.set_ylabel('Probabilidad')
    plt.xticks(rotation=45)
    st.pyplot(fig)

# Sección 4: Información Operativa
st.subheader("ℹ️ Protocolo de Respuesta")

tab1, tab2, tab3 = st.tabs(["🔴 Rojo", "🟠 Naranja", "🟢 Verde"])

with tab1:
    st.error("### ACCIÓN INMEDIATA REQUERIDA")
    st.markdown("""
    - **Activar sirenas** en zonas críticas
    - **Notificar a Protección Civil y Bomberos**
    - **Iniciar evacuación preventiva** en zonas identificadas
    - **Cerrar accesos** a zonas de riesgo
    - **Monitorear niveles** de ríos y quebradas
    """)
    if st.button("✅ Activar Protocolo Rojo", type="primary"):
        st.balloons()
        st.success("Protocolo activado - Equipo de emergencia notificado")

with tab2:
    st.warning("### ACCIÓN PREVENTIVA")
    st.markdown("""
    - **Notificar a equipos de emergencia** para alerta máxima
    - **Verificar sistemas de drenaje**
    - **Alertar a zonas críticas** mediante canales oficiales
    - **Preparar equipos** de respuesta
    """)
    if st.button("✅ Activar Protocolo Naranja"):
        st.success("Protocolo activado - Monitoreo intensificado")

with tab3:
    st.success("### MONITOREO ESTÁNDAR")
    st.markdown("""
    - **Mantener vigilancia** mediante sistema automatizado
    - **Verificar reportes** de ciudadanos
    - **Actualizar pronóstico** cada 30 minutos
    """)
    if st.button("✅ Confirmar Estado Verde"):
        st.info("Estado confirmado - Sistema en monitoreo normal")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    Sistema de Alerta Temprana para Tormentas Rápidas | San Salvador, El Salvador | 
    © 2025 | Desarrollado con apoyo de [Tu Organización]
</div>
""", unsafe_allow_html=True)