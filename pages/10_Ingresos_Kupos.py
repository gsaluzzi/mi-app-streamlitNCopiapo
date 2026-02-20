

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from componentes import subheader_custom, metric_coloreado, fetch_all_from_supabase, asignarTerminal, semana_relativa
from utilities import get_gsheet_df
from auth.permissions import require_auth, check_session_timeout
from ui import render_sidebar_user
import plotly.express as px



check_session_timeout()
require_auth(["admin"])
render_sidebar_user()


st.set_page_config(layout="wide")

@st.cache_data(ttl=3600)
def get_table_cached(table_name):
    return fetch_all_from_supabase(table_name)

transacciones = get_table_cached("transacciones")
expediciones = get_table_cached("expediciones")


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

expediciones = expediciones.rename(columns={
    "fecha": "Fecha",
    "estado": "Estado",
    "terminal": "Terminal",
    "servicio": "Servicio"
})
expediciones["Fecha"] = pd.to_datetime(expediciones["Fecha"], dayfirst=True)
expediciones["Estado"] = expediciones["Estado"].str.lower().str.strip()
expediciones["Terminal"] = expediciones["Servicio"].apply(asignarTerminal)
expediciones["Semana"]= semana_relativa(expediciones["Fecha"], "2025-10-13")
expediciones["es_valida"]= (expediciones["Estado"].str.lower() == "valida").astype(int)

expediciones = expediciones[expediciones['causa']!='Cortadas por inverso']
expediciones["Mes"] = expediciones["Fecha"].dt.month.map(meses)
expediciones["Año"] = expediciones["Fecha"].dt.year
expediciones["Expediciones"] = 1


# def grafico_recaudacion_apilada_pct(
#     df,
#     col_mes="mes",
#     col_terminal="terminal",
#     col_valor="recaudacion",
#     colores_terminales=None
# ):
#     # -----------------------------
#     # Agrupar y calcular porcentajes
#     # -----------------------------
    
#     orden_meses = [
#         "Septiembre", "Octubre", "Noviembre", "Diciembre","Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
#         "Julio", "Agosto"
#     ]
#     df[col_mes] = pd.Categorical(df[col_mes], categories=orden_meses, ordered=True)
    
#     resumen = (
#         df.groupby([col_mes, col_terminal], as_index=False, observed=True)[col_valor]
#         .sum()
#     )

#     resumen["total_mes"] = resumen.groupby(col_mes)[col_valor].transform("sum")
#     resumen["pct"] = resumen[col_valor] / resumen["total_mes"] * 100

#     # -----------------------------
#     # Orden de meses (tal como vienen)
#     # -----------------------------
#     meses2 = resumen[col_mes].unique()

#     # -----------------------------
#     # Colores fijos por terminal
#     # -----------------------------
#     if colores_terminales is None:
#         colores_terminales = {
#             "Los Heroes": "#1f77b4",
#             "Terrapuerto": "#ff7f0e",
#             "Paipote": "#2ca02c"
#         }

#     # -----------------------------
#     # Construcción del gráfico
#     # -----------------------------
#     fig = go.Figure()

#     for terminal, color in colores_terminales.items():
#         df_t = resumen[resumen[col_terminal] == terminal]

#         fig.add_bar(
#             x=df_t[col_mes],
#             y=df_t["pct"],
#             name=terminal,
#             marker_color=color,
#             text=df_t["pct"].round(1).astype(str) + "%",
#             textposition="inside",
#             textfont=dict(size=14, color='white', family='Arial Black'),
#             hovertemplate=(
#                 f"<b>{terminal}</b><br>"
#                 "Mes: %{x}<br>"
#                 "Participación: %{y:.1f}%<extra></extra>"
#             )
#         )

#     # -----------------------------
#     # Layout
#     # -----------------------------
#     fig.update_layout(
#         barmode="stack",
#         yaxis=dict(
#             title="% Recaudación",
#             ticksuffix="%",
#             range=[0, 100]
#         ),
#         # xaxis=dict(title="Mes"),
#         legend_title="Terminal",
#         height=320
#     )
#     fig.update_layout(
#     legend=dict(
#         orientation="h",          # horizontal
#         yanchor="top",
#         y=-0.2,                  # posición vertical (ajusta si hace falta)
#         xanchor="center",
#         x=0.5                     # centrada
#     )
# )


#     return fig

def resaltar_total_fila(row):
    if row.name == "Total":
        return ["background-color: #e6f2ff; font-weight: bold"] * len(row)
    return [""] * len(row)

def formato_moneda_cl(val):
    if pd.isna(val):
        return ""
    return f"${val:,.0f}".replace(",", ".")

def tabla_recaudacion_ultimos_4_meses(
    df,
    col_fecha="fecha",
    col_terminal="Terminal",
    col_mes="Mes",
    col_valor="Recaudación",
    orden_terminales=None,
    incluir_total=True
):
    df = df.copy()

    # ---------------------------------
    # Fechas y últimos 4 meses reales
    # ---------------------------------
    df["fecha_dt"] = pd.to_datetime(df[col_fecha], format="%d-%m-%Y")
    df["mes_periodo"] = df["fecha_dt"].dt.to_period("M")

    ultimos_4 = df["mes_periodo"].sort_values().unique()[-4:]
    df = df[df["mes_periodo"].isin(ultimos_4)]

    # ---------------------------------
    # Orden cronológico real de meses
    # ---------------------------------
    orden_meses = (
        df[["mes_periodo", col_mes]]
        .drop_duplicates()
        .sort_values("mes_periodo")[col_mes]
        .tolist()
    )

    df[col_mes] = pd.Categorical(
        df[col_mes],
        categories=orden_meses,
        ordered=True
    )

    # ---------------------------------
    # Pivot
    # ---------------------------------
    tabla = pd.pivot_table(
        df,
        values=col_valor,
        index=col_terminal,
        columns=col_mes,
        aggfunc="sum",
        fill_value=0
    )

    # ---------------------------------
    # Orden personalizado de terminales
    # ---------------------------------
    if orden_terminales:
        tabla = tabla.reindex(orden_terminales)

    # ---------------------------------
    # Ocultar meses en 0
    # ---------------------------------
    tabla = tabla.loc[:, (tabla != 0).any(axis=0)]

    # ---------------------------------
    # Fila TOTAL
    # ---------------------------------
    if incluir_total:
        tabla.loc["Total"] = tabla.sum(axis=0)

    return tabla



def grafico_recaudacion_apilada_pct_2(
    df,
    col_fecha="fecha",
    col_mes="mes",
    col_terminal="terminal",
    col_valor="recaudacion",
    colores_terminales=None
):
    df = df.copy()

    # -----------------------------
    # Preparar fechas y últimos 4 meses
    # -----------------------------
    df["fecha_dt"] = pd.to_datetime(df[col_fecha], format="%d-%m-%Y")
    df["mes_orden"] = df["fecha_dt"].dt.to_period("M")

    ultimos_4_meses = (
        df["mes_orden"]
        .sort_values()
        .unique()[-4:]
    )

    df = df[df["mes_orden"].isin(ultimos_4_meses)]

    # -----------------------------
    # Orden cronológico real
    # -----------------------------
    orden_meses = (
        df[["mes_orden", col_mes]]
        .drop_duplicates()
        .sort_values("mes_orden")[col_mes]
        .tolist()
    )

    df[col_mes] = pd.Categorical(df[col_mes], categories=orden_meses, ordered=True)

    # -----------------------------
    # Agrupación y porcentajes
    # -----------------------------
    resumen = (
        df.groupby([col_mes, col_terminal], as_index=False)[col_valor]
        .sum()
    )

    resumen["total_mes"] = resumen.groupby(col_mes)[col_valor].transform("sum")
    resumen["pct"] = resumen[col_valor] / resumen["total_mes"] * 100

    # -----------------------------
    # Colores fijos
    # -----------------------------
    if colores_terminales is None:
        colores_terminales = {
            "Los Heroes": "#1f77b4",
            "Terrapuerto": "#ff7f0e",
            "Paipote": "#2ca02c"
        }

    # -----------------------------
    # Gráfico
    # -----------------------------
    fig = go.Figure()

    for terminal, color in colores_terminales.items():
        df_t = resumen[resumen[col_terminal] == terminal]

        fig.add_bar(
            x=df_t[col_mes],
            y=df_t["pct"],
            name=terminal,
            marker_color=color,
            text=df_t["pct"].round(1).astype(str) + "%",
            textposition="inside",
            textfont=dict(size=14, color='white', family='Arial Black'),
            hovertemplate=(
                f"<b>{terminal}</b><br>"
                "Mes: %{x}<br>"
                "Participación: %{y:.1f}%<extra></extra>"
            )
        )

    # -----------------------------
    # Layout
    # -----------------------------
    fig.update_layout(
        barmode="stack",
        yaxis=dict(title="% Recaudación", ticksuffix="%", range=[0, 100]),
        height=320,
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.25,
            xanchor="center",
            x=0.5
        )
    )

    return fig






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

transacciones = transacciones.rename(columns={
    "fecha": "Fecha",
    "transacciones": "Transacciones",
    "recaudación":"Recaudación",
    "comisión":"Comisión",
    "waybill number":"Waybill number",
    "servicio":"Servicio"
})

transacciones["Terminal"] = transacciones["Servicio"].apply(asignarTerminal)
transacciones["Semana"]= semana_relativa(transacciones["Fecha"], "2025-10-13")
transacciones["Fecha"] = pd.to_datetime(transacciones["Fecha"], dayfirst=True)

meses = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
    5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
    9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
}

transacciones["Mes"] = transacciones["Fecha"].dt.month.map(meses)
transacciones["Año"] = transacciones["Fecha"].dt.year


recaudacion_total=transacciones["Recaudación"].sum()
comisiones_total=transacciones["Comisión"].sum()
soporte_total=df_param["Costo validadores"].sum()
credito_total=df_param["Cuota credito"].sum()


recaudacion_efectiva=recaudacion_total-comisiones_total-soporte_total-credito_total
abonado_total=df_ScotKupos["Abono"].sum()

diferencia=recaudacion_efectiva-abonado_total


fig2 = grafico_recaudacion_apilada_pct_2(transacciones, col_mes="Mes", col_terminal="Terminal", col_valor="Recaudación", col_fecha="Fecha")

# orden_meses = [
#     "Septiembre", "Octubre", "Noviembre", "Diciembre",
#     "Enero", "Febrero", "Marzo", "Abril",
#     "Mayo", "Junio", "Julio", "Agosto"
# ]

tabla_2 = tabla_recaudacion_ultimos_4_meses(transacciones, col_fecha="Fecha",orden_terminales=["Paipote", "Terrapuerto", "Los Heroes"])
styler = (
    tabla_2
    .style
    .apply(resaltar_total_fila, axis=1)
    .format(lambda x: f"${x:,.0f}" if pd.notna(x) else "-")
)
# tabla_2=tabla_2.reset_index()


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
col6, col7, col8 = st.columns([3,1,1])

with col6:
    st.plotly_chart(fig)

with col7:
    subheader_custom("", size=60)
    metric_coloreado("Total Abonos", abonado_total, delta=None, color_texto='white', color_fondo="#1a8486", formato="moneda")

with col8:
    subheader_custom("", size=60)
    metric_coloreado("Desfase", diferencia, delta=None, color_texto='white', color_fondo="#162b7f", formato="moneda")


st.markdown("---")
subheader_custom("Recaudación por Terminal", size=20)
col9, col10= st.columns([1,1])
with col9:
    st.plotly_chart(fig2, use_container_width=True)
    
with col10:
    subheader_custom("", size=40)
    st.dataframe(styler, use_container_width=True, hide_index=False)

st.markdown("---")
transacciones2=transacciones[transacciones["Servicio"]!="SIN INFORMACIÓN"]

meses2 = sorted(transacciones2["Mes"].unique())
opciones = ["TODOS"] + meses2





subheader_custom("Recaudación por Línea", size=20)
col11, col12 = st.columns([1,4])

with col11:
    mes_sel = st.selectbox("Selecciona mes", opciones)



if mes_sel == "TODOS":
    transacciones_filtrado= transacciones2.copy()
else:
    transacciones_filtrado = transacciones2[transacciones2["Mes"] == mes_sel]

if mes_sel == "TODOS":
    expediciones_filtrado= expediciones.copy()
else:
    expediciones_filtrado = expediciones[expediciones["Mes"] == mes_sel]


tabla_lh=pd.pivot_table(transacciones_filtrado[transacciones_filtrado["Terminal"]=="Los Heroes"], 
                     values=["Recaudación"],
                     index="Servicio",
                    #  columns="Terminal",
                     aggfunc="sum")
tabla_exp_lh=pd.pivot_table(expediciones_filtrado[expediciones_filtrado["Terminal"]=="Los Heroes"], 
                     values=["Expediciones"],
                     index="Servicio",
                    #  columns="Terminal",
                     aggfunc="sum")
tabla_final_lh=pd.merge(tabla_lh, tabla_exp_lh, on="Servicio", how="left")
tabla_final_lh.loc["Total"] = tabla_final_lh.sum(axis=0)
tabla_final_lh["RecXExp"]=tabla_final_lh["Recaudación"]/tabla_final_lh["Expediciones"]


tabla_paipo=pd.pivot_table(transacciones_filtrado[transacciones_filtrado["Terminal"]=="Paipote"], 
                     values=["Recaudación"],
                     index="Servicio",
                    #  columns="Terminal",
                     aggfunc="sum")
tabla_exp_paipo=pd.pivot_table(expediciones_filtrado[expediciones_filtrado["Terminal"]=="Paipote"], 
                     values=["Expediciones"],
                     index="Servicio",
                    #  columns="Terminal",
                     aggfunc="sum")
tabla_final_paipo=pd.merge(tabla_paipo, tabla_exp_paipo, on="Servicio", how="left")
tabla_final_paipo.loc["Total"] = tabla_final_paipo.sum(axis=0)
tabla_final_paipo["RecXExp"]=tabla_final_paipo["Recaudación"]/tabla_final_paipo["Expediciones"]

tabla_terra=pd.pivot_table(transacciones_filtrado[transacciones_filtrado["Terminal"]=="Terrapuerto"], 
                     values=["Recaudación"],
                     index="Servicio",
                    #  columns="Terminal",
                     aggfunc="sum")
tabla_exp_terra=pd.pivot_table(expediciones_filtrado[expediciones_filtrado["Terminal"]=="Terrapuerto"], 
                     values=["Expediciones"],
                     index="Servicio",
                    #  columns="Terminal",
                     aggfunc="sum")
tabla_final_terra=pd.merge(tabla_terra, tabla_exp_terra, on="Servicio", how="left")
tabla_final_terra.loc["Total"] = tabla_final_terra.sum(axis=0)
tabla_final_terra["RecXExp"]=tabla_final_terra["Recaudación"]/tabla_final_terra["Expediciones"]

col13, col14, col15 = st.columns(3)

with col13:
    subheader_custom("Paipote")
    st.dataframe(tabla_final_paipo.style
    .apply(resaltar_total_fila, axis=1) 
    .format({"Recaudación" : lambda x: f"${x:,.0f}" if pd.notna(x) else "-", 
             "Expediciones": lambda x: f"{x:,.0f}" if pd.notna(x) else "-",
             "RecXExp": lambda x: f"${x:,.0f}" if pd.notna(x) else "-"}), use_container_width=True)

with col14:
    subheader_custom("Los Heroes")
    st.dataframe(tabla_final_lh.style
    .apply(resaltar_total_fila, axis=1) 
    .format({"Recaudación" : lambda x: f"${x:,.0f}" if pd.notna(x) else "-", 
             "Expediciones": lambda x: f"{x:,.0f}" if pd.notna(x) else "-",
             "RecXExp": lambda x: f"${x:,.0f}" if pd.notna(x) else "-"}), use_container_width=True)

with col15:
    subheader_custom("Terrapuerto")
    st.dataframe(tabla_final_terra.style
    .apply(resaltar_total_fila, axis=1) 
    .format({"Recaudación" : lambda x: f"${x:,.0f}" if pd.notna(x) else "-", 
             "Expediciones": lambda x: f"{x:,.0f}" if pd.notna(x) else "-",
             "RecXExp": lambda x: f"${x:,.0f}" if pd.notna(x) else "-"}), use_container_width=True)
