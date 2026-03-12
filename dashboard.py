import streamlit as st
import pandas as pd
import plotly.express as px

# 1. CONFIGURACIÓN EJECUTIVA
st.set_page_config(page_title="Executive Insights | Europcar Mobility Group", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #F4F7F9; }
    [data-testid="stMetricValue"] { font-size: 32px; color: #27AE60; font-weight: 600; }
    .stMetric { 
        background-color: #FFFFFF; padding: 20px; border-radius: 8px; 
        border-top: 4px solid #27AE60; box-shadow: 0 4px 6px rgba(0,0,0,0.05); 
        margin-bottom: 15px;
    }
    .stPlotlyChart { background-color: #FFFFFF; border-radius: 8px; padding: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.02); }
    [data-testid="stSidebar"] { background-color: #FFFFFF; border-right: 1px solid #E0E0E0; }
    </style>
    """, unsafe_allow_html=True)

# 2. CARGA DE DATOS (DATA E IMPACTO)
URL_CASOS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSzC5OL79p1MJZoel12enc4w9G12hbsd_qICkbeE7N-pDdLqCh2gEuuwc3NbaI_820chNyjcifqVdJj/pub?gid=0&single=true&output=csv"
URL_IMPACTO = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSzC5OL79p1MJZoel12enc4w9G12hbsd_qICkbeE7N-pDdLqCh2gEuuwc3NbaI_820chNyjcifqVdJj/pub?gid=397203880&single=true&output=csv"

@st.cache_data(ttl=5) # Caché ultra-rápida para pruebas en tiempo real
def load_data():
    df_c = pd.read_csv(URL_CASOS).fillna("N/A")
    try:
        # Forzamos la lectura limpia de la hoja de impacto
        df_i = pd.read_csv(URL_IMPACTO)
        df_i.columns = df_i.columns.str.strip()
        # Eliminamos filas que sean completamente nulas
        df_i = df_i.dropna(how='all')
    except:
        df_i = pd.DataFrame()
    return df_c, df_i

df, df_impacto = load_data()

# --- BARRA LATERAL (CONTROL PANEL) ---
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/e/e0/Europcar_logo.svg/1280px-Europcar_logo.svg.png", width=160)
    
    # Filtros Ejecutivos
    st.markdown("### **Executive Filters**")
    if 'TYPE OF REQUIREMENT' in df.columns:
        tipos = sorted(df['TYPE OF REQUIREMENT'].unique())
        sel_tipo = st.multiselect("Requirement Type", tipos, default=['COMPLAINT'] if 'COMPLAINT' in tipos else [tipos[0]])
        df_filt = df[df['TYPE OF REQUIREMENT'].isin(sel_tipo)]
    else:
        df_filt = df

    # Limpieza de Dimensiones
    cols_disponibles = [c for c in df.select_dtypes(include=['object']).columns if c != 'TYPE OF REQUIREMENT']
    excluir = ['MONTH', 'DATE', 'NAME', 'BOOKING NUMBER', 'ESTADO', 'ACCION TOMADA', 'CERRADO SI/NO', 
               'INICIO DE RENTA', 'FUENTE', 'RENTAL AGREEMENT', 'FARE', 'FINAL DE RENTA', 'Month_Name'] 
    menu_final = [c for c in cols_disponibles if c not in excluir]
    campo = st.selectbox("Analysis Dimension", menu_final, index=0)

    st.markdown("---")
    st.markdown("### **Performance Impact (YTD)**")
    
    # --- PROCESAMIENTO DINÁMICO DE MESES ---
    if not df_impacto.empty:
        col_mes = [c for c in df_impacto.columns if 'MES' in c.upper()][0]
        col_pct = [c for c in df_impacto.columns if '%' in c or 'IMPACTO' in c.upper()][0]

        for _, row in df_impacto.iterrows():
            mes_raw = str(row[col_mes]).strip()
            valor_impacto = str(row[col_pct]).strip()
            
            # Condición mejorada: Si hay un valor en impacto, muéstralo
            if valor_impacto and valor_impacto != "nan" and valor_impacto != "":
                # Limpiamos el nombre del mes para que se vea elegante
                mes_display = mes_raw.capitalize()
                st.metric(label=f"Impact {mes_display}", value=valor_impacto)

# --- PANEL PRINCIPAL ---
st.title("Strategic Analysis Dashboard")
st.markdown(f"**Europcar Intelligence Unit** | 2026 Operational Performance Review")

# KPIs Principales
k1, k2, k3 = st.columns(3)
with k1: st.metric("Total Records", f"{len(df):,}")
with k2: st.metric("Filtered Cases", f"{len(df_filt):,}")
with k3: st.metric("Unique Entities", f"{df_filt[campo].nunique():,}")

st.markdown("---")

# Visualización (BI Layout)
st.subheader(f"Statistical Distribution by {campo}")
df_graf = df_filt[df_filt[campo] != "N/A"]

if not df_graf.empty:
    c_left, c_right = st.columns([1, 1.2]) 
    with c_left:
        fig_pie = px.pie(df_graf, names=campo, hole=0.5, color_discrete_sequence=px.colors.sequential.Greens_r)
        fig_pie.update_traces(textinfo='percent', textfont_size=12)
        fig_pie.update_layout(showlegend=False, paper_bgcolor='rgba(0,0,0,0)', margin=dict(t=40, b=40, l=10, r=10))
        st.plotly_chart(fig_pie, use_container_width=True)
        
    with c_right:
        counts = df_graf[campo].value_counts().reset_index()
        counts.columns = [campo, 'Count']
        fig_bar = px.bar(counts.head(12), x='Count', y=campo, orientation='h', text='Count', 
                         color='Count', color_continuous_scale='Greens')
        fig_bar.update_traces(textposition='outside', marker_line_color='#FFFFFF', marker_line_width=1)
        fig_bar.update_layout(xaxis_title="Volume", yaxis_title=None, paper_bgcolor='rgba(0,0,0,0)', 
                              plot_bgcolor='rgba(0,0,0,0)', coloraxis_showscale=False)
        st.plotly_chart(fig_bar, use_container_width=True)
else:
    st.info("No qualitative data available for the current selection.")

with st.expander("Detailed Audit Trail"):
    st.dataframe(df_filt, use_container_width=True)