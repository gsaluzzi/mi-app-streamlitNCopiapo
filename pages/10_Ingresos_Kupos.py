

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from componentes import subheader_custom, metric_coloreado, fetch_all_from_supabase
from utilities import get_gsheet_df
from auth.permissions import require_auth, check_session_timeout
# from auth.auth import check_session_timeout
from ui import render_sidebar_user


check_session_timeout()
require_auth(["admin"])
render_sidebar_user()


st.set_page_config(layout="wide")

@st.cache_data(ttl=3600)
def get_table_cached(table_name):
    return fetch_all_from_supabase(table_name)

transacciones = get_table_cached("transacciones")

meses = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
    5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
    9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
}

SHEET_ID_FAC = "1N7glUY1cv2bO-H0MZeGtxL0VlNd7f47YohXQOH3TjCY"

df_Scot= get_gsheet_df(
    sheet_id=SHEET_ID_FAC,
    worksheet_name="Hoja 1"
)

df_param= get_gsheet_df(
    sheet_id=SHEET_ID_FAC,
    worksheet_name="Kupos"
)

columnas_numericas2 = [
    "Costo validadores",
    "Cuota credito"
]

for col in columnas_numericas2:
    df_param[col] = (
        df_param[col]
        .astype(str)
        .str.replace(".", "", regex=False)
        .str.replace(",", ".", regex=False)
    )
    df_param[col] = pd.to_numeric(df_param[col], errors="coerce")






df_Scot["Fecha"] = pd.to_datetime(df_Scot["Fecha"], dayfirst=True)
df_Scot["Mes"] = df_Scot["Fecha"].dt.month.map(meses)
df_Scot["Monto"] = df_Scot["Cargo"]*-1

columnas_numericas = [
    "Cargo",
    "Abono",
    "Numero Documento",
    "Monto",
    "Saldo Diario"
]

for col in columnas_numericas:
    df_Scot[col] = (
        df_Scot[col]
        .astype(str)
        .str.replace(".", "", regex=False)
        .str.replace(",", ".", regex=False)
    )
    df_Scot[col] = pd.to_numeric(df_Scot[col], errors="coerce")
df_Scot = df_Scot.fillna(0)
df_Scot["Tipo"]= (df_Scot["Abono"] == 0).astype(int)  #----- 1 es Cargo 0 es Abono------


df_ScotKupos=df_Scot[df_Scot["Glosa"]=="Ingreso Kupos"]

tabla_kupos=pd.pivot_table(df_ScotKupos, 
                     values=["Abono"],
                     index="Fecha",
                    #  columns="Semana",
                     aggfunc="sum")
tabla_kupos= tabla_kupos.reset_index()
color_barra="#2C3E50"
fig = go.Figure()

fig.add_bar(
    x=tabla_kupos["Fecha"],
    y=tabla_kupos["Abono"],
    marker_color=color_barra,
    # customdata=resumen["variacion_pct"],
    # hovertemplate=(
    #     "<b>%{x}</b><br>"
    #     "Monto: $%{y:,.0f}<br>"
    #     "Variación: %{customdata:.1f}% vs presupuesto"
    #     "<extra></extra>"
    # ),
    # text=[f"${v:,.0f}".replace(",", ".") for v in resumen[col_monto]],
    textfont=dict(size=12, color='black', family='Arial Black'),
    textposition="outside"
    )

    # -----------------------------
    # Banda de tolerancia
    # -----------------------------

    # Ajuste eje Y
# max_val = max(tabla_kupos["Abono"].max(), limite_sup)
# fig.update_yaxes(range=[0, max_val * 1.15])

fig.update_layout(
    title="Abonos Kupos",
    yaxis_title="Monto ($)",
    xaxis_title="Día",
    showlegend=False,
    height=240,
    margin=dict(t=70, b=40)
)







recaudacion_total=transacciones["recaudación"].sum()
comisiones_total=transacciones["comisión"].sum()
soporte_total=df_param["Costo validadores"].sum()
credito_total=df_param["Cuota credito"].sum()


recaudacion_efectiva=recaudacion_total-comisiones_total-soporte_total-credito_total
abonado_total=df_ScotKupos["Abono"].sum()

diferencia=recaudacion_efectiva-abonado_total

st.title("📊 Ingresos Kupos")
st.markdown("---")
subheader_custom("Recaudación")

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    metric_coloreado("Monto Total Recaudado", recaudacion_total, delta=None, color_texto='white', color_fondo="#2b8d5b", formato="moneda")

with col2:
    metric_coloreado("Comisiones Kupos", comisiones_total, delta=None, color_texto='white', color_fondo="#e14c4c", formato="moneda")

with col3:
    metric_coloreado("Costo Validadores", soporte_total, delta=None, color_texto='white', color_fondo="#e14c4c", formato="moneda")

with col4:
    metric_coloreado("Monto Pagos Creditos", credito_total, delta=None, color_texto='white', color_fondo="#e14c4c", formato="moneda")

with col5:
    metric_coloreado("Ingreso Neto", recaudacion_efectiva, delta=None, color_texto='white', color_fondo="#1a8486", formato="moneda")

st.markdown("---")

subheader_custom("Abonos")
col6, col7 = st.columns([4,1])

with col6:
    st.plotly_chart(fig)

with col7:
    subheader_custom("", size=60)
    metric_coloreado("Total Abonos", abonado_total, delta=None, color_texto='white', color_fondo="#1a8486", formato="moneda")

st.markdown("---")

metric_coloreado("Desfase", diferencia, delta=None, color_texto='white', color_fondo="#162b7f", formato="moneda")
