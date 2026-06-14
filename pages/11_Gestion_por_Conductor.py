

import streamlit as st
import pandas as pd
from datetime import datetime
from utilities import get_gsheet_df
import plotly.graph_objects as go
from componentes import asignarTerminal, fetch_all_from_supabase, subheader_custom
from auth.permissions import require_auth, check_session_timeout
from plotly.subplots import make_subplots
import plotly.express as px

from ui import render_sidebar_user

check_session_timeout()
require_auth(["admin"])
render_sidebar_user()


st.set_page_config(layout="wide")

@st.cache_data(ttl=3600)
def get_table_cached(table_name):
    return fetch_all_from_supabase(table_name)

df2 = get_table_cached("expediciones")

meses = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
    5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
    9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
}


df2 = df2.rename(columns={
    "fecha": "Fecha",
    "estado": "Estado",
    "terminal": "Terminal",
    "servicio": "Servicio"
})


df2["Fecha"] = pd.to_datetime(df2["Fecha"], dayfirst=True)
df2["Estado"] = df2["Estado"].str.lower().str.strip()
df2["Terminal"] = df2["Servicio"].apply(asignarTerminal)
df2["es_valida"]= (df2["Estado"].str.lower() == "valida").astype(int)

df2 = df2[df2['causa']!='Cortadas por inverso']
df2["Expedicion"]=1


df2["inicio_expedicion"] = pd.to_datetime(df2["inicio_expedicion"])
df2["fin_expedicion"] = pd.to_datetime(df2["fin_expedicion"])

df2["Mes"] = df2["Fecha"].dt.month.map(meses)
df2["Año"] = df2["Fecha"].dt.year

df2["duracion"] = df2["fin_expedicion"] - df2["inicio_expedicion"]
df2["duracion_min"] = df2["duracion"].dt.total_seconds() / 60
df2["duracion_horas"] = df2["duracion"].dt.total_seconds() / 3600

df2["duracion_hhmmss"] = (
    df2["duracion"].dt.total_seconds()
    .apply(lambda x: f"{int(x//3600):02}:{int((x%3600)//60):02}:{int(x%60):02}")
)

orden_meses = [
        "Octubre", "Noviembre", "Diciembre","Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
        "Julio", "Agosto", "Septiembre"
    ]
df2["Mes"] = pd.Categorical(df2["Mes"], categories=orden_meses, ordered=True)
df2["Mes"] = df2["Mes"].cat.remove_unused_categories()

chofer = sorted(df2["chofer"].dropna().astype(str).unique())
# opciones = ["TODOS"] + chofer
# meses2 = sorted(df2["Mes"].unique())


st.title("👤 Gestión por Conductor")
st.markdown("---")

col1, col2= st.columns(2)
with col1:
    chofer_sel = st.selectbox("Selecciona Conductor", chofer)

subheader_custom("Histórico Expediciones")

expediciones_filtrado = df2[df2["chofer"] == chofer_sel]

tabla_exp=pd.pivot_table(expediciones_filtrado, 
                     values=["Expedicion", "es_valida"],
                     index="Mes",
                    #  columns="Terminal",
                     aggfunc="sum")
tabla_exp = tabla_exp.reset_index()
tabla_exp["porc_validas"]=tabla_exp["es_valida"]/tabla_exp["Expedicion"]

tabla_exp2=tabla_exp[tabla_exp["Expedicion"]>0]

fig_evo=go.Figure()

fig_evo = make_subplots(specs=[[{"secondary_y": True}]])

fig_evo.add_trace(
    go.Scatter(
        x=tabla_exp2["Mes"],
        y=tabla_exp2["Expedicion"],
        mode="lines+markers+text",
        text=tabla_exp2["Expedicion"],
        textfont=dict(size=14, color='black', family='Arial Black'),
        textposition="top center",
        name="Expediciones Realizadas"
    ),
    secondary_y=False
)
fig_evo.add_trace(
    go.Scatter(
        x=tabla_exp2["Mes"],
        y=tabla_exp2["porc_validas"],
        mode="lines+markers+text",
        text=tabla_exp2["porc_validas"].apply(lambda x: f"{x:.0%}"),
        textfont=dict(size=12, color='black', family='Arial Black'),
        textposition="top center",
        name="% Exp válidas"
    ),
    secondary_y=True
)


# promedio=100
# color_linea="#2C3E50"
# fig_evo.add_hline(
#         y=promedio,
#         line_dash="dash",
#         line_color=color_linea,
#         annotation_text="Promedio",
#         annotation_position="top left"
#     )




fig_evo.update_layout(title="Expediciones por mes", template='ygridoff',
                      legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.15,
            xanchor="center",
            x=0.5
        ))
fig_evo.update_yaxes(range=[tabla_exp2["Expedicion"].min()*0.8,tabla_exp2["Expedicion"].max()*1.5], secondary_y=False)
fig_evo.update_yaxes(range=[0,1.1], secondary_y=True, tickformat=".0%")

meses2 = sorted(expediciones_filtrado["Mes"].unique())



# with col2:
#     mes_sel = st.selectbox("Selecciona Mes", meses2)
col3, col4= st.columns([3,1])
with col3:
    st.plotly_chart(fig_evo)
st.markdown("---")
subheader_custom("Análisis según mes")
col5, col6= st.columns(2)
with col5:
    mes_sel = st.selectbox("Selecciona Mes", meses2)

expediciones_filtrado2=expediciones_filtrado[expediciones_filtrado["Mes"]==mes_sel]


expediciones_filtrado2["inicio_hora"] = pd.to_datetime(expediciones_filtrado2["inicio_expedicion"].dt.strftime("2000-01-01 %H:%M:%S"))
expediciones_filtrado2["fin_hora"] = pd.to_datetime(expediciones_filtrado2["fin_expedicion"].dt.strftime("2000-01-01 %H:%M:%S"))
expediciones_filtrado2["fecha"] = expediciones_filtrado2["inicio_expedicion"].dt.strftime("%d-%m-%Y")

jornada = (
    expediciones_filtrado2
    .groupby("fecha")
    .agg(
        inicio_dia=("inicio_expedicion", "min"),
        fin_dia=("fin_expedicion", "max"),
        expedciones=("Expedicion", "sum")
    )
)

jornada["duracion_horas"] = (
    (jornada["fin_dia"] - jornada["inicio_dia"]) 
    .dt.total_seconds() / 3600
) + 0.5 # 0.5 mas 30 minutos de regalo en entrada y salida

expediciones_filtrado2 = expediciones_filtrado2.sort_values(["fecha", "inicio_expedicion"])
expediciones_filtrado2["fin_anterior"] = expediciones_filtrado2.groupby("fecha")["fin_expedicion"].shift(1)

expediciones_filtrado2["tiempo_muerto"] = (
    expediciones_filtrado2["inicio_expedicion"] - expediciones_filtrado2["fin_anterior"]
)
expediciones_filtrado2["tiempo_muerto_min"] = expediciones_filtrado2["tiempo_muerto"].dt.total_seconds() / 60
expediciones_filtrado2["tiempo_muerto_horas"] = expediciones_filtrado2["tiempo_muerto"].dt.total_seconds() / 3600
expediciones_filtrado2["gap_30min"] = expediciones_filtrado2["tiempo_muerto_horas"] >= 0.5


almuerzo_dia = (
    expediciones_filtrado2
    .groupby("fecha")["gap_30min"]
    .any()
    .astype(int)
    .rename("tuvo_almuerzo")
)


tiempos_muertos_dia = (
    expediciones_filtrado2
    .groupby("fecha")["tiempo_muerto"]
    .sum()
    .dt.total_seconds() / 3600
)

jornada["horas_efectivas"] = (
    expediciones_filtrado2.groupby("fecha")["duracion"]
    .sum()
    .dt.total_seconds() / 3600
) + 0.5

jornada["horas_muertas"] = tiempos_muertos_dia 

jornada["eficiencia"] = (
    jornada["horas_efectivas"] / jornada["duracion_horas"]
)

jornada = jornada.join(almuerzo_dia)

jornada["final_efectivas"] = jornada["horas_muertas"] - 0.5*jornada["tuvo_almuerzo"]
jornada["eficiencia_final"] = (
    1 - jornada["final_efectivas"] / jornada["duracion_horas"]
)


expediciones_filtrado2["estado"] = expediciones_filtrado2["es_valida"].map({
    1: "Válida",
    0: "Inválida"
})

fig = px.timeline(
    expediciones_filtrado2,
    x_start="inicio_hora",
    x_end="fin_hora",
    y="fecha",
    color="estado",
    color_discrete_map={
        "Válida": "green",
        "Inválida": "red"
     }   
    # color="chofer"
)

fig.update_yaxes(autorange="reversed")

# 🔥 clave: mostrar solo horas
fig.update_xaxes(
    tickformat="%H:%M",
    title="Hora del día"
)
fig.update_layout(title=chofer_sel, template='ygridoff', height=200 + 30 * expediciones_filtrado2["fecha"].nunique(),
                      legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.1,
            xanchor="center",
            x=0.5
        ))



col7, col8= st.columns([4,1])

with col7:
    st.plotly_chart(fig, width='stretch')


st.dataframe(jornada)



