import os
import sys

# Asegurar que el directorio 'src' esté en el sys.path para importaciones estándar del paquete
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "src"))
if src_path not in sys.path:
    sys.path.insert(0, src_path)

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from csic_climate.data_loader import load_climate_data, filter_by_region_and_years
from csic_climate.metrics import calculate_climate_summary, calculate_decadal_trend


# ==============================================================================
# CONFIGURACIÓN DE PÁGINA Y TEMA OSCURO
# ==============================================================================
st.set_page_config(
    page_title="CSIC ClimateWatch - Monitor de Cambio Climático y Sequía",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS Personalizados para Modo Oscuro Total
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');
    
    /* Global App Background */
    .stApp {
        background-color: #0F172A !important;
        color: #F8FAFC !important;
        font-family: 'Inter', sans-serif;
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #1E293B !important;
        border-right: 1px solid #334155 !important;
    }
    
    /* Header Box */
    .header-box {
        background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
        border: 1px solid #334155;
        border-left: 5px solid #10B981;
        padding: 24px 28px;
        border-radius: 14px;
        margin-bottom: 25px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.4);
    }
    
    .badge-tag {
        background-color: rgba(16, 185, 129, 0.15);
        color: #34D399;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.82rem;
        font-weight: 600;
        border: 1px solid rgba(52, 211, 153, 0.3);
        display: inline-block;
        margin-bottom: 10px;
    }
    
    .header-title {
        font-size: 2.2rem;
        font-weight: 800;
        color: #F8FAFC;
        margin: 0;
        letter-spacing: -0.5px;
    }
    
    .header-subtitle {
        font-size: 0.98rem;
        color: #94A3B8;
        margin-top: 6px;
        font-weight: 400;
    }
    
    /* KPI Metric Cards */
    .kpi-card {
        background-color: #1E293B;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 18px 14px;
        text-align: center;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    
    .kpi-card:hover {
        transform: translateY(-2px);
        border-color: #10B981;
    }
    
    .kpi-title {
        font-size: 0.8rem;
        color: #94A3B8;
        text-transform: uppercase;
        font-weight: 700;
        letter-spacing: 0.5px;
    }
    
    .kpi-number {
        font-size: 1.8rem;
        font-weight: 800;
        color: #F8FAFC;
        margin: 6px 0;
    }
    
    .kpi-desc {
        font-size: 0.78rem;
        color: #64748B;
    }
    
    /* Group Cards in Tab 4 */
    .group-box {
        background-color: #1E293B;
        border-left: 4px solid #3B82F6;
        padding: 18px 22px;
        border-radius: 10px;
        margin-bottom: 14px;
        color: #E2E8F0;
        border-top: 1px solid #334155;
        border-right: 1px solid #334155;
        border-bottom: 1px solid #334155;
    }
    
    /* Streamlit Native Elements Customization */
    .stSelectbox label, .stSlider label {
        color: #E2E8F0 !important;
        font-weight: 600 !important;
    }
    
    /* Tabs Customization */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #1E293B !important;
        border-radius: 8px 8px 0 0 !important;
        color: #94A3B8 !important;
        padding: 10px 18px !important;
        border: 1px solid #334155 !important;
        border-bottom: none !important;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #10B981 !important;
        color: #FFFFFF !important;
        font-weight: 700 !important;
    }
</style>
""", unsafe_allow_html=True)

# --- CABECERA HERO CON SOPORTE DE LOGO ---
logo_path = "assets/logoCSIC.jpg"
if not os.path.exists(logo_path):
    logo_path = "../assets/logoCSIC.jpg"

if os.path.exists(logo_path):
    col_logo, col_header = st.columns([1, 5])
    with col_logo:
        st.image(logo_path, width=130)
    with col_header:
        st.markdown("""
        <div class="header-box">
            <div class="badge-tag">Grupo de Trabajo del Curso • Python para la Ciencia Abierta: Introducción</div>
            <div class="header-title">🌍 CSIC ClimateWatch</div>
            <div class="header-subtitle">Monitor Interactivo de Cambio Climático, Sequía (SPEI) y Olas de Calor en España (1961 - 2024)</div>
        </div>
        """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div class="header-box">
        <div class="badge-tag">Grupo de Trabajo del Curso • Python para la Ciencia Abierta: Introducción</div>
        <div class="header-title">🌍 CSIC ClimateWatch</div>
        <div class="header-subtitle">Monitor Interactivo de Cambio Climático, Sequía (SPEI) y Olas de Calor en España (1961 - 2024)</div>
    </div>
    """, unsafe_allow_html=True)

# --- CARGA DE DATOS CLIMÁTICOS ---
@st.cache_data
def load_data():
    return load_climate_data()

try:
    df_raw = load_data()
except Exception as e:
    st.error(f"❌ Error al cargar el dataset climático: {e}")
    st.stop()

# --- BARRA LATERAL CON FILTROS ---
st.sidebar.markdown("## 🎛️ Filtros de Control")

regiones_disponibles = sorted(df_raw["comunidad_autonoma"].unique().tolist())
regiones_opciones = ["Todas"] + regiones_disponibles

region_sel = st.sidebar.selectbox(
    "📍 Selecciona Comunidad Autónoma:",
    regiones_opciones,
    index=0
)

min_year = int(df_raw["year"].min())
max_year = int(df_raw["year"].max())


year_range = st.sidebar.slider(
    "📅 Rango Temporal (Años):",
    min_value=min_year,
    max_value=max_year,
    value=(1970, 2024),
    step=1
)

st.sidebar.markdown("---")
st.sidebar.markdown(f"**📊 Registros Activos:** {len(df_raw):,} meses")
st.sidebar.markdown(f"**🏛️ Comunidades Autónomas:** {len(regiones_disponibles)}")
st.sidebar.caption("Datos: ERA5 Reanalysis (Copernicus/ECMWF) • Metodología SPEI: IPE-CSIC")


# Filtrado de Datos
df_filtered = filter_by_region_and_years(
    df_raw, 
    region=region_sel, 
    start_year=year_range[0], 
    end_year=year_range[1]
)

# --- RESUMEN DE INDICADORES (TARJETAS KPI TARJETAS OSCURAS) ---
summary = calculate_climate_summary(df_filtered)

c1, c2, c3, c4, c5 = st.columns(5)

with c1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">🌡️ Temp. Media</div>
        <div class="kpi-number">{summary['temp_media']} °C</div>
        <div class="kpi-desc">Promedio Observado</div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    color_anom = "#EF4444" if summary['anomalia_media'] > 0 else "#10B981"
    signo_anom = "+" if summary['anomalia_media'] > 0 else ""
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">☀️ Anomalía Térmica</div>
        <div class="kpi-number" style="color: {color_anom};">{signo_anom}{summary['anomalia_media']} °C</div>
        <div class="kpi-desc">vs Línea Base (1961-1990)</div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">🌧️ Precipitación Total</div>
        <div class="kpi-number" style="color: #60A5FA;">{summary['precipitacion_total']:,} <span style="font-size: 1rem;">mm</span></div>
        <div class="kpi-desc">Acumulado Periodo</div>
    </div>
    """, unsafe_allow_html=True)

with c4:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">🏜️ Sequía Severa</div>
        <div class="kpi-number" style="color: #F59E0B;">{summary['meses_sequia_severa']}</div>
        <div class="kpi-desc">Meses SPEI < -1.5</div>
    </div>
    """, unsafe_allow_html=True)

with c5:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">🔥 Días en Ola Calor</div>
        <div class="kpi-number" style="color: #F87171;">{summary['dias_totales_ola_calor']}</div>
        <div class="kpi-desc">Días T.Máx > 32°C</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# --- PESTAÑAS PRINCIPALES ---
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 Series Temporales y Gráficos", 
    "🗺️ Comparativa Regional", 
    "🧮 Explorador Pandas", 
    "👥 Trabajo en Grupos (GitHub)",
    "ℹ️ INFO & Metodología"
])


# Estilo Oscuro Elegante para Matplotlib
plt.style.use('dark_background')

with tab1:
    st.markdown(f"### 📈 Evolución Climatológica en {region_sel} ({year_range[0]} - {year_range[1]})")
    
    # Agrupación Anual
    df_annual = df_filtered.groupby("year").agg({

        "temperatura_media_c": "mean",
        "anomalia_termica_c": "mean",
        "precipitacion_mm": "sum",
        "indice_spei_sequia": "mean",
        "dias_ola_calor": "sum"
    }).reset_index()
    
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        fig1, ax1 = plt.subplots(figsize=(8, 4.5))
        fig1.patch.set_facecolor('#0F172A')
        ax1.set_facecolor('#1E293B')
        
        colors = ['#EF4444' if x > 0 else '#3B82F6' for x in df_annual["anomalia_termica_c"]]
        ax1.bar(df_annual["year"], df_annual["anomalia_termica_c"], color=colors, alpha=0.9, width=0.8)

        ax1.axhline(0, color='#64748B', linestyle='--', linewidth=1)
        ax1.set_ylabel("Anomalía Térmica (°C)", color='#E2E8F0', fontsize=10)
        ax1.set_title("Anomalía Anual de Temperatura (°C vs 1961-1990)", color='white', fontsize=12, fontweight='bold')
        ax1.grid(True, linestyle=":", alpha=0.25, color='#475569')
        ax1.tick_params(colors='#94A3B8')
        st.pyplot(fig1)

    with col_chart2:
        fig2, ax2 = plt.subplots(figsize=(8, 4.5))
        fig2.patch.set_facecolor('#0F172A')
        ax2.set_facecolor('#1E293B')
        
        ax2.plot(df_annual["year"], df_annual["indice_spei_sequia"], color='#10B981', linewidth=2.2, label="Índice SPEI")
        ax2.axhline(-1.5, color='#EF4444', linestyle='--', linewidth=1.5, label="Umbral Sequía Severa (-1.5)")
        ax2.axhline(0, color='#64748B', linestyle=':', linewidth=0.8)
        ax2.fill_between(df_annual["year"], df_annual["indice_spei_sequia"], -1.5, where=(df_annual["indice_spei_sequia"] <= -1.5), color='#EF4444', alpha=0.35)

        ax2.set_ylabel("Índice SPEI", color='#E2E8F0', fontsize=10)
        ax2.set_title("Índice Estandarizado de Sequía (SPEI - CSIC)", color='white', fontsize=12, fontweight='bold')
        ax2.legend(loc="lower left", facecolor='#1E293B', edgecolor='#334155')
        ax2.grid(True, linestyle=":", alpha=0.25, color='#475569')
        ax2.tick_params(colors='#94A3B8')
        st.pyplot(fig2)

    st.markdown("---")
    st.markdown("### 📅 Tendencia de Calentamiento Promedio por Década")
    df_decadal = calculate_decadal_trend(df_filtered)
    
    fig_dec, ax_dec = plt.subplots(figsize=(10, 3.5))
    fig_dec.patch.set_facecolor('#0F172A')
    ax_dec.set_facecolor('#1E293B')
    
    sns.barplot(
        data=df_decadal, 
        x="decada", 
        y="anomalia_termica_c", 
        hue="decada", 
        legend=False, 
        palette="Reds", 
        ax=ax_dec
    )
    ax_dec.set_xlabel("Década", color='#E2E8F0')
    ax_dec.set_ylabel("Anomalía Media (°C)", color='#E2E8F0')
    ax_dec.set_title("Incremento de Temperatura Promedio por Década (°C)", color='white', fontweight='bold')
    ax_dec.grid(True, linestyle=":", alpha=0.25, color='#475569')
    ax_dec.tick_params(colors='#94A3B8')
    st.pyplot(fig_dec)

with tab2:
    st.markdown("### 🗺️ Ranking y Comparativa entre Comunidades Autónomas")
    
    df_region_summary = df_raw[(df_raw["year"] >= year_range[0]) & (df_raw["year"] <= year_range[1])].groupby("comunidad_autonoma").agg({

        "anomalia_termica_c": "mean",
        "temperatura_media_c": "mean",
        "precipitacion_mm": "mean",
        "indice_spei_sequia": "mean",
        "dias_ola_calor": "sum"
    }).reset_index().round(2)
    
    col_rank1, col_rank2 = st.columns(2)
    
    with col_rank1:
        st.markdown("##### 🔥 Top Comunidades con Mayor Anomalía Térmica (°C)")
        df_sorted_temp = df_region_summary.sort_values(by="anomalia_termica_c", ascending=False).head(10)
        
        fig_rank1, ax_r1 = plt.subplots(figsize=(7, 4.5))
        fig_rank1.patch.set_facecolor('#0F172A')
        ax_r1.set_facecolor('#1E293B')
        
        sns.barplot(data=df_sorted_temp, y="comunidad_autonoma", x="anomalia_termica_c", hue="comunidad_autonoma", legend=False, palette="YlOrRd_r", ax=ax_r1)
        ax_r1.set_xlabel("Anomalía Térmica (°C)", color='#E2E8F0')
        ax_r1.set_ylabel("")
        ax_r1.grid(True, linestyle=":", alpha=0.25, color='#475569')
        ax_r1.tick_params(colors='#94A3B8')
        st.pyplot(fig_rank1)

    with col_rank2:
        st.markdown("##### 🏜️ Top Comunidades con Mayor Impacto de Olas de Calor (Días Acumulados)")
        
        # 1. Calcular el número acumulado de días en ola de calor en el periodo y región seleccionados
        dias_ola_calor_sel = int(df_filtered["dias_ola_calor"].sum())
        
        # 2. Alerta Dinámica: Si el número total de días supera los 20 días
        if dias_ola_calor_sel > 20:
            st.warning("⚠️ Alerta Climática: Se han superado los 20 días en ola de calor en el periodo seleccionado")
            
        # 3. Comparativa: Mostrar la diferencia en días frente al promedio de todas las comunidades en ese mismo rango temporal
        promedio_comunidades = round(float(df_region_summary["dias_ola_calor"].mean()), 1)
        diferencia_promedio = round(dias_ola_calor_sel - promedio_comunidades, 1)
        signo = "+" if diferencia_promedio > 0 else ""
        
        if region_sel != "Todas":
            st.info(
                f"📊 **Comparativa regional:** **{region_sel}** acumula **{dias_ola_calor_sel}** días de ola de calor en el periodo {year_range[0]} - {year_range[1]}. "
                f"Diferencia frente al promedio de todas las comunidades ({promedio_comunidades} días): **{signo}{diferencia_promedio} días**."
            )
        else:
            st.info(
                f"📊 **Comparativa regional:** En el conjunto de comunidades se acumulan **{dias_ola_calor_sel}** días de ola de calor "
                f"(promedio de **{promedio_comunidades} días** por comunidad; diferencia: **{signo}{diferencia_promedio} días**). "
                f"Selecciona una comunidad en la barra lateral para ver su comparativa individual."
            )
        
        df_sorted_heat = df_region_summary.sort_values(by="dias_ola_calor", ascending=False).head(10)
        
        fig_rank2, ax_r2 = plt.subplots(figsize=(7, 4.5))
        fig_rank2.patch.set_facecolor('#0F172A')
        ax_r2.set_facecolor('#1E293B')
        
        sns.barplot(data=df_sorted_heat, y="comunidad_autonoma", x="dias_ola_calor", hue="comunidad_autonoma", legend=False, palette="Oranges_r", ax=ax_r2)
        ax_r2.set_xlabel("Días Acumulados en Ola de Calor", color='#E2E8F0')
        ax_r2.set_ylabel("")
        ax_r2.grid(True, linestyle=":", alpha=0.25, color='#475569')
        ax_r2.tick_params(colors='#94A3B8')
        st.pyplot(fig_rank2)

with tab3:
    st.markdown("### 🧮 Explorador Interactivo del Dataset (Pandas)")
    st.dataframe(df_filtered, width="stretch")
    
    csv_bytes = df_filtered.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Descargar Dataset Filtrado en Formato CSV",
        data=csv_bytes,
        file_name=f"csic_climate_{region_sel}_{year_range[0]}_{year_range[1]}.csv",
        mime="text/csv"
    )

with tab4:
    st.markdown("### 👥 Organización del Trabajo en Grupos de GitHub")
    
    st.markdown("""
    <div class="group-box">
        <h4>🧮 GRUPO 1: Backend / Ciencia de Datos (<code>src/csic_climate/metrics.py</code>)</h4>
        <p><strong>Tarea:</strong> Implementar una nueva función analítica en Python (por ejemplo <code>calculate_warming_rate_per_decade(df)</code> o <code>detect_extreme_events(df)</code>).</p>
    </div>
    
    <div class="group-box" style="border-left-color: #10B981;">
        <h4>🎨 GRUPO 2: Frontend & Visualización (<code>app.py</code>)</h4>
        <p><strong>Tarea:</strong> Diseñar un nuevo widget interactivo y una tarjeta visual/gráfico en Streamlit que consuma la métrica creada por el Grupo 1.</p>
    </div>
    
    <div class="group-box" style="border-left-color: #F59E0B;">
        <h4>📖 GRUPO 3: Documentación & Ciencia Abierta (<code>README.md</code> y <code>CITATION.cff</code>)</h4>
        <p><strong>Tarea:</strong> Redactar la metodología científica, la descripción de las variables de la base del IPE-CSIC, la guía de instalación y las citas BibTeX.</p>
    </div>
    
    <div class="group-box" style="border-left-color: #EC4899;">
        <h4>🧪 GRUPO 4: Calidad de Software, Testing & CI/CD (<code>tests/</code> y <code>.github/workflows/ci.yml</code>)</h4>
        <p><strong>Tarea:</strong> Crear los tests unitarios con <code>pytest</code> para validar las nuevas funciones y asegurar que la automatización pase limpia en las Pull Requests.</p>
    </div>
    """, unsafe_allow_html=True)

with tab5:
    st.markdown("### ℹ️ Información General, Metodología y Fuentes de Datos")
    
    col_info1, col_info2 = st.columns(2)
    
    with col_info1:
        st.markdown("""
        <div class="group-box" style="border-left-color: #10B981;">
            <h4>🎯 ¿Qué hace esta Aplicación?</h4>
            <p><strong>CSIC ClimateWatch</strong> es un cuadro de mando científico e interactivo desarrollado como proyecto integrador del curso <em>Python para la Ciencia Abierta (CSIC)</em>. Permite auditar, visualizar y comparar la evolución de las series climáticas históricas (1961 - 2024), centrándose en el incremento de temperaturas, episodios de olas de calor e índices de sequía en las 17 Comunidades Autónomas de España.</p>
        </div>
        
        <div class="group-box" style="border-left-color: #3B82F6;">
            <h4>🌐 Recolección de Datos (Open Science)</h4>
            <ul>
                <li><strong>Fuente Meteorológica:</strong> Modelo de reanálisis <strong>ERA5</strong> del <em>Servicio de Cambio Climático de Copernicus (C3S / ECMWF)</em> accesible libremente a través de la API REST de Open-Meteo.</li>
                <li><strong>Período Temporal:</strong> Series mensuales continuas desde enero de 1961 hasta diciembre de 2024 (13.056 observaciones reales).</li>
                <li><strong>Línea Base Climática:</strong> Periodo estándar 1961-1990 utilizado como referencia normalizada internacional.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
    with col_info2:
        st.markdown("""
        <div class="group-box" style="border-left-color: #F59E0B;">
            <h4>🔬 Metodología de Indicadores</h4>
            <ul>
                <li><strong>Anomalía Térmica (°C):</strong> Desviación de la temperatura media mensual observada respecto al promedio de la línea base 1961-1990.</li>
                <li><strong>Índice SPEI de Sequía:</strong> Formulación del <em>Standardised Precipitation-Evapotranspiration Index</em> desarrollada por investigadores del <strong>Instituto Pirenaico de Ecología (IPE-CSIC)</strong> (<a href="https://digital.csic.es/handle/10261/22405" target="_blank" style="color: #60A5FA; text-decoration: underline;">Vicente-Serrano et al., Digital.CSIC Handle: 10261/22405</a>). Un valor de SPEI &le; -1.5 define sequía severa/extrema.</li>



                <li><strong>Olas de Calor:</strong> Conteo acumulado de días al mes con temperaturas máximas observadas &gt; 32 °C.</li>
            </ul>
        </div>
        
        <div class="group-box" style="border-left-color: #EC4899;">
            <h4>📜 Principios FAIR y Ciencia Abierta</h4>
            <ul>
                <li><strong>Encontrable (Findable):</strong> Código fuente alojado públicamente en GitHub y metadatos normalizados.</li>
                <li><strong>Accesible (Accessible):</strong> API abierta y descarga libre del dataset completo en CSV.</li>
                <li><strong>Reutilizable (Reusable):</strong> Licencia libre MIT e inclusión de archivo de citación <code>CITATION.cff</code>.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

