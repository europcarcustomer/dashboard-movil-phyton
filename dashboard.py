import streamlit as st
import pandas as pd
import plotly.express as px

# 1. CONFIGURACIÓN EJECUTIVA
st.set_page_config(page_title="Executive Insights | Europcar Mobility Group", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #F4F7F9; }
    [data-testid="stMetricValue"] { font-size: 32px; color: #27AE60; font-weight: 600; }
    .stMetric { background-color: #FFFFFF; padding: 20px; border-radius: 8px; border-top: 4px solid #27AE60; margin-bottom: 15px; }
    .stPlotlyChart { background-color: #FFFFFF; border-radius: 8px; padding: 15px; }
    </style>
    """, unsafe_allow_html=True)

# 2. CARGA DE DATOS
URL_CASOS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSzC5OL79p1MJZoel12enc4w9G12hbsd_qICkbeE7N-pDdLqCh2gEuuwc3NbaI_820chNyjcifqVdJj/pub?gid=0&single=true&output=csv"
URL_IMPACTO = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSzC5OL79p1MJZoel12enc4w9G12hbsd_qICkbeE7N-pDdLqCh2gEuuwc3NbaI_820chNyjcifqVdJj/pub?gid=397203880&single=true&output=csv"

@st.cache_data(ttl=10)
def load_data():
    df_c = pd.read_csv(URL_CASOS)
    df_c.columns = df_c.columns.str.strip()
    df_c = df_c.fillna("N/A")
    try:
        df_i = pd.read_csv(URL_IMPACTO)
        df_i.columns = df_i.columns.str.strip()
    except:
        df_i = pd.DataFrame()
    return df_c, df_i

df, df_impacto = load_data()

# --- BARRA LATERAL ---
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/e/e0/Europcar_logo.svg/1280px-Europcar_logo.svg.png", width=160)
    st.markdown("### **Executive Filters**")
    
    # 1. FILTRO DE TIPO (Igual que antes)
    tipos = sorted(df['TYPE OF REQUIREMENT'].unique())
    sel_tipo = st.multiselect("Requirement Type", tipos, default=tipos)
    df_filt = df[df['TYPE OF REQUIREMENT'].isin(sel_tipo)].copy()

    # 2. SELECCIÓN DE DIMENSIÓN
    excluir = ['DATE','NAME','ESTADO','ACCION TOMADA','CERRADO SI/NO','INICIO DE RENTA','FUENTE','RENTAL AGREEMENT','FARE','FINAL DE RENTA','BOOKING NUMBER','MONTH', 'Month_Name'] 
    menu = [c for c in df.select_dtypes(include=['object']).columns if c not in excluir and c != 'TYPE OF REQUIREMENT']
    campo = st.selectbox("Analysis Dimension", menu, index=0)

    # --- NUEVA FUNCIÓN: FILTRAR ELEMENTOS DE LA DIMENSIÓN ---
    # Unificamos primero para que el filtro no tenga duplicados
    df_filt[campo] = df_filt[campo].astype(str).str.strip().str.upper()
    elementos_disponibles = sorted(df_filt[campo].unique())
    
    # Creamos el multiselect para los elementos de esa dimensión
    sel_elementos = st.multiselect(f"Filter {campo}", elementos_disponibles, default=elementos_disponibles)
    
    # Aplicamos el filtro al dataframe final
    df_filt = df_filt[df_filt[campo].isin(sel_elementos)]

    st.markdown("---")
    st.markdown("### **Performance Impact (YTD)**")
    
    if not df_impacto.empty:
        col_mes = [c for c in df_impacto.columns if 'MES' in c.upper()][0]
        col_pct = [c for c in df_impacto.columns if '%' in c or 'IMPACTO' in c.upper()][0]
        for _, row in df_impacto.iterrows():
            mes = str(row[col_mes]).strip().capitalize()
            if mes != "Nan" and mes != "":
                st.metric(label=f"Impact {mes}", value=str(row[col_pct]).strip())

# --- CUERPO PRINCIPAL ---
st.title("Strategic Analysis Dashboard")
st.markdown(f"**Europcar Intelligence Unit** | 2026 Operational Performance Review")

c1, c2, c3 = st.columns(3)
c1.metric("Total Records", f"{len(df):,}")
c2.metric("Filtered Cases", f"{len(df_filt):,}")
c3.metric("Unique Entities", f"{df_filt[campo].nunique():,}")

st.markdown("---")
st.subheader(f"Statistical Distribution by {campo}")

df_graf = df_filt[df_filt[campo] != "N/A"]

if not df_graf.empty:
    col_l, col_r = st.columns([1, 1.2])
    with col_l:
        fig1 = px.pie(df_graf, names=campo, hole=0.5, color_discrete_sequence=px.colors.sequential.Greens_r)
        fig1.update_layout(showlegend=False, margin=dict(t=40, b=40, l=10, r=10))
        st.plotly_chart(fig1, use_container_width=True)
        
    with col_r:
        counts = df_graf[campo].value_counts().reset_index()
        counts.columns = [campo, 'Count']
        
        fig2 = px.bar(counts.head(15), x='Count', y=campo, orientation='h', 
                         text='Count', color='Count', color_continuous_scale='Greens')
        
        fig2.update_traces(textposition='outside', marker_line_color='#FFFFFF', marker_line_width=1)
        fig2.update_layout(xaxis_title="Volume", yaxis_title=None, coloraxis_showscale=False)
        st.plotly_chart(fig2, use_container_width=True)
else:
    st.info("No data available for the current selection. Please adjust the filters.")

with st.expander("Detailed Audit Trail"):
    st.dataframe(df_filt, use_container_width=True)
