import streamlit as st
import pandas as pd
import plotly.express as px

# 1. CONFIGURACIÓN EJECUTIVA
st.set_page_config(page_title="Executive Insights | Europcar", layout="wide")

# CSS Profesional
st.markdown("""
    <style>
    .stApp { background-color: #F0F2F5; }
    [data-testid="stMetricValue"] { font-size: 34px; color: #1A3922; font-weight: 700; }
    .stMetric { 
        background-color: #FFFFFF; padding: 20px; border-radius: 12px; 
        box-shadow: 0 2px 4px rgba(0,0,0,0.05); border-top: 4px solid #27AE60; 
    }
    .stPlotlyChart { 
        background-color: #FFFFFF; border-radius: 12px; padding: 15px; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    h1, h2, h3 { color: #202124 !important; font-family: 'Segoe UI', sans-serif; }
    </style>
    """, unsafe_allow_html=True)

# 2. CARGA Y ORDENAMIENTO CRONOLÓGICO
URL_CASOS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSzC5OL79p1MJZoel12enc4w9G12hbsd_qICkbeE7N-pDdLqCh2gEuuwc3NbaI_820chNyjcifqVdJj/pub?gid=0&single=true&output=csv"

@st.cache_data(ttl=10)
def load_data():
    df_c = pd.read_csv(URL_CASOS)
    df_c.columns = df_c.columns.str.strip()
    df_c = df_c.fillna("N/A")
    
    if 'MONTH' in df_c.columns:
        orden_meses = ['JANUARY', 'FEBRUARY', 'MARCH', 'APRIL', 'MAY', 'JUNE', 
                       'JULY', 'AUGUST', 'SEPTEMBER', 'OCTOBER', 'NOVEMBER', 'DECEMBER']
        df_c['MONTH'] = df_c['MONTH'].str.strip().str.upper()
        df_c['MONTH'] = pd.Categorical(df_c['MONTH'], categories=orden_meses, ordered=True)
    
    return df_c

df = load_data()

# --- BARRA LATERAL ---
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/e/e0/Europcar_logo.svg/1280px-Europcar_logo.svg.png", width=160)
    st.markdown("---")
    
    tipos = sorted(df['TYPE OF REQUIREMENT'].unique())
    sel_tipo = st.multiselect("Requirement Type", tipos, default=tipos)
    df_filt = df[df['TYPE OF REQUIREMENT'].isin(sel_tipo)].copy()

    meses_disp = sorted(df_filt['MONTH'].unique())
    sel_mes = st.multiselect("Filtrar Mes", meses_disp, default=meses_disp)
    df_filt = df_filt[df_filt['MONTH'].isin(sel_mes)]

    excluir = ['DATE','NAME','ESTADO','ACCION TOMADA','CERRADO SI/NO','INICIO DE RENTA','FUENTE','RENTAL AGREEMENT','FARE','FINAL DE RENTA','BOOKING NUMBER','MONTH'] 
    menu = [c for c in df.select_dtypes(include=['object']).columns if c not in excluir and c != 'TYPE OF REQUIREMENT']
    campo = st.selectbox("Dimensión de Análisis", menu, index=0)

    df_filt[campo] = df_filt[campo].astype(str).str.strip().str.upper()
    elementos_disponibles = sorted(df_filt[campo].unique())
    sel_elementos = st.multiselect(f"Filtrar {campo}", elementos_disponibles, default=elementos_disponibles)
    df_filt = df_filt[df_filt[campo].isin(sel_elementos)]

# --- CUERPO PRINCIPAL ---
st.title("Strategic Analysis Dashboard")
st.markdown(f"**Europcar Intelligence Unit** | Operational Performance Review")

c1, c2, c3 = st.columns(3)
c1.metric("Total Records", f"{len(df):,}")
c2.metric("Filtered Cases", f"{len(df_filt):,}")
c3.metric("Unique Entities", f"{df_filt[campo].nunique():,}")

st.markdown("---")
st.subheader(f"Evolución Mensual: {campo}")

df_trend = df_filt.groupby(['MONTH', campo], observed=True).size().reset_index(name='Count')

if not df_trend.empty:
    fig_trend = px.bar(df_trend, x='MONTH', y='Count', color=campo,
                        barmode='group', text='Count',
                        color_discrete_sequence=px.colors.sequential.Greens_r)
    
    fig_trend.update_traces(textposition='outside')
    fig_trend.update_layout(
        xaxis_title=None, 
        yaxis_title=None, 
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=60, b=60, l=10, r=10),
        # ELIMINAR ESCALAS Y LÍNEAS
        yaxis=dict(showticklabels=False, showgrid=False, zeroline=False),
        xaxis=dict(showgrid=False)
    )
    st.plotly_chart(fig_trend, use_container_width=True)

st.markdown("---")
col_l, col_r = st.columns([1, 1.2])

df_graf = df_filt[df_filt[campo] != "N/A"]

with col_l:
    fig1 = px.pie(df_graf, names=campo, hole=0.5, color_discrete_sequence=px.colors.sequential.Greens_r)
    fig1.update_layout(margin=dict(t=40, b=40, l=10, r=10), paper_bgcolor='rgba(0,0,0,0)', showlegend=False)
    st.plotly_chart(fig1, use_container_width=True)
    
with col_r:
    counts = df_graf[campo].value_counts().reset_index()
    counts.columns = [campo, 'Count']
    fig2 = px.bar(counts.head(15), x='Count', y=campo, orientation='h', 
                    text='Count', color='Count', color_continuous_scale='Greens')
    
    fig2.update_layout(
        margin=dict(t=20, b=20, l=180, r=80), 
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis_title=None,
        yaxis_title=None,
        coloraxis_showscale=False,
        # ELIMINAR ESCALAS Y LÍNEAS
        xaxis=dict(showticklabels=False, showgrid=False, zeroline=False),
        yaxis=dict(showgrid=False)
    )
    st.plotly_chart(fig2, use_container_width=True)

with st.expander("Ver Detalle de Datos (Audit Trail)"):
    st.dataframe(df_filt, use_container_width=True)
